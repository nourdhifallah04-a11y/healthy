"""
Modèle Menu - Menu composé de plusieurs plats
"""
from typing import Dict
from django.db import models
from .plat import Plat


class Menu(models.Model):
    """Modèle Menu"""
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
    plats = models.ManyToManyField(Plat, related_name="menus", through="CompositionMenu")

    class Meta:
        db_table = "plats_menu"
        verbose_name = "Menu"
        verbose_name_plural = "Menus"
        indexes = [
            models.Index(fields=['est_actif']),
            models.Index(fields=['diet_category']),
            models.Index(fields=['date_debut', 'date_fin']),
        ]

    def get_diet_category(self) -> str:
        """Détermine automatiquement la catégorie de régime basée sur les valeurs nutritionnelles"""
        valeurs = self.calculer_valeur_nutritionnelle_totale()
        
        if valeurs.get('proteines', 0) >= 35:
            return 'high-protein'
        
        if valeurs.get('glucides', 0) <= 20:
            return 'low-carb'
        
        desc_lower = (self.description or "").lower()
        if any(word in desc_lower for word in ['vegan', 'végétal', 'sans produit animal', 'plant-based']):
            return 'vegan'
        
        if any(word in desc_lower for word in ['sans gluten', 'gluten-free', 'gluten free']):
            return 'gluten-free'
        
        return 'autre'

    def ajouter_plat(self, plat: Plat, quantite: int = 1):
        """Ajoute un plat au menu avec gestion des quantités"""
        from .composition_menu import CompositionMenu
        composition, created = CompositionMenu.objects.get_or_create(
            menu=self,
            plat=plat,
            defaults={'quantite': quantite}
        )
        if not created:
            composition.quantite += quantite
            composition.save()
        return composition
    
    def supprimer_plat(self, plat: Plat) -> None:
        """Supprime un plat du menu"""
        from .composition_menu import CompositionMenu
        CompositionMenu.objects.filter(menu=self, plat=plat).delete()
    
    def calculer_valeur_nutritionnelle_totale(self) -> Dict:
        """Calcule les valeurs nutritionnelles totales du menu"""
        from .composition_menu import CompositionMenu
        
        compositions = CompositionMenu.objects.filter(menu=self)
        
        total = {
            'calories': 0,
            'proteines': 0,
            'glucides': 0,
            'lipides': 0,
            'fibres': 0,
            'prix': 0
        }
        
        for comp in compositions:
            total['calories'] += comp.plat.calorie * comp.quantite
            total['proteines'] += comp.plat.proteine * comp.quantite
            total['glucides'] += comp.plat.glucides * comp.quantite
            total['lipides'] += comp.plat.lipides * comp.quantite
            total['fibres'] += comp.plat.fibres * comp.quantite
            total['prix'] += float(comp.plat.prix) * comp.quantite
            
        return total
    
    def __str__(self):
        return f"Menu: {self.nom}"
