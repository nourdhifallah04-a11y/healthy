"""
Modèle LigneCommande - Ligne de commande
"""
from decimal import Decimal
from django.db import models
from .commande import Commande
from apps.plats.models import Plat, Menu


class LigneCommande(models.Model):
    """Ligne de commande - peut contenir soit un Menu soit un Plat"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True)
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, null=True, blank=True)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=3)
    
    class Meta:
        db_table = "commande_lignecommande"
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
        indexes = [
            models.Index(fields=['commande']),
            models.Index(fields=['menu']),
            models.Index(fields=['plat']),
        ]
    
    def get_item(self):
        """Retourne l'article (Menu ou Plat)"""
        return self.menu or self.plat
    
    def get_item_name(self):
        """Retourne le nom de l'article"""
        item = self.get_item()
        return item.nom if item else "Article inconnu"
    
    def get_item_type(self):
        """Retourne le type d'article (menu ou plat)"""
        return 'menu' if self.menu else 'plat' if self.plat else 'unknown'
    
    @property
    def sous_total(self) -> Decimal:
        """Calcule le sous-total de la ligne"""
        return self.quantite * self.prix_unitaire
    
    def __str__(self):
        item_name = self.get_item_name()
        return f"{self.commande.id_commande} - {item_name} x{self.quantite}"
