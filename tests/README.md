# Tests - Healthy IA

## Structure des Tests

### 🧪 [Unit Tests](unit/)
Tests unitaires pour vérifier les fonctions individuelles.

**Fichiers:**
- `test_1_score_simple.py` - Tests simples de scoring
- `test_2_score_recommendation_imc.py` - Tests IMC et recommandations
- `test_3_restrictions.py` - Tests des restrictions
- `test_4_age_sexe.py` - Tests âge/sexe
- `test_5_performance_cache.py` - Tests performance et cache
- `test_6_integration_menus.py` - Tests intégration des menus
- `test_score_optimization.py` - Tests optimisation des scores
- `test_scoring_verification.py` - Tests vérification du scoring

### 🔗 [Integration Tests](integration/)
Tests d'intégration pour vérifier l'interaction entre composants.

**Fichiers:**
- `test_integration_complete.py` - Tests intégration complète
- `test_api_ligne_simple.py` - Tests API ligne de commande simple
- `test_commande_feature.py` - Tests fonctionnalité ligne de commande
- `test_n8n_webhook.py` - Tests webhooks N8N
- `test_unified_system.py` - Tests système unifié
- `test_registration.py` - Tests enregistrement utilisateur
- `test_api_integration.py` - Tests intégration API

### 🔧 [Fixtures & Generators](fixtures/)
Données de test et générateurs.

**Fichiers:**
- `generate_plats.py` - Générateur de plats
- `generate_plats2.py` - Générateur de plats v2
- `generate_plats_reels.py` - Générateur de plats réels
- `run_all_tests.py` - Script pour lancer tous les tests

### ✅ [Validation & Diagnostics](validation/)
Scripts de validation et diagnostic.

**Fichiers de validation:**
- `validate_scores.py` - Validation des scores
- `verify_navbar.py` - Vérification de la navbar
- `diagnose_api.py` - Diagnostic API
- `diagnostic_reco.py` - Diagnostic recommandations

**Fichiers de test API:**
- `test_api_endpoint.py` - Tests endpoints API
- `test_api_ligne_simple.py` - Tests API simple
- `test_monitoring_api.py` - Monitoring API

**Fichiers de test ligne de commande:**
- `test_ligne_api.py` - Tests API ligne
- `test_ligne_commande_api.py` - Tests ligne de commande API
- `test_ligne_commande_fixed.py` - Tests fixes ligne de commande
- `test_ligne_debug.py` - Debug ligne de commande

**Tests de monitoring:**
- `test_monitoring_coherence.py` - Cohérence monitoring
- `test_monitoring_improved.py` - Monitoring amélioré

**Tests des alertes:**
- `test_new_alerts.py` - Nouvelles alertes

**Autres tests:**
- `test_import.py` - Tests imports
- `test_with_cookie.py` - Tests avec cookies
- `test_spec_js_fix.py` - Tests specs JavaScript
- `test_simulation_browser.py` - Simulation navigateur
- `n8n_webhook_endpoint.py` - Endpoint webhook N8N

## Lancer les Tests

### Tous les tests
```bash
python tests/fixtures/run_all_tests.py
```

### Tests unitaires uniquement
```bash
pytest tests/unit/
```

### Tests d'intégration uniquement
```bash
pytest tests/integration/
```

### Tests de validation
```bash
python tests/validation/validate_scores.py
python tests/validation/verify_navbar.py
```

## Structure des Résultats

- ✅ **Passing**: Tests réussis
- ❌ **Failing**: Tests échoués
- ⏭️ **Skipped**: Tests ignorés
- ⚠️ **Warnings**: Avertissements

## Configuration

Voir `pytest.ini` et `TEST_SUITE_DOCUMENTATION.md` pour la configuration.
