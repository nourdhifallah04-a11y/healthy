"""
Importation centralisée de tous les modèles de l'app users
"""
from .manager import UtilisateurManager
from .utilisateur import Utilisateur
from .client import Client
from .administrateur import Administrateur
from .profil_nutritionnel import ProfilNutritionnel

__all__ = [
    'UtilisateurManager',
    'Utilisateur',
    'Client',
    'Administrateur',
    'ProfilNutritionnel',
]
