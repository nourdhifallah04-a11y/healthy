"""
Modèle Commande - Commande d'un client
"""
from typing import Dict
from decimal import Decimal
from django.db import models
from django.utils import timezone
from apps.users.models import Client


class Commande(models.Model):
    """Modèle Commande"""
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
    
    class Meta:
        db_table = "commande_commande"
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['client', 'statut']),
            models.Index(fields=['date']),
        ]
    
    def valider_commande(self) -> bool:
        """Valide la commande et change son statut"""
        if self.statut == 'panier':
            self.statut = 'confirmee'
            self.save()
            return True
        return False
    
    def calculer_total(self) -> Decimal:
        """Calcule le total de la commande"""
        from .ligne_commande import LigneCommande
        lignes = LigneCommande.objects.filter(commande=self)
        total = sum(ligne.sous_total for ligne in lignes)
        self.total = total
        self.save()
        return total
    
    def calculer_nutrition_totale(self) -> Dict:
        """Calcule les valeurs nutritionnelles totales de la commande"""
        from .ligne_commande import LigneCommande
        
        total_calories = 0
        total_proteines = 0
        total_glucides = 0
        total_lipides = 0
        
        # Optimize with select_related to avoid N+1 queries
        lignes = LigneCommande.objects.filter(
            commande=self
        ).select_related('menu', 'plat')
        
        for ligne in lignes:
            if ligne.menu:
                valeurs = ligne.menu.calculer_valeur_nutritionnelle_totale()
                total_calories += valeurs.get('calories', 0) * ligne.quantite
                total_proteines += valeurs.get('proteines', 0) * ligne.quantite
                total_glucides += valeurs.get('glucides', 0) * ligne.quantite
                total_lipides += valeurs.get('lipides', 0) * ligne.quantite
            elif ligne.plat:
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
