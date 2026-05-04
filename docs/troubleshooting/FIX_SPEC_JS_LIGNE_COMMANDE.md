# RÉSUMÉ DES CORRECTIONS - POST /api/ligne-commande/ 404

## Problème
Le endpoint POST `http://localhost:8000/api/ligne-commande/` retournait une erreur **404 (Not Found)** dans le fichier `spec.js`.

## Cause Identifiée
Le problème venait d'un **mismatch entre les données**:
- **Avant**: Le code chargeait les **plats** (`/plat/api/plats/`) et envoyait `id_plat` (plat ID)
- **Besoin**: L'API attend un `menu_id` (menu ID), pas un plat ID
- **Résultat**: Le POST échouait car le menu n'existait pas (404)

## Solution Implémentée

### 1. **Changement du endpoint de chargement** 📊
```javascript
// AVANT
fetch('/plat/api/plats/')

// APRÈS  
fetch('/api/menus/')
```

### 2. **Adaptation de la fonction de transformation** 🔄
```javascript
// AVANT: Transformait un Plat
function transformerPlatEnMealDiet(plat) {
    return {
        id: plat.id_plat,  // ❌ Plat ID
        name: plat.nom,
        calories: plat.calorie,
        // ...
    }
}

// APRÈS: Transforme un Menu
function transformerPlatEnMealDiet(menu) {
    const valeurNutrition = menu.valeur_nutritionnelle || {};
    return {
        id: menu.id_menu,  // ✅ Menu ID
        name: menu.nom,
        calories: valeurNutrition.calories,
        // ...
    }
}
```

### 3. **Amélioration du traitement des erreurs dans addToCartForm** ⚠️
- ✅ Ajout de logs console pour déboguer
- ✅ Gestion correcte du parsing JSON avant accès à `response.status`
- ✅ Meilleure gestion des erreurs 400, 404, 401, 403
- ✅ Message d'erreur incluant l'ID du menu pour faciliter le déboggage

```javascript
// Avant: Crash possible
const data = await response.json();
if (response.status === 401 || response.status === 403) { ... }

// Après: Ordre correct
console.log('Response status:', response.status);
if (response.status === 401 || response.status === 403) { ... }
const data = await response.json();
```

## Fichiers Modifiés
- `c:\Users\achra\Desktop\wockspace\healthy\static\specialdiet\spec.js`

## Tests de Validation
Tous les tests passent ✅:

### ✅ TEST 1: GET /api/menus/
- Status: 200 OK
- Menus disponibles: 1
- Données correctement formatées

### ✅ TEST 2: POST /api/ligne-commande/ 
- Status: 201 Created
- LigneCommande créée avec succès
- Avec menu_id=1 et quantite=1

### ✅ TEST 3: Transformation logique
- Tous les champs du menu sont présents
- Les valeurs nutritionnelles sont accessibles
- Les IDs sont correctement mappés

## Comportement Frontend Maintenant
1. Page `specialdiet` charge les **menus** depuis l'API
2. Chaque "meal card" affiche maintenant un menu complet (avec ses valeurs nutritionnelles)
3. Quand l'utilisateur clique "Ajouter au Panier":
   - Le menu_id correct est envoyé au POST
   - L'authentification est vérifiée
   - Une LigneCommande est créée (201)
   - Un message de succès s'affiche

## Configuration Finale
```javascript
// addToCartForm envoie maintenant:
POST /api/ligne-commande/
{
    "menu_id": 1,        // ✅ Correct
    "quantite": 2        // ✅ Correct
}

// Headers:
{
    "Content-Type": "application/json",
    "X-CSRFToken": "..."  // ✅ CSRF token valide
}

// Credentials: same-origin  // ✅ Session cookie inclus
```

## Vérification Manuelle (Si nécessaire)
```bash
# Test du POST avec curl/Postman
POST http://localhost:8000/api/ligne-commande/
{
    "menu_id": 1,
    "quantite": 1
}
# Résultat: 201 Created ✅
```

## ✅ CONCLUSION
L'erreur **404** est maintenant résolue. Le POST `/api/ligne-commande/` fonctionne correctement avec les sessions authentifiées.
