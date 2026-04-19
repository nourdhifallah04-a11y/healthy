# Exemples de Payloads - Webhook N8N

## 1. Payload envoyé par Django à N8N

Quand un utilisateur appelle l'endpoint `/api/profil-nutritionnel/recommander-n8n/`, Django envoie ce payload à N8N:

```json
{
  "profil": {
    "age": 28,
    "poids": 75.0,
    "taille": 175.0,
    "sexe": "homme",
    "objectif": "prise_muscle",
    "allergies": "arachide, cacahuète",
    "restrictions_alimentaires": "végétarien",
    "niveau_activite": "modere",
    "imc": 24.49,
    "bmr": 1755.53,
    "calories_cibles": 2437.77,
    "categorie_imc": "normal"
  },
  "plats_filtrés": [
    {
      "id": 1,
      "nom": "Poulet rôti aux légumes",
      "description": "Poulet fermier rôti avec légumes de saison sans sauce",
      "calories": 450.0,
      "proteines": 45.0,
      "glucides": 20.0,
      "lipides": 15.0,
      "fibres": 5.0,
      "prix": 12.99
    },
    {
      "id": 2,
      "nom": "Salade méditerranéenne",
      "description": "Tomates, concombre, feta, olives, sans viande",
      "calories": 280.0,
      "proteines": 12.0,
      "glucides": 35.0,
      "lipides": 14.0,
      "fibres": 7.0,
      "prix": 9.99
    },
    {
      "id": 3,
      "nom": "Pâtes complètes bolognaise",
      "description": "Pâtes complètes avec sauce tomate et viande hachée",
      "calories": 520.0,
      "proteines": 35.0,
      "glucides": 55.0,
      "lipides": 12.0,
      "fibres": 6.0,
      "prix": 11.99
    },
    {
      "id": 4,
      "nom": "Œufs brouillés aux épinards",
      "description": "3 œufs brouillés avec épinards frais et pain complet",
      "calories": 320.0,
      "proteines": 22.0,
      "glucides": 18.0,
      "lipides": 18.0,
      "fibres": 4.0,
      "prix": 8.99
    },
    {
      "id": 5,
      "nom": "Saumon grillé",
      "description": "Filet de saumon sauvage grillé avec citron et herbes",
      "calories": 380.0,
      "proteines": 42.0,
      "glucides": 0.0,
      "lipides": 22.0,
      "fibres": 0.0,
      "prix": 14.99
    }
  ],
  "menus_filtrés": [
    {
      "id": 1,
      "nom": "Menu Protéiné",
      "description": "Menu spécialement conçu pour la prise de muscle avec protéines élevées",
      "calories": 1200.0,
      "proteines": 130.0,
      "glucides": 80.0,
      "lipides": 30.0,
      "prix": 25.99
    },
    {
      "id": 2,
      "nom": "Menu Équilibré",
      "description": "Menu équilibré pour l'entretien avec répartition optimale des macronutriments",
      "calories": 1000.0,
      "proteines": 85.0,
      "glucides": 120.0,
      "lipides": 25.0,
      "prix": 22.99
    },
    {
      "id": 3,
      "nom": "Menu Léger",
      "description": "Menu faible en calories pour la perte de poids",
      "calories": 750.0,
      "proteines": 65.0,
      "glucides": 75.0,
      "lipides": 18.0,
      "prix": 18.99
    }
  ]
}
```

## 2. Format de réponse attendu de N8N

N8N doit retourner un JSON structuré ainsi:

```json
{
  "profil": {
    "imc": 24.49,
    "bmr": 1755.53,
    "calories_cibles": 2437.77
  },
  "recommandations": {
    "plats": [
      {
        "id": 1,
        "score": 92.5,
        "justification": "Excellente source de protéines (45g) pour la prise de muscle. Calories modérées (450 kcal), bon équilibre macronutriments pour l'objectif."
      },
      {
        "id": 5,
        "score": 88.3,
        "justification": "Riche en protéines (42g) et oméga-3. Très faible en glucides. Parfait pour un apport protéique de qualité."
      },
      {
        "id": 4,
        "score": 82.1,
        "justification": "Bon apport protéique (22g) malgré les restrictions (végétarien). Œufs = protéines complètes de haute qualité."
      },
      {
        "id": 2,
        "score": 45.2,
        "justification": "Respecte les restrictions (végétarien) mais protéines insuffisantes (12g) pour l'objectif de prise muscle."
      },
      {
        "id": 3,
        "score": 38.7,
        "justification": "Contient de la viande (allergie/restriction non mentionnée mais à vérifier). À éviter selon restrictions."
      }
    ],
    "menus": [
      {
        "id": 1,
        "score": 94.2,
        "justification": "Menu optimal pour objectif prise_muscle: 130g protéines, 1200 kcal = surplus calorique modéré, excellent ratio protéine/calorie."
      },
      {
        "id": 2,
        "score": 71.5,
        "justification": "Menu équilibré mais avec insuffisance protéique (85g) pour l'objectif de prise muscle. Plutôt pour maintien."
      },
      {
        "id": 3,
        "score": 28.3,
        "justification": "Calories trop basses (750 kcal) pour objectif prise_muscle. Meilleur pour perte_poids, non aligné au profil."
      }
    ]
  }
}
```

## 3. Réponse finale reçue par le client

Le client reçoit ceci:

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
    "allergies": "arachide, cacahuète",
    "restrictions_alimentaires": "végétarien",
    "niveau_activite": "modere",
    "imc": 24.49,
    "bmr": 1755.53,
    "calories_cibles": 2437.77,
    "categorie_imc": "normal"
  },
  "recommendations": {
    "profil": {
      "imc": 24.49,
      "bmr": 1755.53,
      "calories_cibles": 2437.77
    },
    "recommandations": {
      "plats": [
        {
          "id": 1,
          "score": 92.5,
          "justification": "..."
        }
      ],
      "menus": [
        {
          "id": 1,
          "score": 94.2,
          "justification": "..."
        }
      ]
    }
  }
}
```

## 4. Exemple de réponse d'erreur

### Profil non trouvé (404)
```json
{
  "success": false,
  "error": "Profil nutritionnel non trouvé pour cet utilisateur"
}
```

### N8N indisponible (503)
```json
{
  "success": false,
  "error": "Impossible de se connecter au webhook n8n: Connection refused",
  "webhook_url": "http://localhost:5678/webhook/reco-nutrition"
}
```

### Timeout N8N (504)
```json
{
  "success": false,
  "error": "Timeout du webhook n8n: [Errno 110] Connection timed out"
}
```

### Erreur N8N (400)
```json
{
  "success": false,
  "error": "Erreur du webhook n8n: 400",
  "details": "Détails de l'erreur du webhook..."
}
```

## 5. Structure recommandée pour le workflow N8N

Voici ce que le workflow N8N devrait faire:

1. **Récevoir le webhook** (POST sur `/webhook/reco-nutrition`)
2. **Extraire les données du profil**
   - Calculs IMC, BMR, calories cibles
3. **Analyser les plats**
   - Vérifier allergies/restrictions
   - Calculer score de recommandation (0-100)
   - Justifier le score
4. **Analyser les menus**
   - Même processus que les plats
5. **Trier les résultats**
   - Plats: Top 5 par score décroissant
   - Menus: Top 3 par score décroissant
6. **Retourner la réponse JSON**

## 6. Détails de calcul du score (exemple)

Pour un profil avec objectif "prise_muscle":

```
Score plat = 0

// Vérifier allergie/restriction
if ("arachide" in description) → return 0
if ("cacahuète" in description) → return 0
if ("viande" in description && restrictions == "végétarien") → return 0

// Évaluation protéines (priorité: 30-50g)
if proteine between 30-50 → +35 points
else if proteine >= 25 → +25 points
else if proteine >= 20 → +15 points
else → +5 points

// Évaluation calories (1200-1500 kcal/repas typique)
if 400-600 kcal → +25 points
else if 600-800 kcal → +20 points
else if 200-400 or 800-1000 kcal → +10 points
else → +2 points

// Évaluation glucides (équilibrés: 40-60g)
if 40-60 glucides → +20 points
else if 30-70 glucides → +12 points
else → +5 points

// Évaluation lipides (modérés: 10-25g)
if 10-25 lipides → +15 points
else if 8-30 lipides → +10 points
else → +3 points

// Bonus âge/sexe
if sexe == "homme" && proteine > 25 → +2 points
if age < 30 && calories > 600 → +1 point

Total: 0-100
```

## 7. Cas de restriction spéciale

Gérer les restrictions communes:

```
Restrictions à vérifier:
- "végétarien" → Rejeter si viande, poulet, boeuf, poisson, jambon
- "végane" → Rejeter si viande, œuf, lait, fromage, beurre
- "sans gluten" → Rejeter si blé, pain, pâtes, biscuits
- "sans lactose" → Rejeter si lait, fromage, beurre, crème
- "sans sucre" → Rejeter si sucre, miel, confiture, pâtisserie
```

---

## Intégration dans N8N

1. Créer un nœud "Webhook" avec route `/webhook/reco-nutrition`
2. Ajouter nœuds de traitement:
   - Extract Data
   - Set (calculs)
   - IF (vérifications allergies)
   - Execute function (scoring)
3. Retourner la réponse JSON formatée

Besoin d'aide? Consulter la doc N8N: https://docs.n8n.io/nodes/n8n-nodes-base.webhook/
