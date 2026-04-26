"""
Modèles pour l'app ai (Intelligence Artificielle)
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.users.models import Client
from apps.nutrition.models import Plat, Menu
from typing import Dict, List


class SystemeIA(models.Model):
    """Système d'intelligence artificielle pour les recommandations"""
    nom = models.CharField(max_length=100, default="Nutrition AI")
    version = models.CharField(max_length=20)
    est_actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Système IA"
        verbose_name_plural = "Systèmes IA"
    
    def analyser_preferences(self, client: "Client") -> Dict:
        """Analyse les préférences alimentaires du client basées sur l'historique"""
        from apps.orders.models import Commande
        
        commandes = Commande.objects.filter(client=client, statut='livree')
        plats_frequents = []
        categories_populaires = {}
        
        for commande in commandes:
            for ligne in commande.lignecommande_set.all():
                if ligne.menu:
                    for plat in ligne.menu.plats.all():
                        plats_frequents.append(plat)
                        
                        # Catégorisation par calories
                        if plat.calorie < 400:
                            categorie = 'leger'
                        elif plat.calorie < 700:
                            categorie = 'modere'
                        else:
                            categorie = 'energetique'
                            
                        categories_populaires[categorie] = categories_populaires.get(categorie, 0) + 1
        
        return {
            'plats_frequents': plats_frequents,
            'preferences': categories_populaires
        }
    
    def recommander_menus(self, client: "Client", limite: int = 5) -> List["Menu"]:
        """Recommande des menus personnalisés basés sur le profil et l'historique"""
        profil = client.profil_nutritionnel
        menus_actifs = Menu.objects.filter(est_actif=True)
        
        # Analyser les préférences
        preferences = self.analyser_preferences(client)
        
        # Calculer le score pour chaque menu
        menus_scores = []
        for menu in menus_actifs:
            valeurs = menu.calculer_valeur_nutritionnelle_totale()
            score = 0
            
            # Score basé sur l'objectif nutritionnel
            if profil.objectif == 'perte_poids' and valeurs['calories'] < 600:
                score += 30
            elif profil.objectif == 'prise_muscle' and valeurs['proteines'] > 30:
                score += 30
            elif profil.objectif == 'performance' and valeurs['calories'] > 700:
                score += 30
                
            # Score basé sur les préférences historiques
            if preferences.get('preferences'):
                if valeurs['calories'] < 400 and preferences['preferences'].get('leger', 0) > 0:
                    score += 20
                elif valeurs['calories'] > 700 and preferences['preferences'].get('energetique', 0) > 0:
                    score += 20
                    
            # Score nutritionnel
            score_nutritionnel = (valeurs['proteines'] * 2 - valeurs['lipides']) / 100
            score += max(0, min(20, score_nutritionnel))
            
            menus_scores.append((menu, score))
        
        # Trier par score (décroissant) et retourner les meilleurs
        menus_scores.sort(key=lambda x: x[1], reverse=True)
        return [menu for menu, score in menus_scores[:limite]]
    
    def __str__(self):
        return f"{self.nom} v{self.version}"
