# Structure du Projet - Healthy IA

## 📁 Organisation Générale

```
healthy-ia/
├── README.md                    # Point d'entrée principal
├── manage.py                    # Django management
├── pytest.ini                   # Configuration pytest
│
├── docs/                        # 📚 Documentation
│   ├── README.md               # Index de la documentation
│   ├── setup/                  # 📋 Guides de démarrage
│   ├── api/                    # 🔌 API & N8N
│   ├── features/               # ✨ Fonctionnalités
│   ├── optimization/           # ⚡ Optimisation & Scores
│   ├── troubleshooting/        # 🔧 Dépannage
│   └── guides/                 # 📚 Guides & Architecture
│
├── tests/                       # 🧪 Tests
│   ├── README.md               # Index des tests
│   ├── TEST_SUITE_DOCUMENTATION.md
│   ├── unit/                   # 🧪 Tests unitaires
│   ├── integration/            # 🔗 Tests d'intégration
│   ├── fixtures/               # 🔧 Données et générateurs
│   └── validation/             # ✅ Scripts de validation
│
├── apps/                        # Application Django
├── config/                      # Configuration
├── healthy/                     # Code principal
├── myapp/                       # Applications
├── static/                      # Ressources statiques
├── templates/                   # Templates HTML
└── logs/                        # Fichiers de log
```

## 🚀 Points d'Entrée Rapides

### Pour les Nouveaux Développeurs
1. Lire [docs/README.md](docs/README.md)
2. Suivre [docs/setup/QUICK_START.md](docs/setup/QUICK_START.md)
3. Consulter [docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)

### Pour Exécuter les Tests
1. Consulter [tests/README.md](tests/README.md)
2. Lancer `pytest tests/unit/` pour tests unitaires
3. Lancer `pytest tests/integration/` pour tests complets

### Pour Déboguer
1. Consulter [docs/troubleshooting/README.md](docs/troubleshooting/README.md)
2. Trouver votre erreur et suivre les étapes

### Pour Contribuer
1. Lire [docs/guides/ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)
2. Consulter les guides pertinents dans [docs/](docs/)
3. Exécuter les tests avant de soumettre

## 📚 Documentation par Catégorie

### Setup & Getting Started (`docs/setup/`)
- Configuration environnement
- Démarrage rapide
- Intégration N8N
- Tests

### API & N8N (`docs/api/`)
- Implémentation webhooks
- Documentation endpoints
- Exemples payloads
- Corrections API

### Features (`docs/features/`)
- Navigation (navbar)
- Ligne de commande
- Système d'alertes
- Panier e-commerce

### Optimization (`docs/optimization/`)
- Rapports de performance
- Vérification des scores
- Plans d'optimisation
- Refactoring

### Troubleshooting (`docs/troubleshooting/`)
- Erreurs 404
- Problèmes API
- Debugging ligne de commande
- Erreurs JavaScript

### Guides (`docs/guides/`)
- Architecture générale
- Migration
- Logging & Monitoring
- Documentation technique

## 🧪 Tests par Catégorie

### Unit Tests (`tests/unit/`)
Tests des fonctions individuelles:
- Scoring
- Recommandations
- Restrictions
- Performance

### Integration Tests (`tests/integration/`)
Tests des flux complets:
- API
- Webhooks N8N
- Ligne de commande
- Enregistrement

### Fixtures (`tests/fixtures/`)
Données et générateurs:
- Plats
- Utilisateurs
- Données de test

### Validation (`tests/validation/`)
Scripts de diagnostic:
- Validation scores
- Vérification navbar
- Diagnostic API
- Tests monitoring

## 🔍 Guide de Navigation

| Je veux...                         | Je vais à...                                    |
|------------------------------------|------------------------------------------------|
| Démarrer le projet                 | `docs/setup/QUICK_START.md`                    |
| Comprendre l'architecture          | `docs/guides/ARCHITECTURE.md`                  |
| Intégrer N8N                       | `docs/api/QUICKSTART_N8N.md`                   |
| Lancer les tests                   | `tests/README.md`                              |
| Corriger une erreur 404            | `docs/troubleshooting/README_FIX_404.md`       |
| Optimiser les scores               | `docs/optimization/SCORE_OPTIMIZATION_GUIDE.md`|
| Déboguer la navbar                 | `docs/troubleshooting/` + `tests/validation/verify_navbar.py` |
| Vérifier la cohérence              | `tests/validation/test_monitoring_coherence.py`|
| Contribuer au code                 | `docs/guides/ARCHITECTURE.md` puis consulter la feature pertinente |

## 📊 Statistiques

- **📄 Documents:** ~100 fichiers de documentation
- **🧪 Tests:** 50+ fichiers de tests
- **📚 Guides:** 6 catégories principales
- **🔗 Intégrations:** N8N, API, Django

## ✅ Checklist Intégration

- [ ] Lire la documentation pertinente
- [ ] Consulter l'architecture
- [ ] Lancer les tests existants
- [ ] Créer de nouveaux tests
- [ ] Documenter les changements
- [ ] Valider les scores
- [ ] Vérifier les performances

---

**Dernière mise à jour:** 26 Avril 2026
**Version:** 1.0 - Organisation initiale
