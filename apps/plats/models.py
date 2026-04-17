"""
Importation centralisée des modèles de l'app plats
"""
from .models.plat import Plat
from .models.menu import Menu
from .models.composition_menu import CompositionMenu

__all__ = [
    'Plat',
    'Menu',
    'CompositionMenu',
]
