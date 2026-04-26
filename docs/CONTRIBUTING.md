# Guide de Contribution

## 🤝 Comment contribuer

### Fork et clone
```bash
git clone https://github.com/yourusername/healthy-ia.git
cd healthy-ia
```

### Créer une branche
```bash
git checkout -b feature/your-feature-name
```

### Développement

#### Structure du code
- Suivez les conventions PEP 8
- Utilisez des noms significatifs
- Documentez votre code avec docstrings
- Écrivez des tests

#### Qualité du code
```bash
# Linting
flake8 apps --max-line-length=100

# Formatage
black apps

# Imports
isort apps

# Type checking
mypy apps
```

#### Tests
```bash
# Tests unitaires
pytest apps/

# Avec couverture
pytest --cov=apps

# Tests spécifiques
pytest apps/users/tests/test_models.py::TestUser
```

### Commits
```bash
# Messages clairs et descriptifs
git commit -m "Add user registration endpoint"

# Format
type(scope): description

# Types: feat, fix, docs, style, refactor, test, chore
# Exemples:
# feat(users): add registration endpoint
# fix(scoring): correct IMC calculation
# docs: update API documentation
```

### Pull Request
1. Push vers votre fork
2. Ouvrir une PR sur le repo principal
3. Décrire les changements
4. Ajouter des tests
5. Mettre à jour la documentation

## 📋 Standards du code

### Python
```python
# Docstrings
def calculate_imc(weight, height):
    """
    Calculer l'indice de masse corporelle.
    
    Args:
        weight (float): Poids en kg
        height (float): Taille en cm
    
    Returns:
        float: IMC
    """
    height_m = height / 100
    return weight / (height_m ** 2)

# Type hints
def get_user_scores(user_id: int) -> List[Score]:
    """Récupérer les scores d'un utilisateur."""
    pass
```

### Models Django
```python
class User(AbstractUser):
    """Description du modèle"""
    
    # Champs
    field_name = models.CharField(max_length=100, verbose_name="Label")
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.get_full_name()
```

### Tests
```python
@pytest.mark.django_db
def test_user_creation():
    """Test: créer un utilisateur"""
    user = User.objects.create_user(
        username='test',
        email='test@example.com'
    )
    assert user.username == 'test'
```

## 🐛 Signaler un bug

1. Vérifier qu'il n'existe pas déjà
2. Ouvrir une issue avec:
   - Description claire
   - Étapes pour reproduire
   - Résultat attendu vs actuel
   - Environnement (Python, Django, OS)

## 💡 Proposer une feature

1. Ouvrir une issue pour discussion
2. Décrire le cas d'usage
3. Proposer une solution
4. Attendre l'approbation avant de coder

## 📚 Documentation

- Mettre à jour les docs en markdown
- Ajouter des exemples d'utilisation
- Maintenir le README à jour
- Documenter les API

## ✅ Checklist avant Pull Request

- [ ] Code testé
- [ ] Tests passent
- [ ] Couverture > 80%
- [ ] Linting OK
- [ ] Documentation mise à jour
- [ ] Commits propres
- [ ] Messages clairs
- [ ] Pas de conflits

## 📞 Questions?

- Ouvrir une issue
- Rejoindre la communauté Discord
- Contacter les mainteneurs
