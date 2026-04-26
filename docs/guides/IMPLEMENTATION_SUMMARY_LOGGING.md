# 📋 Résumé: Amélioration des Logs d'Alertes Récentes

## ✅ Modifications complétées

### 1. **score_monitoring.py** - Améliorations principales

#### Structures de données améliorées:
```python
@dataclass
class ScoreRecord:
    client_id: Optional[int] = None       # NEW
    plat_id: Optional[int] = None         # NEW
    menu_id: Optional[int] = None         # NEW

@dataclass
class Alert:
    client_id: Optional[int] = None       # NEW
    plat_id: Optional[int] = None         # NEW
    menu_id: Optional[int] = None         # NEW
```

#### Méthode `record()` améliorée:
```python
def record(self, score_type: str, value: float,
           context: Optional[Dict[str, Any]] = None,
           client_id: Optional[int] = None,        # NEW
           plat_id: Optional[int] = None,          # NEW
           menu_id: Optional[int] = None) -> None: # NEW
```

#### Nouvelles méthodes:
- `get_alerts(level, limit, client_id)` - Filtrage par client_id ajouté
- `get_recent_alerts_by_client(client_id, level, limit)` - Nouvelle méthode
- `get_recent_records(score_type, limit, client_id)` - Filtrage par client_id ajouté

#### Logs améliorés:
```
Avant: [WARNING][professionnel] message | ctx={}
Apres: [WARNING][professionnel] | client_id=42 | plat_id=12 | menu_id=5 | message | ctx={}
```

---

### 2. **views_monitoring.py** - Intégration API

- Ajout du paramètre `client_id` dans `score_dashboard()`
- Support du filtrage `client_id` dans `score_dashboard_api()`
- Amélioration des décorateurs HTTP

**Endpoints disponibles:**
```
GET /api/score-dashboard/?client_id=42
GET /api/score-dashboard/?level=CRITICAL&client_id=42
GET /api/score-dashboard/?type=professionnel&client_id=42
```

---

### 3. **Documentation complète**

Deux fichiers de documentation créés:

1. **IMPROVED_LOGS_MONITORING.md** - Guide complet avec:
   - Vue d'ensemble
   - Guide d'utilisation avec exemples
   - Format des logs avant/après
   - Structure JSON des alertes et enregistrements
   - 4 cas d'usage pratiques
   - Configuration du logging avancée
   - Intégration dans les vues existantes
   - Checklist d'implémentation

2. **test_monitoring_improved.py** - Script de test complet

---

## 🚀 Guide d'intégration rapide

### Cas 1: Enregistrer un score lors du calcul

```python
from myapp.score_monitoring import score_monitor

def compute_nutritional_score(user_id, plat_id=None, menu_id=None):
    user = Utilisateur.objects.get(id=user_id)
    score = calculate_score(user)  # Votre logique
    
    # Enregistrer avec traçabilité
    score_monitor.record(
        score_type='professionnel',
        value=score,
        client_id=user.id,        # Nouveau!
        plat_id=plat_id,          # Nouveau!
        menu_id=menu_id,          # Nouveau!
        context={'email': user.email}
    )
    
    return score
```

### Cas 2: Récupérer les alertes d'un client

```python
from myapp.score_monitoring import score_monitor

# Méthode 1: Utiliser get_alerts avec filtrage
alerts = score_monitor.get_alerts(client_id=42, level='WARNING')

# Méthode 2: Utiliser la méthode dédiée
alerts = score_monitor.get_recent_alerts_by_client(client_id=42)

for alert in alerts:
    print(f"[{alert['level']}] Client {alert['client_id']} | "
          f"Plat {alert.get('plat_id')} | {alert['message']}")
```

### Cas 3: Requête API pour les alertes d'un client

```bash
# Récupérer les alertes du client 42
curl "http://localhost:8000/api/score-dashboard/?client_id=42"

# Alertes critiques seulement
curl "http://localhost:8000/api/score-dashboard/?client_id=42&level=CRITICAL"

# Combiner avec le type de score
curl "http://localhost:8000/api/score-dashboard/?client_id=42&type=professionnel&limit=100"
```

---

## 📊 Exemple de réponse API

```json
{
  "stats": {
    "professionnel": {
      "samples": 150,
      "mean": 72.5,
      "stddev": 8.3,
      "anomalies": 2,
      "outliers": 1,
      "health": "OK"
    }
  },
  "alerts": [
    {
      "level": "WARNING",
      "score_type": "professionnel",
      "message": "Outlier détecté (z-score=3.2) : valeur=95.00",
      "timestamp": "2026-04-19T10:15:30.123456",
      "client_id": 42,
      "plat_id": 12,
      "menu_id": 5,
      "context": {}
    }
  ]
}
```

---

## 🔧 Configuration Logging (Optionnel)

Ajouter dans `settings.py` pour un logging persistant:

```python
LOGGING = {
    "version": 1,
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/score_monitoring.log",
        },
    },
    "loggers": {
        "score_monitor": {
            "handlers": ["file"],
            "level": "DEBUG",
        },
    },
}
```

---

## ✨ Avantages des améliorations

| Avantage | Description |
|----------|-------------|
| **Traçabilité** | Chaque anomalie identifie client/plat/menu |
| **Debugging rapide** | Retrouver toutes les alertes d'un client en 1 requête |
| **Logs clairs** | Format amélioré avec IDs visibles |
| **Backward compatible** | Anciens appels continuent de fonctionner |
| **Thread-safe** | Toutes les opérations protégées |
| **Performances** | Buffers circulaires limitent la mémoire |

---

## 🧪 Tests réussis

```
[OK] Imports reussis
[OK] Score enregistre avec client_id, plat_id, menu_id
[OK] Alertes recuperees
[OK] Alertes filtrees par client_id=42
[OK] Alertes recentes du client 42
[OK] Enregistrements filtres par client_id
[SUCCESS] Tous les tests passent!
```

---

## 📝 Fichiers modifiés

1. ✅ `myapp/score_monitoring.py` - Améliorations principales
2. ✅ `myapp/views_monitoring.py` - Intégration API
3. ✅ `IMPROVED_LOGS_MONITORING.md` - Documentation complète (nouveau)
4. ✅ `test_monitoring_improved.py` - Script de test (nouveau)

---

## 🎯 Prochaines étapes recommandées

### Court terme:
- [ ] Utiliser les nouveaux paramètres dans les vues de calcul de score existantes
- [ ] Tester les nouveaux endpoints API en production
- [ ] Ajouter client_id/plat_id dans tous les appels `score_monitor.record()`

### Moyen terme:
- [ ] Ajouter un dashboard pour visualiser les alertes par client
- [ ] Implémenter des notifications (email/SMS) sur alertes CRITICAL
- [ ] Archiver les alertes anciennes en base de données

### Long terme:
- [ ] Machine learning pour détecter les anomalies automatiques
- [ ] Rapports d'audit automatiques par client
- [ ] Export des alertes en format CSV/Excel

---

## 💬 Questions fréquentes

**Q: Les anciens appels à `record()` vont-ils casser?**  
R: Non! Tous les nouveaux paramètres sont optionnels. La backward compatibility est totale.

**Q: Où sont stockées les alertes?**  
R: En mémoire dans des deques circulaires (maxlen=500). Pour la persistance, voir la section Configuration.

**Q: Combien d'alertes/enregistrements sont conservés?**  
R: 500 alertes totales, 1000 enregistrements par type de score. À configurer via `MAX_RECORDS_PER_TYPE`.

**Q: Les IDs sont-ils obligatoires?**  
R: Non! client_id, plat_id, menu_id sont tous optionnels. Utilisez-les selon vos besoins.

---

## ✅ Checklist finale

- [x] Modifier les structures ScoreRecord et Alert
- [x] Améliorer la signature de record()
- [x] Améliorer le logging avec affichage des IDs
- [x] Ajouter le filtrage par client_id
- [x] Ajouter get_recent_alerts_by_client()
- [x] Mettre à jour get_recent_records()
- [x] Améliorer les vues API
- [x] Créer la documentation complète
- [x] Créer le script de test
- [x] Valider que tout compile et fonctionne
- [x] Résumé de la livraison

**Status: ✅ COMPLET ET TESTÉ**
