"""
Service de recommandations
"""
from django.contrib.auth import get_user_model
from apps.nutrition.models import NutritionalProfile
from .models import Recommendation

User = get_user_model()

class RecommendationEngine:
    """Moteur de recommandations"""
    
    @staticmethod
    def generate_recommendations(user):
        """Générer des recommandations personnalisées"""
        profile = getattr(user, 'nutritionalprofile', None)
        if not profile:
            return []
        
        recommendations = []
        
        # Recommandations basées sur l'IMC
        imc = profile.weight / ((profile.height / 100) ** 2)
        if imc > 25:
            recommendations.append(Recommendation(
                user=user,
                title="Augmenter l'activité physique",
                description="Pratiquez au moins 30 minutes d'activité modérée par jour",
                priority='high'
            ))
        
        # Recommandations basées sur l'âge
        if profile.age > 50:
            recommendations.append(Recommendation(
                user=user,
                title="Augmenter l'apport en calcium",
                description="Consommez plus de produits laitiers et aliments riches en calcium",
                priority='medium'
            ))
        
        return recommendations
