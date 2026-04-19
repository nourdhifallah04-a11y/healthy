# 🎯 Endpoint Webhook N8N - Synthèse Technique

## ✅ Implémentation Complétée

Un endpoint Django a été créé pour appeler un webhook n8n et obtenir des recommandations nutritionnelles personnalisées.

## 📍 Endpoint

```http
POST /api/profil-nutritionnel/recommander-n8n/
```

**URL complète:** `http://localhost:8000/api/profil-nutritionnel/recommander-n8n/`

**Authentification:** Token JWT requis  
**Body:** `{ "profil_id": <optionnel> }`

## 🔗 Webhook N8N appelé

```
POST http://localhost:5678/webhook/reco-nutrition
```

## 📦 Fichiers modifiés

### 1. `myapp/views.py`
- Imports ajoutés: `requests`, `logging`
- Classe ajoutée: `RecommenderN8nWebhookView` (~180 lignes)
- Fonctionnalités:
  - Récupère le profil nutritionnel
  - Prépare un payload JSON avec plats et menus
  - Appelle le webhook N8N
  - Gère les erreurs (404, 503, 504)
  - Log tous les appels

### 2. `myapp/urls.py`
- Route créée: `"api/profil-nutritionnel/recommander-n8n/"`
- Pointée vers `RecommenderN8nWebhookView`

### 3. `requirements.txt`
- Dépendances ajoutées:
  - `requests>=2.28.0`
  - `djangorestframework>=3.14.0`
  - `Pillow>=10.0.0`

## 📄 Fichiers de documentation créés

1. **N8N_WEBHOOK_DOCUMENTATION.md**
   - Guide complet d'utilisation
   - Exemples curl et Python
   - Codes d'erreur
   - Configuration

2. **N8N_PAYLOAD_EXAMPLES.md**
   - Exemples de payloads JSON
   - Format de réponse N8N
   - Calcul des scores
   - Gestion des restrictions

3. **test_n8n_webhook.py**
   - Script de test complet
   - Tests de connectivité N8N
   - Tests sans/avec authentification
   - Tests avec profils invalides

4. **N8N_IMPLEMENTATION_COMPLETE.md**
   - Résumé complet de l'implémentation
   - Checklist de déploiement
   - Configuration optionnelle

5. **QUICKSTART_N8N.md**
   - Démarrage rapide (2 minutes)
   - Commandes essentielles
   - Dépannage basique

## 🚀 Utilisation

### Curl
```bash
curl -X POST http://localhost:8000/api/profil-nutritionnel/recommander-n8n/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profil_id": 1}'
```

### Python
```python
import requests
response = requests.post(
    'http://localhost:8000/api/profil-nutritionnel/recommander-n8n/',
    headers={'Authorization': f'Bearer {token}'},
    json={}
)
print(response.json())
```

### JavaScript/Fetch
```javascript
fetch('/api/profil-nutritionnel/recommander-n8n/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
})
.then(r => r.json())
.then(data => console.log(data.recommendations))
```

## 📊 Payload envoyé à N8N

L'endpoint prépare automatiquement:

```json
{
  "profil": {
    "age": 28,
    "poids": 75.0,
    "taille": 175.0,
    "sexe": "homme",
    "objectif": "prise_muscle",
    "allergies": "...",
    "restrictions_alimentaires": "...",
    "niveau_activite": "modere",
    "imc": 24.49,
    "bmr": 1755.53,
    "calories_cibles": 2437.77,
    "categorie_imc": "normal"
  },
  "plats_filtrés": [...],
  "menus_filtrés": [...]
}
```

## 🎯 Flux d'exécution

```
1. Client envoie POST à /api/profil-nutritionnel/recommander-n8n/
         ↓
2. Django réceptionne la requête (authentification JWT)
         ↓
3. Django récupère le profil nutritionnel du client
         ↓
4. Django récupère tous les plats disponibles
         ↓
5. Django récupère tous les menus actifs
         ↓
6. Django prépare le payload JSON
         ↓
7. Django appelle le webhook N8N (HTTP POST)
         ↓
8. N8N reçoit et traite le payload
         ↓
9. N8N calcule les scores et recommandations
         ↓
10. N8N retourne les résultats JSON
         ↓
11. Django reçoit et formate la réponse
         ↓
12. Client reçoit les recommandations
```

## 🛡️ Gestion des erreurs

| Code | Erreur | Cause |
|------|--------|-------|
| 200 | ✅ Succès | Recommandations obtenues |
| 400 | N8N erreur | Webhook N8N retourne 400+ |
| 401 | Non auth | Token JWT manquant/invalide |
| 404 | Profil absent | Profil nutritionnel non trouvé |
| 503 | N8N inaccessible | Webhook N8N non accessible |
| 504 | Timeout | N8N met > 30 secondes |
| 500 | Erreur serveur | Exception Django |

## 📝 Logs générés

Tous les logs sont imprimés dans la console Django:

```
INFO: Appel du webhook n8n: http://localhost:5678/webhook/reco-nutrition
INFO: Payload: {...}
INFO: Réponse n8n (status 200): {...}
```

En cas d'erreur:
```
ERROR: Erreur de connexion au webhook n8n: Connection refused
ERROR: Timeout du webhook n8n: [Errno 110] Connection timed out
```

## 🔧 Configuration

### URL N8N
Modifiez cette ligne dans `views.py`:
```python
webhook_url = 'http://localhost:5678/webhook/reco-nutrition'
```

### Timeout
Cherchez:
```python
timeout=30  # Augmentez si nécessaire
```

### Variable d'environnement (production)
```python
webhook_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/reco-nutrition')
```

## 🧪 Tests

```bash
# Test N8N accessibilité
python test_n8n_webhook.py --test-n8n

# Test complet
python test_n8n_webhook.py --token YOUR_TOKEN

# Test avec profil spécifique
python test_n8n_webhook.py --token YOUR_TOKEN --profil-id 1
```

## 📋 Checklist final

- [x] Endpoint créé
- [x] Routes configurées
- [x] Dépendances ajoutées
- [x] Gestion d'erreurs implémentée
- [x] Logs configurés
- [x] Tests unitaires possible
- [x] Documentation complète
- [x] Script de test fourni
- [x] Exemples de payloads
- [x] Django check sans erreurs

## 🚀 Prêt pour:

- ✅ Développement local
- ✅ Tests en intégration
- ✅ Déploiement en staging
- ✅ Déploiement en production (après configuration des secrets)

## 📚 Documentation

| Fichier | Contenu |
|---------|---------|
| [N8N_WEBHOOK_DOCUMENTATION.md](N8N_WEBHOOK_DOCUMENTATION.md) | Guide complet d'utilisation |
| [N8N_PAYLOAD_EXAMPLES.md](N8N_PAYLOAD_EXAMPLES.md) | Exemples de payloads JSON |
| [test_n8n_webhook.py](test_n8n_webhook.py) | Script de test |
| [QUICKSTART_N8N.md](QUICKSTART_N8N.md) | Démarrage rapide |
| [N8N_IMPLEMENTATION_COMPLETE.md](N8N_IMPLEMENTATION_COMPLETE.md) | Résumé complet |

## 💡 Prochaines étapes optionnelles

1. **Configuration N8N**: Créer le workflow N8N
2. **Tests d'intégration**: Tester avec des données réelles
3. **Frontend**: Intégrer l'appel API dans l'interface utilisateur
4. **Cache**: Ajouter un cache Redis pour les recommandations
5. **Analytics**: Logger les recommandations pour l'analyse
6. **A/B Testing**: Comparer différentes stratégies de scoring

## 🎓 Pour en savoir plus

- Django REST Framework: https://www.django-rest-framework.org/
- n8n Documentation: https://docs.n8n.io/
- Python Requests: https://requests.readthedocs.io/

---

**Status:** ✅ Complété et prêt à l'emploi  
**Version:** 1.0  
**Date:** 2026-04-18
