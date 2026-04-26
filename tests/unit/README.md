# Unit Tests

Tests unitaires isolés pour les fonctions individuelles.

## Tests Disponibles

- **test_1_score_simple.py** - Calculs simples de score
- **test_2_score_recommendation_imc.py** - Recommandations IMC
- **test_3_restrictions.py** - Contraintes et restrictions
- **test_4_age_sexe.py** - Paramètres âge et sexe
- **test_5_performance_cache.py** - Performance et caching
- **test_6_integration_menus.py** - Intégration des menus
- **test_score_optimization.py** - Optimisation des calculs
- **test_scoring_verification.py** - Vérification complète du scoring

## Lancer les Tests

```bash
# Tous les tests
pytest tests/unit/

# Un test spécifique
pytest tests/unit/test_1_score_simple.py

# Mode verbose
pytest tests/unit/ -v
```

## Couverture

- ✓ Calculs de score
- ✓ Recommandations
- ✓ Restrictions
- ✓ Optimisations
- ✓ Performance
