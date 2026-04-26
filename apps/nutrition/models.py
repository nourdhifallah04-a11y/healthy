"""
Modèles pour l'app nutrition
"""
from django.db import models
from apps.core.models import TimeStampedModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Food(TimeStampedModel):
    """Modèle pour les aliments"""
    name = models.CharField(max_length=200, unique=True, verbose_name='Nom')
    calories = models.IntegerField(verbose_name='Calories (kcal/100g)')
    proteins = models.FloatField(verbose_name='Protéines (g/100g)')
    carbs = models.FloatField(verbose_name='Glucides (g/100g)')
    fats = models.FloatField(verbose_name='Lipides (g/100g)')
    fiber = models.FloatField(default=0, verbose_name='Fibres (g/100g)')
    
    class Meta:
        verbose_name = 'Aliment'
        verbose_name_plural = 'Aliments'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class NutritionalProfile(TimeStampedModel):
    """Profil nutritionnel utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    age = models.IntegerField(verbose_name='Âge')
    height = models.IntegerField(verbose_name='Taille (cm)')
    weight = models.FloatField(verbose_name='Poids (kg)')
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Masculin'), ('F', 'Féminin')],
        verbose_name='Genre'
    )
    activity_level = models.CharField(
        max_length=20,
        choices=[
            ('sedentary', 'Sédentaire'),
            ('lightly_active', 'Légèrement actif'),
            ('moderately_active', 'Modérément actif'),
            ('very_active', 'Très actif'),
        ],
        default='moderately_active',
        verbose_name='Niveau d\'activité'
    )
    daily_calorie_goal = models.IntegerField(verbose_name='Apport calorique quotidien')
    
    class Meta:
        verbose_name = 'Profil nutritionnel'
        verbose_name_plural = 'Profils nutritionnels'
    
    def __str__(self):
        return f"Profil de {self.user.username}"
