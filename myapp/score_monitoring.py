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

Usage rapide :

    from myapp.score_monitoring import score_monitor

    score_monitor.record('professionnel', score=85.2, context={'plat_id': 12})
    stats = score_monitor.get_stats('professionnel')
    alerts = score_monitor.get_alerts()
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
    "min_samples_for_stats": 10  # Échantillons minimum pour stats fiables
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


@dataclass
class Alert:
    """Une alerte détectée par le monitor."""
    level: str                            # INFO / WARNING / CRITICAL
    score_type: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    context: Dict[str, Any] = field(default_factory=dict)


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

    # -------------------------------------------------------------------- API
    def record(self, score_type: str, value: float,
               context: Optional[Dict[str, Any]] = None) -> None:
        """Enregistre un score calculé et déclenche les détections d'anomalie."""
        if not isinstance(value, (int, float)) or math.isnan(value):
            self._emit_alert(Alert(
                level=ALERT_CRITICAL,
                score_type=score_type,
                message=f"Score non numérique reçu : {value!r}",
                context=context or {},
            ))
            return

        record = ScoreRecord(
            score_type=score_type,
            value=float(value),
            context=context or {},
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
                self._emit_alert(Alert(
                    level=ALERT_CRITICAL,
                    score_type=score_type,
                    message=(f"Score hors plage [0,100] : {value:.2f}. "
                             f"Validation post-calcul manquante ou bug."),
                    context=context or {},
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
                        self._emit_alert(Alert(
                            level=ALERT_WARNING,
                            score_type=score_type,
                            message=(f"Outlier détecté (z-score={zscore:.2f}) : "
                                     f"valeur={value:.2f}, moyenne={mean:.2f}, "
                                     f"σ={stdev:.2f}"),
                            context=context or {},
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

    # ---------------------------------------------------------------- ALERTS
    def get_alerts(self, level: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            alerts = list(self._alerts)
        if level:
            alerts = [a for a in alerts if a.level == level]
        return [asdict(a) for a in alerts[-limit:]]

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
    def get_recent_records(self, score_type: str,
                           limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            buf = self._records.get(score_type, deque())
            return [asdict(r) for r in list(buf)[-limit:]]

    def reset(self, score_type: Optional[str] = None) -> None:
        with self._lock:
            if score_type:
                self._records.pop(score_type, None)
                self._counters.pop(score_type, None)
            else:
                self._records.clear()
                self._counters.clear()
                self._alerts.clear()

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
    level_map = {
        ALERT_INFO: logging.INFO,
        ALERT_WARNING: logging.WARNING,
        ALERT_CRITICAL: logging.ERROR,
    }
    _logger.log(
        level_map.get(alert.level, logging.INFO),
        "[%s][%s] %s | ctx=%s",
        alert.level, alert.score_type, alert.message, alert.context,
    )


score_monitor.register_alert_callback(_default_log_callback)

