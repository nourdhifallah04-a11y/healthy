# Validation & Diagnostics

Scripts de validation et diagnostic pour vérifier le système.

## Scripts de Validation

- **validate_scores.py** - Valide les calculs de score
- **verify_navbar.py** - Vérifie la navbar

## Scripts de Diagnostic

- **diagnose_api.py** - Diagnostic API
- **diagnostic_reco.py** - Diagnostic recommandations

## Tests API

- **test_api_endpoint.py** - Tests endpoints API
- **test_monitoring_api.py** - Monitoring API

## Tests Ligne de Commande

- **test_ligne_api.py** - API ligne de commande
- **test_ligne_commande_api.py** - Ligne de commande API
- **test_ligne_commande_fixed.py** - Ligne de commande (version fixée)
- **test_ligne_debug.py** - Debug ligne de commande

## Tests Monitoring

- **test_monitoring_coherence.py** - Cohérence du monitoring
- **test_monitoring_improved.py** - Monitoring amélioré

## Tests des Alertes

- **test_new_alerts.py** - Tests des nouvelles alertes

## Autres Tests

- **test_import.py** - Tests imports
- **test_with_cookie.py** - Tests avec cookies de session
- **test_spec_js_fix.py** - Tests specs JavaScript
- **test_simulation_browser.py** - Simulation navigateur
- **n8n_webhook_endpoint.py** - Endpoint webhook N8N

## Lancer les Tests

```bash
# Validation des scores
python tests/validation/validate_scores.py

# Vérification navbar
python tests/validation/verify_navbar.py

# Diagnostic API
python tests/validation/diagnose_api.py

# Tests spécifiques
pytest tests/validation/test_api_endpoint.py -v
```

## Résultats

Ces tests génèrent des rapports:
- Validation: Succès/Échec
- Diagnostic: État du système
- Couverture: Points couverts
