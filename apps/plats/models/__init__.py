"""
Importation centralisée de tous les modèles de l'app plats
"""
from .plat import Plat
from .menu import Menu
from .composition_menu import CompositionMenu

__all__ = [
    'Plat',
    'Menu',
    'CompositionMenu',
]
