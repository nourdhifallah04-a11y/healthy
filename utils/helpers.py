"""
Common helper functions for the application.
"""
from typing import Dict, List, Tuple


def format_price(price):
    """Format price for display."""
    return f"${price:.2f}"


def paginate_queryset(queryset, page=1, page_size=10):
    """Paginate a queryset."""
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]


# Nutritional calculation utilities
class NutritionalCalculator:
    """Utility class for nutritional calculations used across models"""
    
    @staticmethod
    def categoriser_calories(calories: float) -> str:
        """Catégorise un aliment par ses calories"""
        if calories < 400:
            return 'leger'
        elif calories < 700:
            return 'modere'
        else:
            return 'energetique'
    
    @staticmethod
    def calculer_score_nutritionnel(calories: float, proteines: float, lipides: float, fibres: float) -> int:
        """Calcule un score nutritionnel de 0 à 100"""
        score = 50
        
        if proteines > 30:
            score += 20
        elif proteines > 20:
            score += 10
        
        if calories > 800:
            score -= 20
        elif calories > 600:
            score -= 10
        
        if fibres > 10:
            score += 10
        elif fibres > 5:
            score += 5
        
        if lipides > 30:
            score -= 10
        
        return min(100, max(0, score))
    
    @staticmethod
    def calculer_nutrition_agregee(items: List[Dict], quantites: List[int] = None) -> Dict:
        """Calcule les totaux nutritionnels pour une liste d'aliments"""
        if not items:
            return {'calories': 0, 'proteines': 0, 'glucides': 0, 'lipides': 0}
        
        if not quantites:
            quantites = [1] * len(items)
        
        total_calories = sum(item.get('calories', 0) * qty for item, qty in zip(items, quantites))
        total_proteines = sum(item.get('proteines', 0) * qty for item, qty in zip(items, quantites))
        total_glucides = sum(item.get('glucides', 0) * qty for item, qty in zip(items, quantites))
        total_lipides = sum(item.get('lipides', 0) * qty for item, qty in zip(items, quantites))
        
        return {
            'calories': total_calories,
            'proteines': total_proteines,
            'glucides': total_glucides,
            'lipides': total_lipides
        }
