from django.db import models
from typing import Dict

from myapp.plat.models import Plat


class Menu(models.Model):
    """ModÃ¨le Menu"""
    DIET_CATEGORIES = [
        ('high-protein', 'High Protein'),
        ('low-carb', 'Low Carb'),
        ('vegan', 'Vegan'),
        ('gluten-free', 'Sans Gluten'),
        ('autre', 'Autre'),
    ]
    
    id_menu = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_actif = models.BooleanField(default=True)
    diet_category = models.CharField(max_length=20, choices=DIET_CATEGORIES, default='autre', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    plats = models.ManyToManyField("plat.Plat", related_name="menus")

    def get_diet_category(self) -> str:
        """DÃ©termine automatiquement la catÃ©gorie de rÃ©gime basÃ©e sur les valeurs nutritionnelles"""
        valeurs = self.calculer_valeur_nutritionnelle_totale()
        
        # High-protein: protÃ©ine >= 35g
        if valeurs.get('proteines', 0) >= 35:
            return 'high-protein'
        
        # Low-carb: glucides <= 20g
        if valeurs.get('glucides', 0) <= 20:
            return 'low-carb'
        
        # Vegan: check description for vegan indicators
        desc_lower = (self.description or "").lower()
        if any(word in desc_lower for word in ['vegan', 'vÃ©gÃ©tal', 'sans produit animal', 'plant-based']):
            return 'vegan'
        
        # Gluten-free: check description
        if any(word in desc_lower for word in ['sans gluten', 'gluten-free', 'gluten free']):
            return 'gluten-free'
        
        return 'autre'
    
    def ajouter_plat(self, plat: Plat) -> None:
        """Ajoute un plat au menu"""
        self.plats.add(plat)
    
    def supprimer_plat(self, plat: Plat) -> None:
        """Supprime un plat du menu"""
        self.plats.remove(plat)
    
    def calculer_valeur_nutritionnelle_totale(self) -> Dict:
        """Calcule les valeurs nutritionnelles totales du menu"""
        #print(f"Calcul des valeurs nutritionnelles pour le menu '{self.nom}' (ID: {self.id_menu})")
        plats = self.plats.all()
        
        total = {
            'calories': 0,
            'proteines': 0,
            'glucides': 0,
            'lipides': 0,
            'fibres': 0,
            'prix': 0
        }
        
        for plat in plats:
            total['calories'] += plat.calorie
            total['proteines'] += plat.proteine
            total['glucides'] += plat.glucides
            total['lipides'] += plat.lipides
            total['fibres'] += plat.fibres
            total['prix'] += float(plat.prix)
            #print(f"  - {plat.nom}: {total['calories']:.0f} kcal, {total['proteines']:.0f}g prot, {total['glucides']:.0f}g gluc, {total['lipides']:.0f}g lip, {total['fibres']:.0f}g fib, {total['prix']:.2f}€")
        return total
    
    def __str__(self):
        return f"Menu: {self.nom}"