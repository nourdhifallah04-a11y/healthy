# 🎯 Restructuration Django - Guide de Migration

## ✅ Étape 1 : Nouvelle structure créée

La nouvelle architecture professionnelle a été créée avec :

### 📂 Structure de répertoires
```
config/                    # Configuration centralisée
├── settings/             # Settings multi-environnements
│   ├── base.py          # Configuration commune
│   ├── development.py   # Développement
│   ├── production.py    # Production
│   └── testing.py       # Tests
├── urls.py              # URLs principales
├── wsgi.py              # WSGI application
└── asgi.py              # ASGI application

apps/                      # Applications Django
├── core/                 # App commune (modèles de base, utils)
├── users/                # Gestion utilisateurs
├── nutrition/            # Gestion aliments et profils
├── scoring/              # Système de scoring
│   └── services/         # Logique métier complexe
└── orders/               # Gestion commandes
```

### 📚 Documentation
- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Guide d'installation
- [docs/API.md](docs/API.md) - Documentation API
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Déploiement production
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) - Guide de contribution

### 🧪 Tests
- Tests unitaires dans chaque app (`tests/`)
- Tests d'intégration centralisés (`tests/integration/`)
- Tests de performance (`tests/performance/`)
- Configuration pytest dans `pytest.ini`

## 🚀 Étape 2 : Migration du code existant

### A. Mise à jour du manage.py
Le `manage.py` actuel utilise `myapp.settings`. À mettre à jour en:
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

### B. Migration des modèles

#### ✅ Models à migrer vers les apps appropriées :

**Apps/core/models.py** (ajouter):
- Modèles de base TimeStampedModel, SoftDeleteModel
- QuerySet et Manager personnalisés

**Apps/users/models.py**:
- Modèle User (étendu d'AbstractUser)
- À migrer depuis : `myapp/models.py`

**Apps/nutrition/models.py**:
- Food
- NutritionalProfile
- À migrer depuis : ancien code nutrition

**Apps/scoring/models.py**:
- Score
- Recommendation
- À migrer depuis : `myapp/models.py` ou ancien code

**Apps/orders/models.py**:
- CartItem
- Order
- OrderItem
- À migrer depuis : code existant

### C. Migration des vues et serializers
- Déplacer les vues vers les fichiers `views.py` de chaque app
- Créer les `serializers.py` pour chaque app
- Organiser la logique métier dans `services/` (ex: scoring/services/)

### D. Migration des URLs
- Mettre à jour `config/urls.py` pour inclure les URLs des apps
- Créer `urls.py` dans chaque app avec les routes spécifiques

### E. Migration de l'admin
- Créer `admin.py` dans chaque app
- Migrer l'enregistrement des modèles

## 📋 Checklist de migration

- [ ] Copier les modèles vers les apps appropriées
- [ ] Mettre à jour les vues et serializers
- [ ] Créer/mettre à jour les fichiers `urls.py`
- [ ] Migrer l'admin Django
- [ ] Mettre à jour `INSTALLED_APPS` dans settings
- [ ] Créer les migrations initiales
- [ ] Tester l'application
- [ ] Migrer les données existantes (si nécessaire)
- [ ] Supprimer l'ancien code
- [ ] Mettre à jour la documentation

## 🔧 Configuration initiale

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Configurer l'environnement
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 3. Mettre à jour DJANGO_SETTINGS_MODULE
```python
# manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
```

### 4. Créer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Tester
```bash
python manage.py test
# ou
pytest
```

## 📁 Fichiers à migrer depuis l'ancien code

### Du répertoire racine vers les apps :

```
test_*.py           → tests/integration/ ou apps/*/tests/
generate_*.py       → scripts/
diagnose_*.py       → scripts/
validate_*.py       → scripts/
verify_*.py         → scripts/

# Documentation
*.md (except README, ARCHITECTURE) → docs/
```

### De myapp/ vers les apps :

```
myapp/models.py     → apps/core/, apps/users/, apps/scoring/
myapp/views.py      → apps/*/views.py
myapp/serializers.py → apps/*/serializers.py
myapp/urls.py       → config/urls.py (principale)
myapp/admin.py      → apps/*/admin.py
myapp/forms.py      → apps/*/forms.py (optionnel)
```

## 🧹 Nettoyage après migration

1. Supprimer les anciens répertoires `myapp/` et `healthy/`
2. Supprimer les fichiers de test orphelins de la racine
3. Supprimer les fichiers markdown de documentation orphelins
4. Organiser les fichiers statiques et templates

## 🔄 Exemple : Migrer le modèle Score

### Avant (myapp/models.py)
```python
class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.FloatField()
    # ...
```

### Après (apps/scoring/models.py)
```python
from apps.core.models import TimeStampedModel

class Score(TimeStampedModel):
    SCORE_TYPE_CHOICES = [
        ('professionnel', 'Score Professionnel'),
        ('imc', 'Score IMC'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score_type = models.CharField(
        max_length=20,
        choices=SCORE_TYPE_CHOICES
    )
    value = models.FloatField()
    
    class Meta:
        verbose_name = 'Score'
        unique_together = ('user', 'score_type')
```

## 📞 Support

- Voir la documentation complète : [ARCHITECTURE.md](ARCHITECTURE.md)
- Questions sur l'API : [docs/API.md](docs/API.md)
- Guide d'installation : [docs/INSTALLATION.md](docs/INSTALLATION.md)

## 🎓 Prochaines étapes

1. **Migrer le code existant** vers la nouvelle structure
2. **Tester** : `pytest` ou `python manage.py test`
3. **Optimiser** : Ajouter des index, caching, pagination
4. **Déployer** : Suivre [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

**Créé :** Avril 2024  
**Dernière mise à jour :** Avril 2024
