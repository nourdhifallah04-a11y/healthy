# Structure des Modèles par Package

## Overview

La structure des modèles a été refactorisée pour suivre le pattern **"Une classe = Un fichier"**. Chaque classe de modèle Django est maintenant organisée dans son propre fichier au lieu d'avoir tous les modèles dans un seul `models.py`.

## Avantages

✅ **Séparation des responsabilités** - Chaque classe dans son propre fichier  
✅ **Meilleure lisibilité** - Moins d'une seule grosse classe  
✅ **Maintenance simplifiée** - Trouvez facilement ce que vous cherchez  
✅ **Imports clairs** - Structure logique et intuitive  
✅ **Scalabilité** - Facile d'ajouter de nouveaux modèles  
✅ **Pas d'imports circulaires** - Organisation hiérarchique  

## Structure des Répertoires

```
healthy/
├── apps/
│   ├── users/
│   │   ├── models/
│   │   │   ├── __init__.py           # Importations centralisées
│   │   │   ├── manager.py            # UtilisateurManager
│   │   │   ├── utilisateur.py        # Classe Utilisateur
│   │   │   ├── client.py             # Classe Client
│   │   │   ├── administrateur.py     # Classe Administrateur
│   │   │   └── profil_nutritionnel.py # Classe ProfilNutritionnel
│   │   ├── models.py                 # Fichier proxy pour imports
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── plats/
│   │   ├── models/
│   │   │   ├── __init__.py           # Importations centralisées
│   │   │   ├── plat.py               # Classe Plat
│   │   │   ├── menu.py               # Classe Menu
│   │   │   └── composition_menu.py   # Classe CompositionMenu
│   │   ├── models.py                 # Fichier proxy pour imports
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── commande/
│   │   ├── models/
│   │   │   ├── __init__.py           # Importations centralisées
│   │   │   ├── commande.py           # Classe Commande
│   │   │   └── ligne_commande.py     # Classe LigneCommande
│   │   ├── models.py                 # Fichier proxy pour imports
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── specialdiet/
│   │   ├── models/
│   │   │   ├── __init__.py           # Importations centralisées
│   │   │   └── systemia.py           # Classe SystemeIA
│   │   ├── models.py                 # Fichier proxy pour imports
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── contact/
│   │   ├── models/
│   │   │   └── __init__.py
│   │   └── ... (à compléter)
│   │
│   └── (autres apps...)
```

## Comment Utiliser

### Importer depuis Django (comme avant)

Vous pouvez continuer à importer les modèles comme avant:

```python
from apps.users.models import Utilisateur, Client, ProfilNutritionnel
from apps.plats.models import Plat, Menu, CompositionMenu
from apps.commande.models import Commande, LigneCommande
from apps.specialdiet.models import SystemeIA
```

### Importer directement depuis les fichiers individuels

Ou importer directement des fichiers spécifiques:

```python
from apps.users.models.utilisateur import Utilisateur
from apps.users.models.client import Client
from apps.plats.models.plat import Plat
from apps.commande.models.commande import Commande
```

## Structure de Chaque Fichier de Modèle

### 1. Fichier `__init__.py` du package models

```python
"""
Importation centralisée de tous les modèles de l'app XXXX
"""
from .manager import UtilisateurManager
from .utilisateur import Utilisateur
from .client import Client
...

__all__ = [
    'UtilisateurManager',
    'Utilisateur',
    'Client',
    ...
]
```

### 2. Fichier de classe individuelle

```python
"""
Modèle NomClasse - Description brève
"""
from django.db import models
from .autre_classe import AutreClasse  # Si dépendance

class NomClasse(models.Model):
    """Docstring complète de la classe"""
    field1 = models.CharField(max_length=100)
    field2 = models.ForeignKey(AutreClasse, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "app_nomclasse"
        verbose_name = "Nom Classe"
        verbose_name_plural = "Noms Classe"
    
    def method(self):
        """Méthode"""
        pass
    
    def __str__(self):
        return self.field1
```

### 3. Fichier proxy `models.py`

```python
"""
Importation centralisée des modèles de l'app XXXX
"""
from .models.classe1 import Classe1
from .models.classe2 import Classe2
...

__all__ = [
    'Classe1',
    'Classe2',
    ...
]
```

## App: Users

### Hiérarchie

```
UtilisateurManager (manager.py)
        ↓
Utilisateur (utilisateur.py)
    ├── Client (client.py)
    │   └── ProfilNutritionnel (profil_nutritionnel.py)
    │
    └── Administrateur (administrateur.py)
```

### Dépendances

- `Utilisateur` → `UtilisateurManager` (manager personnalisé)
- `Client` → `Utilisateur` (OneToOneField)
- `Administrateur` → `Utilisateur` (OneToOneField)
- `ProfilNutritionnel` → `Client` (OneToOneField)
- `ProfilNutritionnel` → `Plat` (import conditionnel pour éviter import circulaire)

### Fichiers

1. **manager.py** - Manager personnalisé pour l'authentification par email
2. **utilisateur.py** - Modèle utilisateur personnalisé
3. **client.py** - Profil client
4. **administrateur.py** - Profil administrateur
5. **profil_nutritionnel.py** - Profil nutritionnel du client

## App: Plats

### Hiérarchie

```
Plat (plat.py)
 ├── Menu (menu.py)
 │   └── CompositionMenu (composition_menu.py)
 │
 └── (Utilisé par CompositionMenu)
```

### Dépendances

- `Menu` → `Plat` (ManyToManyField via CompositionMenu)
- `CompositionMenu` → `Menu` + `Plat` (ForeignKeys)

### Fichiers

1. **plat.py** - Modèle plat avec méthodes d'évaluation
2. **menu.py** - Modèle menu composé de plats
3. **composition_menu.py** - Table de liaison Menu-Plat

## App: Commande

### Hiérarchie

```
Commande (commande.py)
    └── LigneCommande (ligne_commande.py)
         ├── Menu (from apps.plats)
         └── Plat (from apps.plats)
```

### Dépendances

- `Commande` → `Client` (ForeignKey)
- `LigneCommande` → `Commande` (ForeignKey)
- `LigneCommande` → `Menu` + `Plat` (ForeignKeys optionnels)

### Fichiers

1. **commande.py** - Modèle commande
2. **ligne_commande.py** - Lignes de commande

## App: SpecialDiet

### Hiérarchie

```
SystemeIA (systemia.py)
    ├── Client (from apps.users)
    └── Menu (from apps.plats)
```

### Dépendances

- `SystemeIA` → `Client` (analyse)
- `SystemeIA` → `Menu` (recommandations)

### Fichiers

1. **systemia.py** - Système IA pour recommandations

## Gestion des Imports Circulaires

Pour éviter les imports circulaires, nous utilisons:

### 1. Imports conditionnels (dans les méthodes)

```python
def recommander_plats(self):
    # Import ici pour éviter import circulaire
    from apps.plats.models import Plat
    ...
```

### 2. Type hints avec strings

```python
def ajouter_plat(self, plat: "Plat", quantite: int = 1):
    ...
```

### 3. Forward references

```python
class Menu(models.Model):
    plats = models.ManyToManyField("Plat", through="CompositionMenu")
```

## Ajout d'un Nouveau Modèle

Pour ajouter un nouveau modèle à une app existante:

1. **Créer le fichier** `apps/app/models/nom_classe.py`

```python
"""
Modèle NomClasse - Description
"""
from django.db import models

class NomClasse(models.Model):
    # Champs et méthodes
    pass
```

2. **Mettre à jour** `apps/app/models/__init__.py`

```python
from .nom_classe import NomClasse

__all__ = [
    ...
    'NomClasse',
]
```

3. **Vérifier** `apps/app/models.py`

(Doit automatiquement inclure la nouvelle classe via l'import)

## Best Practices

✅ **Une classe par fichier** - Pas d'exceptions  
✅ **Noms cohérents** - Nom du fichier = nom de la classe (snake_case)  
✅ **Docstrings complètes** - Décrivez le modèle et ses responsabilités  
✅ **Meta class** - Définissez toujours `db_table`  
✅ **__str__** - Retournez une représentation lisible  
✅ **Imports organisés** - Django, puis local  
✅ **Évitez les imports circulaires** - Utilisez imports conditionnels  

## Avantages pour l'Équipe

### Développeurs

- Trouvez rapidement le code que vous cherchez
- Mettez à jour un modèle sans affecter les autres
- Comprendre les dépendances rapidement

### Code Review

- Reviews plus courtes et focalisées
- Diffs plus clairs
- Meilleure traçabilité

### Maintenance

- Migrations plus claires
- Debugging plus facile
- Refactoring simplifié

## Migration de l'Ancienne Structure

Les anciens fichiers `models.py` (un par app) contiennent maintenant seulement des imports depuis le package `models/`:

```python
# apps/users/models.py (ancien myapp/models.py)
from .models.utilisateur import Utilisateur
from .models.client import Client
...
```

Cela assure la **compatibilité rétro-active** - Le code existant utilisant `from apps.users.models import Utilisateur` continue de fonctionner!

## Fichiers Concernés

### Apps transformées

- ✅ `apps/users/` - 5 classes
- ✅ `apps/plats/` - 3 classes
- ✅ `apps/commande/` - 2 classes
- ✅ `apps/specialdiet/` - 1 classe

### Apps à compléter

- ⏳ `apps/contact/` - À implémenter
- ⏳ `apps/health/` - À implémenter (si existant)

## Références

Django Best Practices:
- https://docs.djangoproject.com/en/stable/topics/db/models/
- https://docs.djangoproject.com/en/stable/ref/models/fields/

Project Structure:
- Voir `STRUCTURE.md` pour vue d'ensemble
- Voir `ARCHITECTURE.md` pour diagrammes

## Questions Fréquemment Posées

**Q: Pourquoi ne pas garder un seul models.py?**  
A: Meilleure organisation et maintenabilité pour les projets larges.

**Q: Cela change-t-il comment importer les modèles?**  
A: Non! Les imports existants continuent de fonctionner.

**Q: Comment gérer les dépendances?**  
A: Utilisez imports conditionnels dans les méthodes si nécessaire.

**Q: Et si deux modèles se dépendent?**  
A: Placez le modèle indépendant en premier dans la hiérarchie.
