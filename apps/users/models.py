"""
Modèles pour l'app users
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    """Modèle utilisateur étendu"""
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('nutritionist', 'Nutritionniste'),
        ('admin', 'Administrateur'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Rôle'
    )
    bio = models.TextField(blank=True, verbose_name='Biographie')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Vérifiée'
    )
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.get_full_name() or self.username
