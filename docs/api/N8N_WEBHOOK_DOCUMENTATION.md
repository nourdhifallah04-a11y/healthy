# Endpoint Webhook N8N - Recommandations Nutritionnelles

## Vue d'ensemble

Cet endpoint permet d'appeler un workflow N8N pour obtenir des recommandations nutritionnelles personnalisées basées sur le profil d'un utilisateur.

**URL de l'endpoint:** `POST /profilNutritionnel/api/profil-nutritionnel/recommander-n8n/`

**Webhook N8N:** `http://localhost:5678/webhook/reco-nutrition`

## Authentification

L'endpoint nécessite une authentification (token JWT ou session Django). L'utilisateur doit être connecté.

## Requête

### Exemple minimal (utilise le profil de l'utilisateur courant)

```bash
curl -X POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Exemple avec profil_id spécifique

```bash
curl -X POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profil_id": 1}'
```

### Requête Python

```python
import requests
import json

# Configuration
ENDPOINT_URL = "http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/"
TOKEN = "votre_token_jwt"

# Headers avec authentification
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Payload (optionnel)
payload = {
    "profil_id": 1  # Optionnel, utilise le profil courant si absent
}

# Effectuer la requête
response = requests.post(ENDPOINT_URL, json=payload, headers=headers)

# Afficher la réponse
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
```

## Réponse

### Réponse réussie (200 OK)

```json
{
  "success": true,
  "message": "Recommandations obtenues avec succès",
  "profil": {
    "age": 28,
    "poids": 75.0,
    "taille": 175.0,
    "sexe": "homme",
    "objectif": "prise_muscle",
    "allergies": "",
    "restrictions_alimentaires": "",
    "niveau_activite": "modere",
    "imc": 24.49,
    "bmr": 1755.5,
    "calories_cibles": 2437.7,
    "categorie_imc": "normal"
  },
  "recommendations": {
    "plats": [
      {
        "id": 1,
        "score": 92.5,
        "justification": "Excellente source de protéines (45g), calories modérées, parfait pour prise de muscle"
      }
    ],
    "menus": [
      {
        "id": 1,
        "score": 88.3,
        "justification": "Menu équilibré avec bon ratio macronutriments"
      }
    ]
  }
}
```

### Réponse erreur (4xx/5xx)

```json
{
  "success": false,
  "error": "Profil nutritionnel non trouvé pour cet utilisateur"
}
```

## Payload envoyé à N8N

L'endpoint prépare automatiquement un payload JSON contenant :

```json
{
  "profil": {
    "age": 28,
    "poids": 75.0,
    "taille": 175.0,
    "sexe": "homme",
    "objectif": "prise_muscle",
    "allergies": "",
    "restrictions_alimentaires": "",
    "niveau_activite": "modere",
    "imc": 24.49,
    "bmr": 1755.5,
    "calories_cibles": 2437.7,
    "categorie_imc": "normal"
  },
  "plats_filtrés": [
    {
      "id": 1,
      "nom": "Poulet rôti",
      "description": "Poulet fermier rôti avec légumes",
      "calories": 450.0,
      "proteines": 45.0,
      "glucides": 20.0,
      "lipides": 15.0,
      "fibres": 5.0,
      "prix": 12.99
    }
  ],
  "menus_filtrés": [
    {
      "id": 1,
      "nom": "Menu Protéiné",
      "description": "Menu spécial pour gain musculaire",
      "calories": 1200.0,
      "proteines": 130.0,
      "glucides": 80.0,
      "lipides": 30.0,
      "prix": 25.99
    }
  ]
}
```

## Codes de statut HTTP

| Code | Description |
|------|-------------|
| 200  | Succès - Recommandations obtenues |
| 400  | Erreur du webhook N8N ou données invalides |
| 401  | Non authentifié |
| 403  | Non autorisé |
| 404  | Profil nutritionnel non trouvé |
| 503  | Service N8N indisponible |
| 504  | Timeout du webhook N8N |
| 500  | Erreur interne du serveur |

## Gestion des erreurs

L'endpoint gère les erreurs suivantes :

1. **Profil non trouvé** - Retourne 404 si le profil n'existe pas
2. **Connexion N8N échouée** - Retourne 503 si le webhook N8N n'est pas accessible
3. **Timeout N8N** - Retourne 504 si N8N met trop de temps à répondre (30s max)
4. **Erreur JSON N8N** - Capture la réponse brute si N8N ne retourne pas du JSON valide

Tous les événements sont loggés pour le débogage.

## Configuration

### N8N Webhook

Assurez-vous que le webhook N8N est configuré et accessible à l'URL :
```
http://localhost:5678/webhook/reco-nutrition
```

### Logs

Les logs sont écrits avec le logger `myapp.views`. Configurez-les dans Django settings :

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'myapp.views': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## Exemple d'intégration frontend

```javascript
// JavaScript - Fetch API
const recommendN8n = async () => {
  const token = localStorage.getItem('authToken');
  
  const response = await fetch('/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  });
  
  const data = await response.json();
  
  if (data.success) {
    console.log('Profil:', data.profil);
    console.log('Recommandations:', data.recommendations);
  } else {
    console.error('Erreur:', data.error);
  }
};
```

## Tests

### Test avec curl (avec authentification token)

```bash
# 1. Récupérer un token
TOKEN=$(curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  | jq -r '.token')

# 2. Appeler l'endpoint
curl -X POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq
```

### Test avec Django Shell

```python
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import json

User = get_user_model()
client = APIClient()

# Authentifier
user = User.objects.first()
client.force_authenticate(user=user)

# Appeler l'endpoint
response = client.post('/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/', {})
print(json.dumps(response.json(), indent=2))
```

## Dépannage

### Erreur: "Impossible de se connecter au webhook n8n"
- Vérifiez que N8N est démarré
- Vérifiez l'URL du webhook: `http://localhost:5678/webhook/reco-nutrition`
- Vérifiez la configuration réseau (ports, firewall)

### Erreur: "Timeout du webhook n8n"
- Vérifiez que le workflow N8N répond correctement
- Augmentez le timeout (actuellement 30s) dans le code
- Vérifiez les logs N8N

### Le profil n'est pas trouvé
- Assurez-vous que l'utilisateur a créé un profil nutritionnel
- Testez avec `/profilNutritionnel/api/profil-nutritionnel/obtenir/` d'abord

## Logs et monitoring

L'endpoint enregistre les informations suivantes :

```
INFO: Appel du webhook n8n: http://localhost:5678/webhook/reco-nutrition
INFO: Payload: {...}
INFO: Réponse n8n (status 200): {...}
ERROR: Erreur de connexion au webhook n8n: Connection refused
ERROR: Timeout du webhook n8n: [Errno 110] Connection timed out
```

## API Response Format

La réponse N8N peut avoir différents formats selon votre configuration. L'endpoint retourne la réponse complète dans le champ `recommendations`.

Exemple de structure attendue:
```json
{
  "profil": {...},
  "recommandations": {
    "plats": [
      {"id": 1, "score": 92.5, "justification": "..."}
    ],
    "menus": [
      {"id": 1, "score": 88.3, "justification": "..."}
    ]
  }
}
```

---

Pour plus d'informations sur la configuration N8N, consultez: https://docs.n8n.io/
