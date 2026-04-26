"""
Modèles de base pour toutes les apps
"""
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """Modèle abstrait avec timestamps"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

class SoftDeleteModel(TimeStampedModel):
    """Modèle avec soft delete"""
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Supprimé le")
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete"""
        self.deleted_at = timezone.now()
        self.save()
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None

class BaseQuerySet(models.QuerySet):
    """QuerySet personnalisé"""
    def active(self):
        """Retourne les objets non supprimés"""
        return self.filter(deleted_at__isnull=True)
    
    def deleted(self):
        """Retourne les objets supprimés"""
        return self.filter(deleted_at__isnull=False)

class BaseManager(models.Manager):
    """Manager personnalisé"""
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def deleted(self):
        return self.get_queryset().deleted()
