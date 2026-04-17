"""
Modèle CompositionMenu - Table de liaison entre Menu et Plat
"""
from django.db import models
from .plat import Plat
from .menu import Menu


class CompositionMenu(models.Model):
    """Table de liaison entre Menu et Plat"""
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ['menu', 'plat']
        db_table = "plats_compositionmenu"
        verbose_name = "Composition du menu"
        verbose_name_plural = "Compositions des menus"
    
    def __str__(self):
        return f"{self.menu.nom} - {self.plat.nom} x{self.quantite}"
