# Architecture Django - Healthy IA

## 📋 Structure Proposée

```
healthy-ia/
├── config/                           # Configuration Django
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Paramètres communs
│   │   ├── development.py           # Développement
│   │   ├── production.py            # Production
│   │   └── testing.py               # Tests
│   ├── urls.py                      # URLs principales
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
│
├── apps/                             # Applications Django
│   ├── users/                        # Gestion utilisateurs
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   └── tests/
│   │
│   ├── nutrition/                    # Core nutrition
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── services.py              # Logique métier
│   │   ├── admin.py
│   │   └── tests/
│   │
│   ├── scoring/                      # Système de scoring
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── calculator.py        # Calculs des scores
│   │   │   ├── recommendation.py    # Recommandations
│   │   │   └── monitoring.py        # Monitoring
│   │   ├── admin.py
│   │   └── tests/
│   │
│   ├── orders/                       # Gestion commandes
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── admin.py
│   │   └── tests/
│   │
│   └── core/                         # App commune
│       ├── models.py                 # Modèles de base
│       ├── views.py                  # Vues communes
│       ├── serializers.py
│       ├── middleware/
│       ├── permissions/
│       ├── utils/
│       └── tests/
│
├── static/                           # Fichiers statiques
│   ├── css/
│   ├── js/
│   │   ├── profil_nutritionnel/
│   │   ├── navbar/
│   │   └── common/
│   ├── images/
│   └── vendor/
│
├── media/                            # Fichiers upload
│   └── uploads/
│
├── templates/                        # Templates HTML
│   ├── base.html
│   ├── dashboard/
│   ├── nutrition/
│   ├── scoring/
│   ├── orders/
│   ├── users/
│   └── errors/
│
├── tests/                            # Tests au niveau projet
│   ├── __init__.py
│   ├── conftest.py                  # Configuration pytest
│   ├── fixtures.py
│   ├── integration/
│   │   ├── test_api_integration.py
│   │   └── test_workflow.py
│   ├── performance/
│   │   └── test_performance.py
│   └── e2e/
│       └── test_user_flows.py
│
├── docs/                             # Documentation
│   ├── API.md
│   ├── INSTALLATION.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
│
├── scripts/                          # Scripts utilitaires
│   ├── generate_data.py
│   ├── backup.py
│   ├── deploy.py
│   └── maintenance.py
│
├── logs/                             # Logs applicatifs
│   └── .gitkeep
│
├── .env.example                      # Variables d'environnement
├── .env                              # (gitignore)
├── .gitignore
├── manage.py                         # Point d'entrée Django
├── requirements.txt
├── requirements-dev.txt
├── requirements-prod.txt
├── pytest.ini
├── docker-compose.yml
├── Dockerfile
├── README.md
└── ARCHITECTURE.md                   # Ce fichier
```

## 🎯 Principes de cette Architecture

### 1. **Séparation des préoccupations**
   - Chaque app Django a une responsabilité unique
   - `services/` pour la logique métier complexe
   - `serializers/` pour la sérialisation API

### 2. **Configuration multi-environnements**
   - `settings/base.py` : Configuration commune
   - `settings/development.py` : Développement
   - `settings/production.py` : Production
   - `settings/testing.py` : Tests

### 3. **Tests organisés**
   - Tests unitaires dans chaque app
   - Tests d'intégration au niveau projet
   - Tests de performance séparés

### 4. **Documentation centralisée**
   - Réduction du chaos de fichiers .md à la racine
   - Documentation dans le dossier `docs/`

### 5. **Scripts utilitaires**
   - Tous les scripts Python utilitaires regroupés dans `scripts/`
   - Générations de données, backups, déploiements

## 📦 Apps Django Proposées

### `config`
- Configuration centralisée
- Paramètres par environnement
- URLs principales

### `apps/users`
- Authentification
- Profils utilisateurs
- Gestion des rôles

### `apps/nutrition`
- Modèles d'aliments
- Profils nutritionnels
- Analyse nutritionnelle

### `apps/scoring`
- Calcul des scores
- Recommandations
- Monitoring des scores

### `apps/orders`
- Gestion des commandes
- Panier d'achat
- Intégration paiement

### `apps/core`
- Modèles de base
- Permissions personnalisées
- Middlewares
- Utilitaires communs

## 🚀 Étapes de Migration

1. **Préparation** (complète)
2. **Création structure** (complète)
3. **Migration des fichiers**
4. **Refactorisation du code**
5. **Tests et validation**
6. **Documentation**
