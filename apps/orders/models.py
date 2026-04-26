"""
Modèles pour l'app orders
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.nutrition.models import Food
from django.contrib.auth import get_user_model

User = get_user_model()

class CartItem(TimeStampedModel):
    """Modèle pour un article du panier"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    food = models.ForeignKey(Food, on_delete=models.CASCADE, verbose_name='Aliment')
    quantity = models.FloatField(default=1, verbose_name='Quantité (g)')
    
    class Meta:
        verbose_name = 'Article du panier'
        verbose_name_plural = 'Articles du panier'
        unique_together = ('user', 'food')
    
    def __str__(self):
        return f"{self.user.username} - {self.food.name}"
    
    @property
    def total_calories(self):
        return (self.food.calories * self.quantity) / 100

class Order(TimeStampedModel):
    """Modèle pour une commande"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('preparing', 'En préparation'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix total')
    delivery_address = models.TextField(verbose_name='Adresse de livraison')
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commande #{self.id} - {self.user.username}"

class OrderItem(TimeStampedModel):
    """Modèle pour un article dans une commande"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Commande')
    food = models.ForeignKey(Food, on_delete=models.PROTECT, verbose_name='Aliment')
    quantity = models.FloatField(verbose_name='Quantité (g)')
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Prix unitaire')
    
    class Meta:
        verbose_name = 'Article de commande'
        verbose_name_plural = 'Articles de commande'
    
    def __str__(self):
        return f"{self.order.id} - {self.food.name}"
