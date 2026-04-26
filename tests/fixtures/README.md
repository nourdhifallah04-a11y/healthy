# Fixtures & Generators

Données de test et générateurs pour les tests.

## Générateurs

- **generate_plats.py** - Génère des données de plats
- **generate_plats2.py** - Génère des plats v2
- **generate_plats_reels.py** - Génère des plats réels

## Scripts

- **run_all_tests.py** - Exécute tous les tests du projet

## Utilisation

```bash
# Générer les données
python tests/fixtures/generate_plats.py

# Lancer tous les tests
python tests/fixtures/run_all_tests.py
```

## Structure des Données

Les générateurs créent:
- Entrées (plats d'entrée)
- Plats (plats principaux)
- Desserts
- Données nutritionnelles
- Restrictions diététiques

## Import dans les Tests

```python
from tests.fixtures.generate_plats import create_sample_data
data = create_sample_data()
```
