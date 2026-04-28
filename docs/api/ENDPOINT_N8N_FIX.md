# Fix du Endpoint N8N - Diagnostic 400 Bad Request

## 🔴 Problème Original
- **Erreur**: `POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/ 400 (Bad Request)`
- **Cause**: Plusieurs problèmes identifiés et corrigés

## ✅ Corrections Appliquées

### 1. **Erreur 500 - RawPostDataException (CRITICAL)**
**Problème**: 
```python
logger.info(f"Request body: {request.body}")  # ❌ Erreur après accès à request.data
```

Django REST Framework consomme le stream de données lors de l'accès à `request.data`, rendant `request.body` inaccessible.

**Solution**:
```python
logger.info(f"Request data: {request.data}")  # ✅ Correct
```

### 2. **Optimisation du Payload** 
**Avant**: Payload contenait les tableaux `plats_filtrés` et `menus_filtrés` (~28 lignes)
```python
payload = {
    'profil': {...},
    'plats_filtrés': [...],      # ❌ Données volumineuses inutiles
    'menus_filtrés': [...]       # ❌ Données volumineuses inutiles
}
```

**Après**: Payload simplifié avec données du profil uniquement
```python
payload = {
    'profil': {
        'age': profil.age,
        'poids': profil.poids,
        'taille': profil.taille,
        'sexe': profil.sexe,
        'objectif': profil.objectif,
        'allergies': profil.allergies,
        'restrictions_alimentaires': profil.restrictions_alimentaires,
        'niveau_activite': profil.niveau_activite,
        'imc': profil.calculer_imc(),
        'bmr': profil.calculer_bmr(),
        'calories_cibles': profil.besoins_caloriques_journaliers(),
        'categorie_imc': profil.determiner_categorie_imc()
    }
}
```

### 3. **Amélioration du Logging** 
Ajout de logs détaillés pour diagnostiquer les erreurs futures:
- Authentification de l'utilisateur ✅
- Extraction du profil_id ✅
- Recherche du Client ✅
- Récupération du ProfilNutritionnel ✅
- Statut des appels n8n ✅

### 4. **Gestion CSRF Améliorée**
**Template (base.html)**:
```html
<meta name="csrf-token" content="{{ csrf_token }}">
```

**JavaScript (script.js)**:
```javascript
// Cherche le token CSRF de plusieurs sources
let token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
            document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            getCookie('csrftoken') ||
            getCookie('csrf');
```

### 5. **Interface Frontend Améliorée**
- Nouvelle section "Recommandations N8N" sur accueil
- Bouton "Obtenir mes recommandations" (utilisateurs connectés)
- Loader pendant le chargement
- Affichage des résultats avec formatting
- Gestion des erreurs détaillée (HTTP + réseau)

### 6. **Gestion d'Erreurs Robuste**
```javascript
if (!response.ok) {
    // Affiche le statut HTTP et le message d'erreur spécifique
    console.error('Erreur HTTP:', response.status, data);
}

// Distinction des types d'erreurs
- SyntaxError → Problème JSON
- TypeError → Problème réseau/CORS
- Autres erreurs → Messages détaillés
```

## 🔍 Diagnostics pour le 400 Bad Request

Le code 400 peut venir de plusieurs sources:

### ❌ **Cause 1: Utilisateur non authentifié**
```
Header manquant: Authorization Token
```
**Solution**: Vérifier que l'utilisateur est connecté (bouton masqué si non-connecté)

### ❌ **Cause 2: Pas de Client/ProfilNutritionnel**
```
Client.DoesNotExist ou ProfilNutritionnel.DoesNotExist
```
**Solution**: Créer/compléter le profil nutritionnel via l'espace client

### ❌ **Cause 3: n8n non disponible**
```
ConnectionError ou Timeout
```
**Solution**: Vérifier que n8n tourne sur localhost:5678

### ❌ **Cause 4: CSRF Token invalide**
```
403 Forbidden (CSRF)
```
**Solution**: Vérifier les headers CSRF dans la requête

## 🧪 Tests Recommandés

### Test 1: Vérifier l'import
```bash
python manage.py shell -c "from myapp.views import RecommenderN8nWebhookView; print('✅ Import OK')"
```

### Test 2: Tester via curl (avec token)
```bash
curl -X POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test 3: Tester via l'interface
1. Se connecter sur http://localhost:8000/
2. Aller à l'accueil
3. Voir la section "Recommandations N8N"
4. Cliquer sur le bouton
5. Vérifier la console (F12) pour les logs détaillés

## 📝 Fichiers Modifiés

| Fichier | Modifications |
|---------|--------------|
| `myapp/views.py` | Suppression plats/menus filtrés, logs améliorés |
| `templates/accueil/accueil.html` | Ajout section recommandations + bouton |
| `static/accueil/script.js` | Gestion complète AJAX + erreurs |
| `templates/base.html` | Meta tag CSRF ajouté |
| `myapp/urls.py` | Route déjà configurée ✅ |
| `requirements.txt` | Dépendances déjà installées ✅ |

## 🚀 Prochaines Étapes

1. **Tester l'endpoint** avec un utilisateur connecté ayant un profil nutritionnel
2. **Vérifier n8n** est accessible sur localhost:5678
3. **Consulter les logs Django** pour déboguer les 400 persistants
4. **Créer un utilisateur de test** avec profil complet si besoin

## 📊 Payload Final (Simplifié)

```json
{
  "profil": {
    "age": 30,
    "poids": 75.5,
    "taille": 180.0,
    "sexe": "M",
    "objectif": "prise_muscle",
    "allergies": "arachides",
    "restrictions_alimentaires": "gluten",
    "niveau_activite": "modere",
    "imc": 23.3,
    "bmr": 1680.5,
    "calories_cibles": 2400.0,
    "categorie_imc": "poids_normal"
  }
}
```

✅ **Plus léger**, plus rapide, plus pertinent pour n8n
