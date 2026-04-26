"""
Modèles pour l'app orders
"""
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.nutrition.models import Food, Plat, Menu
from apps.users.models import Client
from django.contrib.auth import get_user_model
from decimal import Decimal
from typing import Dict

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


# ===== MODÈLES ISSUS DE MYAPP =====

class Commande(models.Model):
    """Modèle Commande (issu de myapp)"""
    STATUTS = [
        ('panier', 'Panier'),
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    
    id_commande = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes')
    date = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=20, choices=STATUTS, default='panier')
    total = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    adresse_livraison = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    def valider_commande(self) -> bool:
        """Valide la commande et change son statut"""
        if self.statut == 'panier':
            self.statut = 'confirmee'
            self.save()
            return True
        return False
    
    def calculer_total(self) -> Decimal:
        """Calcule le total de la commande"""
        lignes = self.lignecommande_set.all()
        total = sum(ligne.sous_total for ligne in lignes)
        self.total = total
        self.save()
        return total
    
    def calculer_nutrition_totale(self) -> Dict:
        """Calcule les valeurs nutritionnelles totales de la commande"""
        total_calories = 0
        total_proteines = 0
        total_glucides = 0
        total_lipides = 0
        
        for ligne in self.lignecommande_set.all():
            # Gérer les deux cas: menu ou plat
            if ligne.menu:
                # Si c'est un menu, calculer les valeurs nutritionnelles totales
                valeurs = ligne.menu.calculer_valeur_nutritionnelle_totale()
                total_calories += valeurs.get('calories', 0) * ligne.quantite
                total_proteines += valeurs.get('proteines', 0) * ligne.quantite
                total_glucides += valeurs.get('glucides', 0) * ligne.quantite
                total_lipides += valeurs.get('lipides', 0) * ligne.quantite
            elif ligne.plat:
                # Si c'est un plat, utiliser ses valeurs directement
                total_calories += ligne.plat.calorie * ligne.quantite
                total_proteines += ligne.plat.proteine * ligne.quantite
                total_glucides += ligne.plat.glucides * ligne.quantite
                total_lipides += ligne.plat.lipides * ligne.quantite
        
        return {
            'calories': total_calories,
            'proteines': total_proteines,
            'glucides': total_glucides,
            'lipides': total_lipides
        }
    
    def __str__(self):
        return f"Commande #{self.id_commande} - {self.client.utilisateur.nom}"


class LigneCommande(models.Model):
    """Ligne de commande - peut contenir soit un Menu soit un Plat"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True)
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, null=True, blank=True)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=3)
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
    
    def get_item(self):
        """Retourne l'article (Menu ou Plat)"""
        return self.menu if self.menu else self.plat
    
    def get_item_name(self):
        """Retourne le nom de l'article"""
        if self.menu:
            return self.menu.nom
        elif self.plat:
            return self.plat.nom
        return "Article inconnu"
    
    def get_item_type(self):
        """Retourne le type d'article (menu ou plat)"""
        return 'menu' if self.menu else 'plat'
    
    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
    
    def __str__(self):
        item_name = self.get_item_name()
        return f"{self.commande.id_commande} - {item_name} x{self.quantite}"
