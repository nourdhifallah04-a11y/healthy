# Refactoring: Migration from myapp to apps/

## Overview
Cette documentation décrit la restructuration complète du projet pour passer d'une architecture monolithique (`myapp`) à une architecture modulaire basée sur des Django apps spécialisées sous `apps/`.

## Architecture Avant (Legacy)
```
myapp/
├── models.py (Utilisateur, Client, Administrateur, ProfilNutritionnel, Plat, Menu, Commande, LigneCommande, SystemeIA)
├── serializers.py
├── views.py
├── admin.py
└── migrations/
```

## Architecture Après (Refactorisée)
```
apps/
├── core/                    # Models de base et utilities
├── users/                   # Gestion des utilisateurs
│   ├── models.py           # User, Utilisateur, Client, Administrateur
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   └── migrations/
├── nutrition/              # Gestion nutritionnelle et plats
│   ├── models.py           # Food, NutritionalProfile, ProfilNutritionnel, Plat, Menu
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   └── migrations/
├── orders/                 # Gestion des commandes
│   ├── models.py           # CartItem, Order, OrderItem, Commande, LigneCommande
│   ├── serializers.py
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   └── migrations/
├── scoring/                # Système de scoring
│   ├── models.py           # Score, Recommendation
│   ├── services/
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   └── migrations/
└── ai/                     # Intelligence Artificielle (NOUVEAU)
    ├── models.py           # SystemeIA
    ├── serializers.py
    ├── views.py
    ├── admin.py
    ├── urls.py
    ├── apps.py
    ├── tests.py
    └── migrations/
```

## Détails de la Migration

### 1. **apps/users/** - Gestion des Utilisateurs
**Models migrés :**
- `Utilisateur` - Modèle utilisateur personnalisé (AbstractUser) avec email comme USERNAME_FIELD
- `Client` - Relation OneToOne avec Utilisateur
- `Administrateur` - Relation OneToOne avec Utilisateur
- `User` - Modèle gardé pour compatibilité avec TimeStampedModel

**Changements clés :**
- `db_table = "users_utilisateur"` pour cohérence des noms
- AUTH_USER_MODEL défini à `users.Utilisateur` dans config/settings/base.py

### 2. **apps/nutrition/** - Alimentation et Profils Nutritionnels
**Models migrés :**
- `Food` - Modèle alimentaire existant conservé
- `NutritionalProfile` - Profil nutritionnel existant conservé
- `ProfilNutritionnel` - Profil client personnalisé avec calcul IMC/BMR
- `Plat` - Modèle de plat avec scoring nutritionnel
- `Menu` - Modèle de menu avec liste de plats et calculs nutritionnels

**Fonctionnalités avancées :**
- Calcul IMC (`calculer_imc()`)
- Calcul BMR via formule Harris-Benedict (`calculer_bmr()`)
- Besoins caloriques journaliers (`besoins_caloriques_journaliers()`)
- Scoring nutritionnel avec cache (`calculer_score_nutritionnel()`)
- Recommandations de plats basées sur profil (`recommander_plats()`)

### 3. **apps/orders/** - Gestion des Commandes
**Models migrés :**
- `CartItem` - Article du panier existant conservé
- `Order` - Commande existante conservée
- `OrderItem` - Ligne de commande existante conservée
- `Commande` - Commande personnalisée du client
- `LigneCommande` - Ligne de commande flexible (Menu ou Plat)

**Fonctionnalités :**
- Support Menu ET Plat dans une même commande
- Calcul des valeurs nutritionnelles totales (`calculer_nutrition_totale()`)
- Validation de commande
- Calcul du total automatique

### 4. **apps/ai/** (NOUVEAU) - Système d'Intelligence Artificielle
**Models créés :**
- `SystemeIA` - Moteur de recommandation personnalisé

**Fonctionnalités :**
- Analyse des préférences clients (`analyser_preferences()`)
- Recommandation de menus basée sur historique (`recommander_menus()`)
- Prise en compte de l'objectif et des préférences historiques

### 5. **config/settings/base.py** - Configuration Centralisée
**Modifications :**
```python
INSTALLED_APPS += [
    'apps.core',
    'apps.users',
    'apps.nutrition',
    'apps.scoring',
    'apps.orders',
    'apps.ai',  # NOUVEAU
]

AUTH_USER_MODEL = 'users.Utilisateur'
```

### 6. **config/urls.py** - Routing Centralisé
**Nouveau endpoint :**
```python
path('api/v1/ai/', include('apps.ai.urls', namespace='ai')),
```

## Implication des Imports

### Avant
```python
from myapp.models import Utilisateur, Plat, Menu, Commande
from myapp.serializers import ClientSerializer
```

### Après
```python
from apps.users.models import Utilisateur, Client, Administrateur
from apps.nutrition.models import Plat, Menu, ProfilNutritionnel
from apps.orders.models import Commande, LigneCommande
from apps.ai.models import SystemeIA
from apps.users.serializers import ClientSerializer
```

## Migrations Django

Pour appliquer le nouveau modèle de données :

```bash
# Générer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Charger les données (si nécessaire)
python manage.py loaddata fixture.json
```

## À Faire (Prochaines Étapes)

1. ✅ Structurer les models dans les apps appropriées
2. ✅ Créer serializers pour chaque app
3. ✅ Ajouter admin registrations complètes
4. ✅ Enregistrer la nouvelle app `ai` dans INSTALLED_APPS
5. ✅ Mettre à jour config/urls.py
6. ⏳ **Générer les migrations Django**
7. ⏳ Mettre à jour les imports dans tous les fichiers du projet
8. ⏳ Archiver/Supprimer le dossier `myapp/`
9. ⏳ Tester l'intégration complète
10. ⏳ Mettre à jour la documentation du projet

## Avantages de cette Refactorisation

- **Modularité** : Chaque app a une responsabilité bien définie
- **Maintenabilité** : Séparation claire des domaines métier
- **Scalabilité** : Facilité d'ajouter des apps sans impacter les existantes
- **Testabilité** : Tests unitaires isolés par app
- **Réutilisabilité** : Les apps peuvent être extraites comme packages indépendants
- **Documentation** : Structure claire et auto-documentée

## Notes de Configuration

### Custom User Model
Le projet utilise `Utilisateur` (AbstractUser) comme custom user model au lieu du User par défaut Django.
Cela permet :
- Utiliser `email` comme champ d'authentification
- Ajouter des champs spécifiques (nom, prenom, telephone, etc.)
- Gérer les rôles (Client, Administrateur) via des modèles liés

### Score Caching
Les modèles `Plat` utilisent un système de cache pour optimiser le calcul des scores :
- `get_cached_score()` - Récupère le score du cache
- `set_cached_score()` - Sauvegarde le score en cache
- Clé de cache = `score_{id}_{valeurs_nutritionnelles}`

## Fichiers Modifiés

| Fichier | Type | Action |
|---------|------|--------|
| `apps/users/models.py` | Update | Ajout Utilisateur, Client, Administrateur |
| `apps/users/serializers.py` | Update | Ajout serializers pour nouveaux models |
| `apps/users/admin.py` | Update | Ajout admin registrations |
| `apps/nutrition/models.py` | Update | Ajout Plat, Menu, ProfilNutritionnel |
| `apps/nutrition/serializers.py` | Update | Ajout serializers nutrition |
| `apps/nutrition/admin.py` | Update | Ajout admin registrations |
| `apps/orders/models.py` | Update | Ajout Commande, LigneCommande |
| `apps/orders/admin.py` | Update | Ajout admin registrations |
| `apps/ai/` | Create | Nouvelle app avec SystemeIA |
| `config/settings/base.py` | Update | Ajout apps.ai + AUTH_USER_MODEL |
| `config/urls.py` | Update | Ajout route /api/v1/ai/ |

## Rollback (Si Nécessaire)

Pour revenir à l'architecture précédente :
1. Garder une branche git avec l'ancien code
2. Conserver les migrations `0001_initial` pour chaque app
3. Documenter tout changement d'import

---
**Dernière mise à jour** : 2024
**Status** : En cours - Migrations Django et tests requis
