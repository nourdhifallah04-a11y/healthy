"""
Modèles pour l'app scoring
"""
from django.db import models
from apps.core.models import TimeStampedModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Score(TimeStampedModel):
    """Modèle pour les scores"""
    SCORE_TYPE_CHOICES = [
        ('professionnel', 'Score Professionnel'),
        ('imc', 'Score IMC'),
        ('nutritionnel', 'Score Nutritionnel'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    score_type = models.CharField(
        max_length=20,
        choices=SCORE_TYPE_CHOICES,
        verbose_name='Type de score'
    )
    value = models.FloatField(verbose_name='Valeur')
    max_value = models.FloatField(default=100, verbose_name='Valeur maximale')
    details = models.JSONField(default=dict, blank=True, verbose_name='Détails')
    
    class Meta:
        verbose_name = 'Score'
        verbose_name_plural = 'Scores'
        ordering = ['-created_at']
        unique_together = ('user', 'score_type')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_score_type_display()}"
    
    @property
    def percentage(self):
        return (self.value / self.max_value) * 100

class Recommendation(TimeStampedModel):
    """Modèle pour les recommandations"""
    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(verbose_name='Description')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        verbose_name='Priorité'
    )
    is_completed = models.BooleanField(default=False, verbose_name='Complétée')
    
    class Meta:
        verbose_name = 'Recommandation'
        verbose_name_plural = 'Recommandations'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title
