# Integration Tests

Tests d'intégration complète entre composants et systèmes.

## Tests Disponibles

- **test_integration_complete.py** - Test intégration complète du système
- **test_api_ligne_simple.py** - API ligne de commande simple
- **test_commande_feature.py** - Feature ligne de commande
- **test_n8n_webhook.py** - Webhooks N8N
- **test_unified_system.py** - Système unifié
- **test_registration.py** - Enregistrement utilisateur
- **test_api_integration.py** - Intégration API

## Lancer les Tests

```bash
# Tous les tests
pytest tests/integration/

# Un test spécifique
pytest tests/integration/test_integration_complete.py

# Mode verbose
pytest tests/integration/ -v
```

## Couverture

- ✓ Flux complets utilisateur
- ✓ Intégration API
- ✓ Webhooks N8N
- ✓ Système de commandes
- ✓ Enregistrement

## Dépendances

Ces tests peuvent nécessiter:
- Base de données configurée
- Services externes accessibles
- Environnement .env configuré
