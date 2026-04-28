"""
================================================================================
 SCORE MONITORING - Surveillance et statistiques des calculs de scores
================================================================================

Ce module fournit un système léger de monitoring des calculs de score
nutritionnel (simple, IMC, professionnel) avec :

  - Enregistrement de chaque score calculé (en mémoire + persistance optionnelle)
  - Calcul de moyenne, variance, écart-type, min/max par type de score
  - Détection d'anomalies (scores hors plage [0,100], variance excessive,
    valeurs aberrantes via détection Z-score)
  - Système d'alertes configurables (callbacks)
  - Export JSON pour dashboard
  - Traçabilité client_id, plat_id, menu_id dans les logs

Usage rapide :

    from myapp.score_monitoring import score_monitor

    # Enregistrer un score avec traçabilité
    score_monitor.record(
        'professionnel', 
        score=85.2, 
        client_id=42,
        plat_id=12,
        menu_id=5,
        context={'details': 'additional info'}
    )
    
    # Récupérer les alertes récentes d'un client
    alerts = score_monitor.get_alerts(client_id=42, limit=20)
    alerts_by_client = score_monitor.get_recent_alerts_by_client(client_id=42)
    
    # Statistiques
    stats = score_monitor.get_stats('professionnel')
"""

from __future__ import annotations

import json
import math
import statistics
import threading
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Deque, Dict, List, Optional


# ============================================================================
#  CONFIGURATION
# ============================================================================

# Nombre maximum d'enregistrements gardés en mémoire (rolling buffer)
MAX_RECORDS_PER_TYPE = 1000

# Seuils d'alerte par défaut
DEFAULT_THRESHOLDS = {
    "min_score": 0.0,            # Score < 0 → anomalie
    "max_score": 100.0,          # Score > 100 → anomalie
    "max_stddev": 35.0,          # Écart-type trop élevé → recalibration nécessaire
    "min_mean_warn": 25.0,       # Moyenne trop basse → stratégie trop sévère
    "max_mean_warn": 90.0,       # Moyenne trop haute → stratégie trop laxiste
    "outlier_zscore": 3.0,       # |z-score| > 3 → outlier
    "min_samples_for_stats": 10, # Échantillons minimum pour stats fiables
    # NOUVELLES ALERTES
    "anomaly_rate_warn": 0.15,   # Taux d'anomalies > 15% → alerte
    "anomaly_rate_critical": 0.25, # Taux d'anomalies > 25% → critique
    "repeated_anomaly_threshold": 3, # 3+ anomalies consécutives → alerte
    "mean_shift_threshold": 15.0, # Changement moyen > 15 points → alerte
    "identical_scores_threshold": 5, # 5+ scores identiques → suspect
    "anomaly_per_client_warn": 5, # 5+ anomalies par client → alerte
    "anomaly_per_plat_warn": 4,  # 4+ anomalies par plat → alerte
}

# Niveaux d'alerte
ALERT_INFO = "INFO"
ALERT_WARNING = "WARNING"
ALERT_CRITICAL = "CRITICAL"


# ============================================================================
#  STRUCTURES DE DONNÉES
# ============================================================================

@dataclass
class ScoreRecord:
    """Un enregistrement de calcul de score."""
    score_type: str                       # 'simple', 'imc', 'professionnel'
    value: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)
    client_id: Optional[int] = None       # ID du client (Utilisateur)
    plat_id: Optional[int] = None         # ID du plat (si applicable)
    menu_id: Optional[int] = None         # ID du menu (si applicable)


@dataclass
class Alert:
    """Une alerte détectée par le monitor."""
    level: str                            # INFO / WARNING / CRITICAL
    score_type: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)
    client_id: Optional[int] = None       # ID du client pour traçabilité
    plat_id: Optional[int] = None         # ID du plat (si applicable)
    menu_id: Optional[int] = None         # ID du menu (si applicable)


# ============================================================================
#  MONITOR SINGLETON
# ============================================================================

class ScoreMonitor:
    """
    Singleton thread-safe qui agrège les scores calculés et détecte
    les anomalies.
    """

    def __init__(self, max_records: int = MAX_RECORDS_PER_TYPE,
                 thresholds: Optional[Dict[str, float]] = None):
        self._lock = threading.RLock()
        self._records: Dict[str, Deque[ScoreRecord]] = {}
        self._alerts: Deque[Alert] = deque(maxlen=500)
        self._max_records = max_records
        self._thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self._alert_callbacks: List[Callable[[Alert], None]] = []
        # Compteurs cumulatifs (non bornés par buffer rolling)
        self._counters: Dict[str, Dict[str, int]] = {}
        # NOUVEAUX TRACKERS
        self._anomalies_by_client: Dict[int, int] = {}  # Compteur anomalies par client
        self._anomalies_by_plat: Dict[int, int] = {}    # Compteur anomalies par plat
        self._last_score_by_type: Dict[str, float] = {} # Dernier score enregistré par type
        self._consecutive_anomalies: Dict[str, int] = {} # Compteur anomalies consécutives

    # -------- HELPER: Formatter les IDs pour inclusion dans messages --------
    @staticmethod
    def _format_ids(client_id: Optional[int] = None,
                   plat_id: Optional[int] = None,
                   menu_id: Optional[int] = None) -> str:
        """Formate les IDs pour inclusion directe dans les messages d'alerte.
        
        Returns:
            String formaté: "[client_id=X] [plat_id=Y]" ou vide si pas d'IDs
        """
        parts = []
        if client_id is not None:
            parts.append(f"client_id={client_id}")
        if plat_id is not None:
            parts.append(f"plat_id={plat_id}")
        if menu_id is not None:
            parts.append(f"menu_id={menu_id}")
        return " [" + "] [".join(parts) + "]" if parts else ""

    @staticmethod
    def _make_json_safe(obj: Any) -> Any:
        """Convertit un objet en format JSON-safe (primitifs uniquement).
        
        Gère les types primitifs, dict, list, float, int, str, bool, None.
        Les autres objets sont convertis en string.
        """
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj
        elif isinstance(obj, dict):
            return {k: ScoreMonitor._make_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [ScoreMonitor._make_json_safe(item) for item in obj]
        else:
            # Pour tout objet non-primitif, convertir en string
            return str(obj)

    # -------------------------------------------------------------------- API
    def _enrich_context_with_nutritional_data(self, context: Dict[str, Any],
                                              client_id: Optional[int] = None,
                                              plat_id: Optional[int] = None) -> Dict[str, Any]:
        """Enrichit le contexte avec les données nutritionnelles du plat et IMC du client.
        
        Args:
            context: Contexte existant
            client_id: ID du client
            plat_id: ID du plat
            
        Returns:
            Contexte enrichi avec plat (nutritional data) et client (IMC) fields
        """
        enriched = dict(context)  # Copie du contexte existant
        
        # Enrichir avec données du plat si plat_id fourni
        if plat_id is not None:
            try:
                from myapp.plat.models import Plat
                plat = Plat.objects.get(id_plat=plat_id)
                enriched['plat'] = {
                    'id': plat.id_plat,
                    'nom': plat.nom,
                    'calories': float(plat.calorie),
                    'proteines': float(plat.proteine),
                    'glucides': float(plat.glucides),
                    'lipides': float(plat.lipides),
                    'fibres': float(plat.fibres),
                }
            except Exception:
                # Si le plat n'existe pas ou erreur BD, continuer sans données nutritionnelles
                pass
        
        # Enrichir avec IMC du client si client_id fourni
        if client_id is not None:
            try:
                from myapp.users.models import Client, Utilisateur
                user = Utilisateur.objects.get(id=client_id)
                client = user.client
                
                # Calculer IMC si date de naissance existe
                if client.date_naissance:
                    from datetime import date
                    from dateutil.relativedelta import relativedelta
                    age = relativedelta(date.today(), client.date_naissance).years
                    
                    # Récupérer poids/taille depuis ProfilNutritionnel
                    try:
                        from myapp.profilNutritionnel.models import ProfilNutritionnel
                        profile = ProfilNutritionnel.objects.filter(client=client).last()
                        if profile:
                            # Calculer IMC: poids (kg) / (taille (m))^2
                            if profile.taille and profile.poids:
                                taille_m = float(profile.taille) / 100  # Convertir cm en m
                                imc = float(profile.poids) / (taille_m ** 2)
                                enriched['client'] = {
                                    'id': client_id,
                                    'age': age,
                                    'imc': round(imc, 2),
                                }
                    except Exception:
                        enriched['client'] = {'id': client_id, 'age': age}
                else:
                    enriched['client'] = {'id': client_id}
            except Exception:
                # Si le client n'existe pas ou erreur, continuer sans données IMC
                pass
        
        return enriched

    def record(self, score_type: str, value: float,
               context: Optional[Dict[str, Any]] = None,
               client_id: Optional[int] = None,
               plat_id: Optional[int] = None,
               menu_id: Optional[int] = None) -> None:

        """Enregistre un score calculé et déclenche les détections d'anomalie.
        
        Args:
            score_type: Type de score ('simple', 'imc', 'professionnel')
            value: Valeur du score
            context: Contexte additionnel (dict)
            client_id: ID du client (Utilisateur)
            plat_id: ID du plat concerné (optionnel)
            menu_id: ID du menu concerné (optionnel)
        """
        # Enrichir le contexte avec données nutritionnelles
        enriched_context = self._enrich_context_with_nutritional_data(
            context or {}, client_id=client_id, plat_id=plat_id
        )
        
        if not isinstance(value, (int, float)) or math.isnan(value):
            ids_str = self._format_ids(client_id, plat_id, menu_id)
            self._emit_alert(Alert(
                level=ALERT_CRITICAL,
                score_type=score_type,
                message=f"Score non numérique reçu : {value!r}{ids_str}",
                context=enriched_context,
                client_id=client_id,
                plat_id=plat_id,
                menu_id=menu_id,
            ))
            return

        record = ScoreRecord(
            score_type=score_type,
            value=float(value),
            context=enriched_context,
            client_id=client_id,
            plat_id=plat_id,
            menu_id=menu_id,
        )

        with self._lock:
            buf = self._records.setdefault(
                score_type, deque(maxlen=self._max_records)
            )
            buf.append(record)

            counters = self._counters.setdefault(score_type, {
                "total": 0, "anomalies": 0, "outliers": 0
            })
            counters["total"] += 1

            # Détection : score hors plage [0,100]
            if value < self._thresholds["min_score"] or value > self._thresholds["max_score"]:
                counters["anomalies"] += 1
                ids_str = self._format_ids(client_id, plat_id, menu_id)
                self._emit_alert(Alert(
                    level=ALERT_CRITICAL,
                    score_type=score_type,
                    message=(f"[BUG CALCUL] Score INVALIDE {value:.1f} hors [0,100]{ids_str} | "
                             f"Type: {score_type} | Action: Vérifier algo calcul"),
                    context=enriched_context,
                    client_id=client_id,
                    plat_id=plat_id,
                    menu_id=menu_id,
                ))

            # Détection outlier (z-score) si assez d'échantillons
            if len(buf) >= self._thresholds["min_samples_for_stats"]:
                values = [r.value for r in buf]
                mean = statistics.fmean(values)
                stdev = statistics.pstdev(values)
                if stdev > 0:
                    zscore = abs(value - mean) / stdev
                    if zscore > self._thresholds["outlier_zscore"]:
                        counters["outliers"] += 1
                        ids_str = self._format_ids(client_id, plat_id, menu_id)
                        self._emit_alert(Alert(
                            level=ALERT_WARNING,
                            score_type=score_type,
                            message=(f"[VALEUR ABERRANTE] Z-score={zscore:.1f}{ids_str} | "
                                     f"Valeur: {value:.1f} (écart: {zscore*stdev:.1f}) | "
                                     f"Moy: {mean:.1f} | Action: Vérifier donnée"),
                            context=enriched_context,
                            client_id=client_id,
                            plat_id=plat_id,
                            menu_id=menu_id,
                        ))

            # ========== NOUVELLES DÉTECTIONS ==========
            
            # Détection 1: Variance excessive (écart-type trop élevé)
            if len(buf) >= self._thresholds["min_samples_for_stats"]:
                values = [r.value for r in buf]
                stdev = statistics.pstdev(values)
                if stdev > self._thresholds["max_stddev"]:
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_WARNING,
                        score_type=score_type,
                        message=(f"[INSTABILITÉ] Variance trop élevée σ={stdev:.1f}{ids_str} (seuil: {self._thresholds['max_stddev']:.1f}) | "
                                 f"Type: {score_type} | Action: Recalibrer algo"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))

            # Détection 2: Taux d'anomalies élevé
            if counters["total"] >= 20:  # Au moins 20 scores
                anomaly_rate = counters.get("anomalies", 0) / counters["total"]
                if anomaly_rate > self._thresholds["anomaly_rate_critical"]:
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_CRITICAL,
                        score_type=score_type,
                        message=(f"[SYSTÈME KO] Taux anomalies CRITIQUE {anomaly_rate*100:.1f}%{ids_str} "
                                 f"({counters['anomalies']}/{counters['total']}) | "
                                 f"Action: Arrêt + investigation système urgente"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))
                elif anomaly_rate > self._thresholds["anomaly_rate_warn"]:
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_WARNING,
                        score_type=score_type,
                        message=(f"[ANOMALIES ÉLEVÉES] Taux {anomaly_rate*100:.1f}%{ids_str} "
                                 f"({counters['anomalies']}/{counters['total']}) | "
                                 f"Type: {score_type} | Action: Audit paramètres"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))

            # Détection 3: Anomalies récurrentes par client
            if client_id is not None and value < self._thresholds["min_score"] or value > self._thresholds["max_score"]:
                self._anomalies_by_client[client_id] = self._anomalies_by_client.get(client_id, 0) + 1
                if self._anomalies_by_client[client_id] >= self._thresholds["anomaly_per_client_warn"]:
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_WARNING,
                        score_type=score_type,
                        message=(f"[CLIENT PROBLÉMATIQUE] ID {client_id}{ids_str} a "
                                 f"{self._anomalies_by_client[client_id]} anomalies | "
                                 f"Action: Vérifier + nettoyer profil"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))

            # Détection 4: Anomalies récurrentes par plat
            if plat_id is not None and (value < self._thresholds["min_score"] or value > self._thresholds["max_score"]):
                self._anomalies_by_plat[plat_id] = self._anomalies_by_plat.get(plat_id, 0) + 1
                if self._anomalies_by_plat[plat_id] >= self._thresholds["anomaly_per_plat_warn"]:
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_WARNING,
                        score_type=score_type,
                        message=(f"[PLAT SUSPECT] ID {plat_id}{ids_str} cause "
                                 f"{self._anomalies_by_plat[plat_id]} anomalies | "
                                 f"Action: Audit données nutritionnelles"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))

            # Détection 5: Changement drastique du score (variation moyenne)
            if score_type in self._last_score_by_type:
                prev_score = self._last_score_by_type[score_type]
                mean_shift = abs(value - prev_score)
                if mean_shift > self._thresholds["mean_shift_threshold"]:
                    direction = "augmentation" if value > prev_score else "diminution"
                    pct_change = (mean_shift / prev_score * 100) if prev_score != 0 else 0
                    interpretation = "Amélioration" if value > prev_score else "Dégradation"
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    
                    self._emit_alert(Alert(
                        level=ALERT_INFO,
                        score_type=score_type,
                        message=(f"[{interpretation}] Variation importante: {direction} de "
                                 f"{mean_shift:.1f} pts ({pct_change:+.1f}%){ids_str} | "
                                 f"{prev_score:.1f} → {value:.1f}"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))
            self._last_score_by_type[score_type] = value

            # Détection 6: Pattern suspect (scores identiques)
            if len(buf) >= self._thresholds["identical_scores_threshold"]:
                recent_values = [r.value for r in list(buf)[-self._thresholds["identical_scores_threshold"]:]]
                if len(set(recent_values)) == 1:  # Tous les scores sont identiques
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_WARNING,
                        score_type=score_type,
                        message=(f"[DUPLICATION SUSPECT] {len(recent_values)} scores identiques{ids_str} "
                                 f"({value:.1f}) | Type: {score_type} | "
                                 f"Action: Vérifier données source"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))

            # Détection 7: Moyenne extrême (trop haute ou trop basse)
            if len(buf) >= self._thresholds["min_samples_for_stats"]:
                values = [r.value for r in buf]
                mean = statistics.fmean(values)
                if mean < self._thresholds["min_mean_warn"]:
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_WARNING,
                        score_type=score_type,
                        message=(f"[STRATÉGIE TROP SÉVÈRE] Moyenne très basse {mean:.1f}{ids_str} "
                                 f"(seuil: {self._thresholds['min_mean_warn']:.1f}) | "
                                 f"Action: Assouplir critères"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))
                elif mean > self._thresholds["max_mean_warn"]:
                    ids_str = self._format_ids(client_id, plat_id, menu_id)
                    self._emit_alert(Alert(
                        level=ALERT_WARNING,
                        score_type=score_type,
                        message=(f"[STRATÉGIE TROP LAXISTE] Moyenne très haute {mean:.1f}{ids_str} "
                                 f"(seuil: {self._thresholds['max_mean_warn']:.1f}) | "
                                 f"Action: Durcir critères"),
                        context=enriched_context,
                        client_id=client_id,
                        plat_id=plat_id,
                        menu_id=menu_id,
                    ))

    # ---------------------------------------------------------------- STATS
    def get_stats(self, score_type: Optional[str] = None) -> Dict[str, Any]:
        """Renvoie statistiques agrégées (par type ou global)."""
        with self._lock:
            if score_type:
                return self._compute_stats_for(score_type)
            return {st: self._compute_stats_for(st) for st in self._records.keys()}

    def _compute_stats_for(self, score_type: str) -> Dict[str, Any]:
        buf = self._records.get(score_type, deque())
        counters = self._counters.get(score_type, {})
        if not buf:
            return {
                "score_type": score_type,
                "samples": 0,
                "total_recorded": counters.get("total", 0),
                "mean": None, "median": None, "stddev": None,
                "variance": None, "min": None, "max": None,
                "anomalies": counters.get("anomalies", 0),
                "outliers": counters.get("outliers", 0),
                "health": "UNKNOWN",
            }
        values = [r.value for r in buf]
        mean = statistics.fmean(values)
        stdev = statistics.pstdev(values) if len(values) > 1 else 0.0
        variance = stdev ** 2

        # Évaluation santé (heuristique)
        health = self._evaluate_health(mean, stdev, len(values))

        return {
            "score_type": score_type,
            "samples": len(values),
            "total_recorded": counters.get("total", 0),
            "mean": round(mean, 2),
            "median": round(statistics.median(values), 2),
            "stddev": round(stdev, 2),
            "variance": round(variance, 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "anomalies": counters.get("anomalies", 0),
            "outliers": counters.get("outliers", 0),
            "health": health,
            "last_updated": buf[-1].timestamp,
        }

    def _evaluate_health(self, mean: float, stdev: float, samples: int) -> str:
        if samples < self._thresholds["min_samples_for_stats"]:
            return "INSUFFICIENT_DATA"
        if stdev > self._thresholds["max_stddev"]:
            return "CRITICAL"          # Variance très élevée → recalibrer
        if mean < self._thresholds["min_mean_warn"]:
            return "WARNING_LOW_MEAN"  # Stratégie trop sévère
        if mean > self._thresholds["max_mean_warn"]:
            return "WARNING_HIGH_MEAN" # Stratégie trop laxiste
        return "OK"

    # ================================================================ ALERTS
    def _matches_nutritional_filters(self, alert: Alert,
                                     plat_id: Optional[int] = None,
                                     calorie_min: Optional[float] = None,
                                     calorie_max: Optional[float] = None,
                                     proteines_min: Optional[float] = None,
                                     proteines_max: Optional[float] = None,
                                     glucides_min: Optional[float] = None,
                                     glucides_max: Optional[float] = None,
                                     lipides_min: Optional[float] = None,
                                     lipides_max: Optional[float] = None,
                                     fibres_min: Optional[float] = None,
                                     fibres_max: Optional[float] = None,
                                     imc_min: Optional[float] = None,
                                     imc_max: Optional[float] = None) -> bool:
        """Vérifie si une alerte correspond aux filtres nutritionnels (AND logic).
        
        Args:
            alert: Alert object to check
            plat_id: Filter by plat ID
            calorie_min/max, proteines_min/max, etc: Nutritional range filters
            imc_min/max: Client IMC range filters
            
        Returns:
            True if alert matches ALL provided filters, False otherwise
        """
        # Filtre par plat_id
        if plat_id is not None and alert.plat_id != plat_id:
            return False
        
        context = alert.context or {}
        plat_data = context.get('plat', {})
        client_data = context.get('client', {})
        
        # Filtres nutritionnels du plat
        if calorie_min is not None and plat_data.get('calories') is not None:
            if plat_data['calories'] < calorie_min:
                return False
        
        if calorie_max is not None and plat_data.get('calories') is not None:
            if plat_data['calories'] > calorie_max:
                return False
        
        if proteines_min is not None and plat_data.get('proteines') is not None:
            if plat_data['proteines'] < proteines_min:
                return False
        
        if proteines_max is not None and plat_data.get('proteines') is not None:
            if plat_data['proteines'] > proteines_max:
                return False
        
        if glucides_min is not None and plat_data.get('glucides') is not None:
            if plat_data['glucides'] < glucides_min:
                return False
        
        if glucides_max is not None and plat_data.get('glucides') is not None:
            if plat_data['glucides'] > glucides_max:
                return False
        
        if lipides_min is not None and plat_data.get('lipides') is not None:
            if plat_data['lipides'] < lipides_min:
                return False
        
        if lipides_max is not None and plat_data.get('lipides') is not None:
            if plat_data['lipides'] > lipides_max:
                return False
        
        if fibres_min is not None and plat_data.get('fibres') is not None:
            if plat_data['fibres'] < fibres_min:
                return False
        
        if fibres_max is not None and plat_data.get('fibres') is not None:
            if plat_data['fibres'] > fibres_max:
                return False
        
        # Filtres IMC du client
        if imc_min is not None and client_data.get('imc') is not None:
            if client_data['imc'] < imc_min:
                return False
        
        if imc_max is not None and client_data.get('imc') is not None:
            if client_data['imc'] > imc_max:
                return False
        
        return True

    def get_alerts(self, level: Optional[str] = None,
                   limit: int = 100,
                   client_id: Optional[int] = None,
                   plat_id: Optional[int] = None,
                   calorie_min: Optional[float] = None,
                   calorie_max: Optional[float] = None,
                   proteines_min: Optional[float] = None,
                   proteines_max: Optional[float] = None,
                   glucides_min: Optional[float] = None,
                   glucides_max: Optional[float] = None,
                   lipides_min: Optional[float] = None,
                   lipides_max: Optional[float] = None,
                   fibres_min: Optional[float] = None,
                   fibres_max: Optional[float] = None,
                   imc_min: Optional[float] = None,
                   imc_max: Optional[float] = None) -> List[Dict[str, Any]]:
        """Récupère les alertes récentes avec filtrage avancé.
        
        Args:
            level: Filtrer par niveau (INFO, WARNING, CRITICAL)
            limit: Nombre max d'alertes à retourner
            client_id: Filtrer par client_id (optionnel)
            plat_id: Filtrer par plat_id (optionnel)
            calorie_min/max: Plage de calories (optionnel)
            proteines_min/max: Plage de protéines (optionnel)
            glucides_min/max: Plage de glucides (optionnel)
            lipides_min/max: Plage de lipides (optionnel)
            fibres_min/max: Plage de fibres (optionnel)
            imc_min/max: Plage IMC du client (optionnel)
            
        Returns:
            Liste des alertes (les plus récentes en dernier), JSON-safe.
            Filtres combinés avec AND logic.
        """
        with self._lock:
            alerts = list(self._alerts)
        
        # Filtre par niveau
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        # Filtre par client_id
        if client_id is not None:
            alerts = [a for a in alerts if a.client_id == client_id]
        
        # Filtres nutritionnels (AND logic)
        alerts = [a for a in alerts if self._matches_nutritional_filters(
            a,
            plat_id=plat_id,
            calorie_min=calorie_min,
            calorie_max=calorie_max,
            proteines_min=proteines_min,
            proteines_max=proteines_max,
            glucides_min=glucides_min,
            glucides_max=glucides_max,
            lipides_min=lipides_min,
            lipides_max=lipides_max,
            fibres_min=fibres_min,
            fibres_max=fibres_max,
            imc_min=imc_min,
            imc_max=imc_max,
        )]
        
        # Convertir en dictionnaires avec contexte JSON-safe
        result = []
        for a in alerts[-limit:]:
            alert_dict = asdict(a)
            # S'assurer que le contexte est JSON-safe
            alert_dict['context'] = self._make_json_safe(alert_dict.get('context', {}))
            result.append(alert_dict)
        
        return result

    def register_alert_callback(self, fn: Callable[[Alert], None]) -> None:
        """Enregistre un callback appelé à chaque alerte (ex : notif, log)."""
        self._alert_callbacks.append(fn)

    def _emit_alert(self, alert: Alert) -> None:
        self._alerts.append(alert)
        for cb in self._alert_callbacks:
            try:
                cb(alert)
            except Exception:
                pass  # Ne jamais casser le calcul de score à cause d'un callback

    # ---------------------------------------------------------------- UTILS
    def get_recent_alerts_by_client(self, client_id: int,
                                    level: Optional[str] = None,
                                    limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les alertes récentes d'un client spécifique.
        
        Args:
            client_id: ID du client
            level: Filtrer par niveau (optionnel)
            limit: Nombre max d'alertes
            
        Returns:
            Liste des alertes du client (les plus récentes en dernier)
        """
        return self.get_alerts(level=level, limit=limit, client_id=client_id)

    def get_recent_records(self, score_type: str,
                           limit: int = 50,
                           client_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Récupère les enregistrements de score récents (optionnellement filtrés par client).
        
        Args:
            score_type: Type de score
            limit: Nombre max d'enregistrements
            client_id: Filtrer par client_id (optionnel)
            
        Returns:
            Liste des enregistrements (les plus récents en dernier)
        """
        with self._lock:
            buf = self._records.get(score_type, deque())
            records = [asdict(r) for r in list(buf)[-limit:]]
        
        if client_id is not None:
            records = [r for r in records if r.get('client_id') == client_id]
        
        return records

    # ===== NOUVELLES MÉTHODES DE FILTRAGE =====
    
    def get_alerts_by_plat(self, plat_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les alertes liées à un plat spécifique."""
        with self._lock:
            alerts = [a for a in self._alerts if a.plat_id == plat_id]
        
        result = []
        for a in alerts[-limit:]:
            alert_dict = asdict(a)
            alert_dict['context'] = self._make_json_safe(alert_dict.get('context', {}))
            result.append(alert_dict)
        return result
    
    def get_alerts_by_type_message(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les alertes contenant un mot-clé spécifique."""
        with self._lock:
            alerts = [a for a in self._alerts if keyword.lower() in a.message.lower()]
        
        result = []
        for a in alerts[-limit:]:
            alert_dict = asdict(a)
            alert_dict['context'] = self._make_json_safe(alert_dict.get('context', {}))
            result.append(alert_dict)
        return result
    
    def get_anomalies_summary(self) -> Dict[str, Any]:
        """Résumé des anomalies détectées."""
        with self._lock:
            return {
                "total_anomalies_by_client": dict(self._anomalies_by_client),
                "total_anomalies_by_plat": dict(self._anomalies_by_plat),
                "critical_clients": [c for c, count in self._anomalies_by_client.items() 
                                    if count >= self._thresholds["anomaly_per_client_warn"]],
                "problematic_plats": [p for p, count in self._anomalies_by_plat.items()
                                     if count >= self._thresholds["anomaly_per_plat_warn"]],
            }
    
    def get_alerts_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Groupe les alertes par catégorie."""
        with self._lock:
            alerts_list = list(self._alerts)
        
        categories = {
            "out_of_range": [],          # Scores hors plage
            "outliers": [],              # Outliers Z-score
            "high_variance": [],         # Variance excessive
            "anomaly_rate": [],          # Taux d'anomalies élevé
            "client_issues": [],         # Problèmes client
            "plat_issues": [],           # Problèmes plat
            "mean_shift": [],            # Variation importante
            "pattern_suspect": [],       # Pattern suspect
            "mean_extremes": [],         # Moyenne extrême
            "other": [],                 # Autres
        }
        
        for alert in alerts_list:
            alert_dict = asdict(alert)
            alert_dict['context'] = self._make_json_safe(alert_dict.get('context', {}))
            msg = alert.message.lower()
            if "hors plage" in msg:
                categories["out_of_range"].append(alert_dict)
            elif "outlier" in msg and "z-score" in msg:
                categories["outliers"].append(alert_dict)
            elif "variance excessive" in msg:
                categories["high_variance"].append(alert_dict)
            elif "taux d'anomalies" in msg:
                categories["anomaly_rate"].append(alert_dict)
            elif "client" in msg and "anomalies" in msg:
                categories["client_issues"].append(alert_dict)
            elif "plat" in msg and "anomalies" in msg:
                categories["plat_issues"].append(alert_dict)
            elif "variation importante" in msg:
                categories["mean_shift"].append(alert_dict)
            elif "pattern suspect" in msg or "scores identiques" in msg:
                categories["pattern_suspect"].append(alert_dict)
            elif "moyenne" in msg and ("trop" in msg):
                categories["mean_extremes"].append(alert_dict)
            else:
                categories["other"].append(alert_dict)
        
        return {k: v for k, v in categories.items() if v}  # Retourner seulement les catégories non-vides
    
    def reset(self, score_type: Optional[str] = None) -> None:
        """Réinitialise les compteurs et trackers.
        
        Args:
            score_type: Type de score à réinitialiser (optionnel, tout sinon)
        """
        with self._lock:
            if score_type:
                self._records.pop(score_type, None)
                self._counters.pop(score_type, None)
            else:
                self._records.clear()
                self._counters.clear()
                self._alerts.clear()
                # Nettoyer les trackers
                self._anomalies_by_client.clear()
                self._anomalies_by_plat.clear()
                self._last_score_by_type.clear()
                self._consecutive_anomalies.clear()

    def to_json(self) -> str:
        return json.dumps({
            "stats": self.get_stats(),
            "alerts": self.get_alerts(limit=50),
            "thresholds": self._thresholds,
        }, indent=2, default=str)


# ============================================================================
#  INSTANCE GLOBALE
# ============================================================================

# Singleton partagé pour toute l'application
score_monitor = ScoreMonitor()


# Callback par défaut : log via logging Python
import logging
_logger = logging.getLogger("score_monitor")


def _default_log_callback(alert: Alert) -> None:
    """Callback de logging amélioré avec affichage des IDs."""
    level_map = {
        ALERT_INFO: logging.INFO,
        ALERT_WARNING: logging.WARNING,
        ALERT_CRITICAL: logging.ERROR,
    }
    
    # Construction du prefix avec IDs si disponibles
    ids_parts = []
    if alert.client_id is not None:
        ids_parts.append(f"client_id={alert.client_id}")
    if alert.plat_id is not None:
        ids_parts.append(f"plat_id={alert.plat_id}")
    if alert.menu_id is not None:
        ids_parts.append(f"menu_id={alert.menu_id}")
    
    ids_prefix = " | " + " | ".join(ids_parts) if ids_parts else ""
    
    log_msg = (
        f"[{alert.level}][{alert.score_type}]{ids_prefix} | {alert.message} | ctx={alert.context}"
    )
    
    _logger.log(level_map.get(alert.level, logging.INFO), log_msg)


score_monitor.register_alert_callback(_default_log_callback)

