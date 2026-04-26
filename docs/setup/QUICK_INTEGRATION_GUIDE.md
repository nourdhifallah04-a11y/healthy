# 🚀 Guide d'intégration rapide - Logs d'Alertes améliorés

## En 3 étapes

### ✅ Étape 1: Identifier où enregistrer les scores

Trouvez les appels actuels à `score_monitor.record()`:

```bash
grep -r "score_monitor.record" --include="*.py"
```

### ✅ Étape 2: Ajouter les IDs

**Avant:**
```python
score_monitor.record('professionnel', score=85.2)
```

**Après:**
```python
score_monitor.record(
    'professionnel', 
    score=85.2,
    client_id=user.id,        # ← Ajouté
    plat_id=plat.id,          # ← Ajouté (optionnel)
    menu_id=menu.id           # ← Ajouté (optionnel)
)
```

### ✅ Étape 3: Tester

Récupérer les alertes:
```python
from myapp.score_monitoring import score_monitor

# Alertes du client
alerts = score_monitor.get_alerts(client_id=42)
print(f"Alertes: {len(alerts)}")
```

---

## 📍 Emplacements probables à modifier

### 1. Vues de calcul de score
**Fichier probable:** `myapp/views.py`, `myapp/api.py`

```python
def calculate_score_view(request):
    user = request.user
    score = calculate_score(user)
    
    # Ajouter IDs ici:
    score_monitor.record(
        'professionnel',
        value=score,
        client_id=user.id,  # ← NOUVEAU
    )
```

### 2. API de recommandations N8N
**Fichier probable:** Fonction qui appelle N8N

```python
def recommend_with_n8n(request):
    user = request.user
    profil = user.client.profil_nutritionnel
    
    score_monitor.record(
        'professionnel',
        value=calculate_recommendations_score(profil),
        client_id=user.id,  # ← NOUVEAU
    )
```

### 3. Vues de commande/ligne de commande
**Fichier probable:** Endpoint de validation de commande

```python
def validate_order_line(request):
    user = request.user
    plat = Plat.objects.get(id=request.data['plat_id'])
    
    # Score adaptée au plat
    score = calculate_plat_score(plat, user)
    
    score_monitor.record(
        'professionnel',
        value=score,
        client_id=user.id,
        plat_id=plat.id,  # ← NOUVEAU
    )
```

---

## 🔍 Recherche multi-fichiers

### Trouver tous les appels à record()
```python
# Dans Django shell
import os
import re

pattern = r'score_monitor\.record\('

for root, dirs, files in os.walk('myapp'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                for i, line in enumerate(f, 1):
                    if 'score_monitor.record' in line:
                        print(f"{filepath}:{i}: {line.strip()}")
```

---

## 📊 Vérification après implémentation

### Vérifier que les IDs sont enregistrés:
```python
from myapp.score_monitoring import score_monitor

# Récupérer une alerte pour voir les IDs
alerts = score_monitor.get_alerts(limit=1)
if alerts:
    alert = alerts[0]
    print(f"Client ID: {alert.get('client_id')}")
    print(f"Plat ID: {alert.get('plat_id')}")
    print(f"Menu ID: {alert.get('menu_id')}")
    print(f"Message: {alert['message']}")
```

### Tester le filtrage:
```python
# Filtrer par client
client_42_alerts = score_monitor.get_alerts(client_id=42)
print(f"Client 42 a {len(client_42_alerts)} alertes")

# Filtrer par niveau
critical = score_monitor.get_alerts(level='CRITICAL')
print(f"Alertes critiques: {len(critical)}")
```

---

## 🎯 Priorité d'implémentation

### 1️⃣ **Priorité haute** (DOIT être fait)
- [ ] Vue de calcul de score principal
- [ ] API de recommandations
- [ ] Validation de commande

### 2️⃣ **Priorité moyenne** (DEVRAIT être fait)
- [ ] Endpoints de profil nutritionnel
- [ ] APIs de menu/plat
- [ ] Calculs IMC

### 3️⃣ **Priorité basse** (PEUT être fait)
- [ ] Autres vues moins critiques
- [ ] Tests unitaires
- [ ] Statistiques de monitoring

---

## 🧪 Test complet (une ligne)

```bash
python manage.py shell -c "
from myapp.score_monitoring import score_monitor
score_monitor.record('professionnel', 85.0, client_id=1, plat_id=2, menu_id=3)
alerts = score_monitor.get_alerts(client_id=1)
print('SUCCESS' if alerts and alerts[0]['client_id'] == 1 else 'FAILED')
"
```

---

## 📚 Références rapides

| Méthode | Usage | Exemple |
|---------|-------|---------|
| `record()` | Enregistrer un score | `record('prof', 85, client_id=42)` |
| `get_alerts()` | Récupérer alertes | `get_alerts(client_id=42, level='CRITICAL')` |
| `get_recent_alerts_by_client()` | Alertes d'un client | `get_recent_alerts_by_client(42)` |
| `get_recent_records()` | Records de score | `get_recent_records('prof', client_id=42)` |

---

## ❓ Aide & Débogage

### "Je ne vois pas les IDs dans les logs"
→ Vérifie que tu passes `client_id`, `plat_id`, `menu_id` à `record()`

### "Les IDs sont None dans l'alerte"
→ Assure-toi que tu les passes : `record(..., client_id=user.id, ...)`

### "Comment récupérer les alertes d'un client spécifique?"
→ Utilise: `score_monitor.get_alerts(client_id=42)`

### "Comment filtrer par niveau ET client?"
→ Utilise: `score_monitor.get_alerts(level='CRITICAL', client_id=42)`

---

## 🎉 Done!

Une fois toutes les modifications faites, vous aurez:

✅ Traçabilité complète de chaque calcul de score  
✅ Logs avec IDs visibles et lisibles  
✅ Filtrage efficace des alertes par client  
✅ Debugging 10x plus rapide  
✅ Audit trail pour conformité  

---

**Temps estimé:** 30-60 minutes pour intégration complète  
**Difficulté:** Facile (copier/coller les paramètres)  
**Impact:** Très haut (debugging massif amélioré)
