# Amélioration des Logs d'Alertes Récentes

## 📋 Vue d'ensemble

Le système de monitoring des scores a été amélioré pour inclure la traçabilité complète des entités concernées:
- **client_id**: ID de l'utilisateur/client
- **plat_id**: ID du plat (optionnel)
- **menu_id**: ID du menu (optionnel)

Cela permet un diagnostique et un debugging bien plus efficace des anomalies de calcul de score.

---

## 🔧 Utilisation

### 1. Enregistrement d'un score avec traçabilité

```python
from myapp.score_monitoring import score_monitor

# Enregistrer un score simple avec traçabilité complète
score_monitor.record(
    score_type='professionnel',
    value=85.2,
    client_id=42,           # ID du client (Utilisateur)
    plat_id=12,             # ID du plat (optionnel)
    menu_id=5,              # ID du menu (optionnel)
    context={'details': 'information additionnelle'}
)

# Enregistrement minimal (compatible avec l'ancienne API)
score_monitor.record('simple', value=78.5)

# Avec juste le client
score_monitor.record('imc', value=24.5, client_id=42)
```

### 2. Récupération des alertes récentes

#### Toutes les alertes
```python
alerts = score_monitor.get_alerts(limit=50)
```

#### Alertes d'un client spécifique
```python
# Méthode 1: Utiliser le paramètre client_id dans get_alerts
alerts = score_monitor.get_alerts(client_id=42, limit=50)

# Méthode 2: Utiliser la méthode dédiée
alerts = score_monitor.get_recent_alerts_by_client(client_id=42, limit=50)
```

#### Alertes filtrées par niveau
```python
# Alertes critiques d'un client
critical_alerts = score_monitor.get_alerts(
    level='CRITICAL', 
    client_id=42, 
    limit=50
)

# Niveaux disponibles: 'INFO', 'WARNING', 'CRITICAL'
```

### 3. Récupération des enregistrements de score

```python
# Tous les enregistrements d'un type de score
records = score_monitor.get_recent_records('professionnel', limit=50)

# Enregistrements d'un client spécifique
client_records = score_monitor.get_recent_records(
    'professionnel', 
    limit=50, 
    client_id=42
)
```

---

## 📊 Format des Logs

### Exemple de log avec traçabilité

**Avant:**
```
[WARNING][professionnel] Outlier détecté (z-score=3.5) : valeur=95.00, moyenne=65.00, σ=8.57 | ctx={}
```

**Après:**
```
[WARNING][professionnel] | client_id=42 | plat_id=12 | menu_id=5 | Outlier détecté (z-score=3.5) : valeur=95.00, moyenne=65.00, σ=8.57 | ctx={}
```

### Structure d'une Alerte (JSON)

```json
{
  "level": "WARNING",
  "score_type": "professionnel",
  "message": "Outlier détecté (z-score=3.5) : valeur=95.00, moyenne=65.00, σ=8.57",
  "timestamp": "2026-04-19T10:15:30.123456",
  "context": {},
  "client_id": 42,
  "plat_id": 12,
  "menu_id": 5
}
```

### Structure d'un Enregistrement de Score (JSON)

```json
{
  "score_type": "professionnel",
  "value": 85.2,
  "timestamp": "2026-04-19T10:15:30.123456",
  "context": {"details": "additional info"},
  "client_id": 42,
  "plat_id": 12,
  "menu_id": 5
}
```

---

## 🌐 API Dashboard

### Endpoint: `/api/score-dashboard/`

**Paramètres GET:**
- `type`: Type de score (simple, imc, professionnel) - optionnel
- `level`: Niveau d'alerte (INFO, WARNING, CRITICAL) - optionnel
- `client_id`: ID du client pour filtrer - optionnel
- `limit`: Nombre max d'alertes (défaut: 50)

**Exemples:**

```bash
# Toutes les alertes récentes
curl "http://localhost:8000/api/score-dashboard/"

# Alertes d'un client spécifique
curl "http://localhost:8000/api/score-dashboard/?client_id=42"

# Alertes critiques d'un client
curl "http://localhost:8000/api/score-dashboard/?client_id=42&level=CRITICAL"

# Alertes d'un type de score spécifique
curl "http://localhost:8000/api/score-dashboard/?type=professionnel&limit=100"

# Combinaison: Client + Niveau + Type
curl "http://localhost:8000/api/score-dashboard/?client_id=42&level=WARNING&type=professionnel"
```

**Réponse:**

```json
{
  "stats": {...},
  "alerts": [
    {
      "level": "WARNING",
      "score_type": "professionnel",
      "message": "...",
      "timestamp": "2026-04-19T10:15:30.123456",
      "context": {},
      "client_id": 42,
      "plat_id": 12,
      "menu_id": 5
    }
  ],
  "recent": [...]
}
```

---

## 💡 Cas d'usage pratiques

### 1. Auditer les calculs de score d'un client

```python
# Vérifier si un client a des alertes
client_id = 42
alerts = score_monitor.get_recent_alerts_by_client(client_id=client_id)

print(f"Client {client_id} a {len(alerts)} alertes récentes")
for alert in alerts:
    print(f"  [{alert['level']}] {alert['message']}")
```

### 2. Analyser les problèmes d'un plat

```python
# Trouver toutes les alertes liées à un plat
all_alerts = score_monitor.get_alerts(limit=1000)
plat_alerts = [a for a in all_alerts if a.get('plat_id') == 12]

print(f"Plat 12 a provoqué {len(plat_alerts)} alertes")
```

### 3. Surveiller les anomalies critiques

```python
# Alertes critiques récentes
critical = score_monitor.get_alerts(level='CRITICAL', limit=20)

for alert in critical:
    client_id = alert.get('client_id', 'unknown')
    plat_id = alert.get('plat_id', 'N/A')
    print(f"ALERTE CRITIQUE - Client: {client_id}, Plat: {plat_id}")
    print(f"  Message: {alert['message']}")
    print(f"  Heure: {alert['timestamp']}")
```

### 4. Générer un rapport par client

```python
from myapp.models import Utilisateur

for user in Utilisateur.objects.all()[:10]:
    alerts = score_monitor.get_recent_alerts_by_client(user.id)
    if alerts:
        print(f"\n=== Rapport pour {user.nom} (ID: {user.id}) ===")
        for alert in alerts[-5:]:  # Les 5 dernières alertes
            print(f"  [{alert['level']}] {alert['message']}")
```

---

## 🔍 Configuration du Logging

Le système utilise le logger Python standard `score_monitor`. Vous pouvez configurer le niveau de détail dans `settings.py`:

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/score_monitoring.log",
            "formatter": "verbose",
        },
    },
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} - {message}",
            "style": "{",
        },
    },
    "loggers": {
        "score_monitor": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
```

---

## 🚀 Intégration dans les vues existantes

### Exemple: Vue de calcul de score

```python
from myapp.score_monitoring import score_monitor
from myapp.models import Utilisateur, Plat, Menu

def calculate_score_with_monitoring(user_id, plat_id=None, menu_id=None):
    """Calcule un score avec monitoring et traçabilité."""
    user = Utilisateur.objects.get(id=user_id)
    
    # ... logique de calcul de score ...
    score = compute_score(user)
    
    # Enregistrer avec traçabilité
    score_monitor.record(
        score_type='professionnel',
        value=score,
        client_id=user.id,
        plat_id=plat_id,
        menu_id=menu_id,
        context={
            'username': user.nom,
            'email': user.email,
        }
    )
    
    return score
```

---

## 📝 Notes importantes

1. **Backward Compatibility**: Les anciens appels à `score_monitor.record()` sans les nouveaux paramètres continuent de fonctionner.

2. **Tous les paramètres sont optionnels**: Vous pouvez enregistrer un score avec juste `client_id`, ou avec tous les IDs, selon votre besoin.

3. **Performance**: Le système utilise des buffers circulaires (deque) avec `maxlen=500` pour les alertes et `maxlen=1000` par type de score. Cela garantit une utilisation mémoire constante.

4. **Thread-safe**: Toutes les opérations sont protégées par un `RLock` pour éviter les conditions de course en multithreading.

5. **Filtrage flexible**: Vous pouvez filtrer les alertes par niveau ET client_id simultanément.

---

## ✅ Checklist d'implémentation

- [x] Améliorer les structures de données ScoreRecord et Alert
- [x] Ajouter les paramètres client_id, plat_id, menu_id à la méthode record()
- [x] Améliorer le callback de logging pour afficher les IDs
- [x] Ajouter le filtrage par client_id dans get_alerts()
- [x] Ajouter la méthode get_recent_alerts_by_client()
- [x] Améliorer la méthode get_recent_records() avec filtrage client
- [x] Mettre à jour les vues pour supporter les nouveaux paramètres
- [x] Documenter les cas d'usage et l'API complète
