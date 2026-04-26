"""
Service de calcul des scores
"""
import math
from django.contrib.auth import get_user_model
from apps.nutrition.models import NutritionalProfile

User = get_user_model()

class ScoreCalculator:
    """Classe pour calculer les scores"""
    
    @staticmethod
    def calculate_imc_score(weight, height):
        """Calculer le score IMC"""
        height_m = height / 100
        imc = weight / (height_m ** 2)
        
        # Classification IMC
        if imc < 18.5:
            return imc, "Insuffisance pondérale"
        elif 18.5 <= imc < 25:
            return 100, "Poids normal"
        elif 25 <= imc < 30:
            return 75, "Surpoids"
        elif 30 <= imc < 35:
            return 50, "Obésité classe 1"
        elif 35 <= imc < 40:
            return 25, "Obésité classe 2"
        else:
            return 0, "Obésité classe 3"
    
    @staticmethod
    def calculate_professional_score(user):
        """Calculer le score professionnel"""
        profile = getattr(user, 'nutritionalprofile', None)
        if not profile:
            return 0
        
        # Critères de scoring
        score = 50  # Score de base
        
        # Bonus pour l'âge
        if 25 <= profile.age <= 65:
            score += 20
        
        # Bonus pour le poids
        imc_score, _ = ScoreCalculator.calculate_imc_score(
            profile.weight,
            profile.height
        )
        score += (imc_score / 100) * 30
        
        return min(score, 100)
    
    @staticmethod
    def calculate_nutritional_score(daily_intake, daily_goal):
        """Calculer le score nutritionnel"""
        if daily_goal == 0:
            return 0
        
        percentage = (daily_intake / daily_goal) * 100
        
        if 85 <= percentage <= 110:
            return 100
        elif 70 <= percentage <= 130:
            return 80
        else:
            return 60
