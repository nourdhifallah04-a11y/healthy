"""
Nutrition app - Gestion des aliments et profils nutritionnels
"""
from django.apps import AppConfig

class NutritionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.nutrition'
    verbose_name = 'Nutrition'
