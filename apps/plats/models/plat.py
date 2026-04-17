"""
Modèle Plat - Représentation d'un plat du menu
"""
from typing import Dict, List
from django.db import models


class Plat(models.Model):
    """Modèle Plat"""
    id_plat = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    calorie = models.FloatField(help_text="Calories en kcal")
    proteine = models.FloatField(help_text="Protéines en grammes")
    glucides = models.FloatField(default=0, help_text="Glucides en grammes")
    lipides = models.FloatField(default=0, help_text="Lipides en grammes")
    fibres = models.FloatField(default=0, help_text="Fibres en grammes")
    prix = models.DecimalField(max_digits=10, decimal_places=3)
    est_disponible = models.BooleanField(default=True)
    isNew = models.BooleanField(default=False)
    image = models.ImageField(upload_to='plats/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "plats_plat"
        verbose_name = "Plat"
        verbose_name_plural = "Plats"
        indexes = [
            models.Index(fields=['est_disponible']),
            models.Index(fields=['isNew']),
            models.Index(fields=['prix']),
        ]
    
    def afficher_detail(self) -> Dict:
        """Affiche les détails du plat"""
        return {
            'nom': self.nom,
            'calories': self.calorie,
            'proteines': self.proteine,
            'glucides': self.glucides,
            'lipides': self.lipides,
            'prix': str(self.prix)
        }
    
    def get_diet_categories(self) -> List[str]:
        """Retourne les catégories de régime auxquelles appartient ce plat"""
        categories = []
        
        # High-protein: protéine >= 35g
        if self.proteine >= 35:
            categories.append('high-protein')
        
        # Low-carb: glucides <= 20g
        if self.glucides <= 20:
            categories.append('low-carb')
        
        # Vegan: check description for vegan indicators
        desc_lower = (self.description or "").lower()
        if any(word in desc_lower for word in ['vegan', 'végétal', 'sans produit animal', 'plant-based']):
            categories.append('vegan')
        
        # Gluten-free: check description
        if any(word in desc_lower for word in ['sans gluten', 'gluten-free', 'gluten free']):
            categories.append('gluten-free')
        
        return categories if categories else ['autre']
    
    def calculer_score_nutritionnel(self) -> int:
        """Calcule un score nutritionnel de 0 à 100 basé sur les valeurs nutritionnelles"""
        score = 50  # Score de base
        
        # Bonus pour les protéines (important pour la satiété et la musculature)
        if self.proteine > 30:
            score += 20
        elif self.proteine > 20:
            score += 10
            
        # Malus pour les calories élevées
        if self.calorie > 800:
            score -= 20
        elif self.calorie > 600:
            score -= 10
            
        # Bonus pour les fibres (satiété et santé digestive)
        if self.fibres > 10:
            score += 15
        elif self.fibres > 5:
            score += 8
            
        # Malus pour les lipides saturés
        if self.lipides > 30:
            score -= 15
        elif self.lipides > 20:
            score -= 8
            
        return max(0, min(100, score))
    
    @staticmethod
    def calculer_score_recommendation(plat: "Plat", categorie_imc: str, 
                                     allergies: str = "", restrictions: str = "",
                                     age: int = None, sexe: str = None) -> float:
        """
        Calcule un score de recommandation pour un plat basé sur la catégorie IMC, 
        allergies, restrictions alimentaires, âge et sexe
        """
        # Vérifier les allergies et restrictions alimentaires
        texte_plat = (plat.nom + " " + plat.description).lower()
        
        print(f"\n  [CALCUL SCORE] Plat: {plat.nom}")
        print(f"  Valeurs: Cal={plat.calorie:.0f} | Prot={plat.proteine:.1f}g | Gluc={plat.glucides:.1f}g | Lip={plat.lipides:.1f}g | Fib={plat.fibres:.1f}g")
        
        # Vérifier les allergies
        if allergies:
            allergies_list = [a.strip().lower() for a in allergies.split(',')]
            for allergie in allergies_list:
                if allergie and allergie in texte_plat:
                    print(f"  ❌ ALLERGIE DÉTECTÉE: {allergie}")
                    return 0.0
        
        # Vérifier les restrictions
        if restrictions:
            restrictions_list = [r.strip().lower() for r in restrictions.split(',')]
            for restriction in restrictions_list:
                if restriction:
                    if restriction in texte_plat:
                        print(f"  ❌ RESTRICTION VIOLÉE: {restriction}")
                        return 0.0
                    
                    # Cas spécifiques de restrictions communes
                    if restriction == 'vegetarien' and any(x in texte_plat for x in ['viande', 'poulet', 'boeuf', 'poisson', 'saumon', 'thon']):
                        print(f"  ❌ RESTRICTION VIOLÉE: {restriction} (détecté viande/poisson)")
                        return 0.0
                    elif restriction == 'vegane' and any(x in texte_plat for x in ['viande', 'poulet', 'boeuf', 'poisson', 'oeuf', 'lait', 'fromage', 'beurre']):
                        print(f"  ❌ RESTRICTION VIOLÉE: {restriction} (détecté produit animal)")
                        return 0.0
                    elif restriction == 'sans gluten' and any(x in texte_plat for x in ['blé', 'gluten', 'pain', 'pate', 'biscuit', 'cereale']):
                        print(f"  ❌ RESTRICTION VIOLÉE: {restriction} (détecté gluten)")
                        return 0.0
                    elif restriction == 'sans lactose' and any(x in texte_plat for x in ['lait', 'fromage', 'beurre', 'creme', 'yaourt']):
                        print(f"  ❌ RESTRICTION VIOLÉE: {restriction} (détecté lactose)")
                        return 0.0
        
        print(f"  ✓ Pas d'allergie/restriction")
        score = 0.0
        
        if categorie_imc == 'insuffisance_ponderale':
            print(f"  📊 Catégorie: INSUFFISANCE PONDÉRALE")
            bonus_cal = min((plat.calorie / 1000) * 25, 25)
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f}")
            
            bonus_prot = min((plat.proteine / 40) * 25, 25)
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f}")
            
            bonus_gluc = min((plat.glucides / 50) * 20, 20)
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f}")
            
            bonus_lip = min((plat.lipides / 30) * 15, 15)
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f}")
            
            bonus_fib = min((plat.fibres / 10) * 15, 15)
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f}")
        
        elif categorie_imc == 'normal':
            print(f"  📊 Catégorie: NORMAL")
            if 400 <= plat.calorie <= 800:
                bonus_cal = 20
            elif 300 <= plat.calorie <= 900:
                bonus_cal = 15
            elif plat.calorie <= 200 or plat.calorie > 1000:
                bonus_cal = 5
            else:
                bonus_cal = 10
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f}")
            
            if 20 <= plat.proteine <= 35:
                bonus_prot = 25
            elif 15 <= plat.proteine <= 40:
                bonus_prot = 18
            elif plat.proteine > 40:
                bonus_prot = 12
            else:
                bonus_prot = 5
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f}")
            
            if 30 <= plat.glucides <= 50:
                bonus_gluc = 20
            elif 20 <= plat.glucides <= 60:
                bonus_gluc = 15
            else:
                bonus_gluc = 5
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f}")
            
            if 10 <= plat.lipides <= 25:
                bonus_lip = 15
            elif 5 <= plat.lipides <= 30:
                bonus_lip = 10
            else:
                bonus_lip = 3
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f}")
            
            if 5 <= plat.fibres <= 12:
                bonus_fib = 20
            elif plat.fibres > 3:
                bonus_fib = 12
            else:
                bonus_fib = 5
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f}")
        
        elif categorie_imc == 'surpoids':
            print(f"  📊 Catégorie: SURPOIDS")
            if plat.calorie <= 500:
                bonus_cal = 30
            elif plat.calorie <= 700:
                bonus_cal = 20
            elif plat.calorie <= 900:
                bonus_cal = 10
            else:
                bonus_cal = 2
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f}")
            
            if 25 <= plat.proteine <= 40:
                bonus_prot = 30
            elif 20 <= plat.proteine <= 45:
                bonus_prot = 22
            elif plat.proteine >= 15:
                bonus_prot = 15
            else:
                bonus_prot = 5
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f}")
            
            if plat.glucides <= 30:
                bonus_gluc = 18
            elif plat.glucides <= 45:
                bonus_gluc = 12
            elif plat.glucides <= 60:
                bonus_gluc = 6
            else:
                bonus_gluc = 1
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f}")
            
            if plat.lipides <= 15:
                bonus_lip = 20
            elif plat.lipides <= 20:
                bonus_lip = 14
            elif plat.lipides <= 30:
                bonus_lip = 8
            else:
                bonus_lip = 2
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f}")
            
            if 8 <= plat.fibres <= 15:
                bonus_fib = 22
            elif plat.fibres >= 5:
                bonus_fib = 15
            else:
                bonus_fib = 5
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f}")
        
        elif categorie_imc == 'obesite':
            print(f"  📊 Catégorie: OBÉSITÉ")
            if plat.calorie <= 350:
                bonus_cal = 35
            elif plat.calorie <= 450:
                bonus_cal = 25
            elif plat.calorie <= 600:
                bonus_cal = 12
            else:
                bonus_cal = 1
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f}")
            
            if 30 <= plat.proteine <= 50:
                bonus_prot = 35
            elif 25 <= plat.proteine <= 55:
                bonus_prot = 25
            elif plat.proteine >= 20:
                bonus_prot = 15
            else:
                bonus_prot = 3
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f}")
            
            if plat.glucides <= 20:
                bonus_gluc = 20
            elif plat.glucides <= 35:
                bonus_gluc = 12
            elif plat.glucides <= 50:
                bonus_gluc = 5
            else:
                bonus_gluc = 1
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f}")
            
            if plat.lipides <= 10:
                bonus_lip = 25
            elif plat.lipides <= 15:
                bonus_lip = 15
            elif plat.lipides <= 25:
                bonus_lip = 8
            else:
                bonus_lip = 2
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f}")
            
            if 10 <= plat.fibres <= 20:
                bonus_fib = 25
            elif plat.fibres >= 6:
                bonus_fib = 16
            else:
                bonus_fib = 4
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f}")
        
        # Facteurs d'âge et de sexe
        print(f"  👤 Facteurs personnels: Âge={age} ans, Sexe={sexe}")
        bonus_age_sexe = 0.0
        
        if sexe == 'femme':
            bonus_age_sexe += 2
            if categorie_imc in ['normal', 'insuffisance_ponderale']:
                if plat.calorie > 700:
                    bonus_age_sexe -= 3
            print(f"    • Genre: Femme +{2:.1f}")
        
        elif sexe == 'homme':
            bonus_age_sexe += 1
            if plat.proteine > 25:
                bonus_age_sexe += 2
            print(f"    • Genre: Homme +{1 + (2 if plat.proteine > 25 else 0):.1f}")
        
        if age:
            if age < 20:
                bonus_age_sexe += min((plat.calorie / 1000) * 3, 3)
                print(f"    • Âge < 20 ans: +{min((plat.calorie / 1000) * 3, 3):.2f}")
            elif age >= 50:
                if plat.calorie < 600:
                    bonus_age_sexe += 2
                if plat.fibres > 5:
                    bonus_age_sexe += 1
                print(f"    • Âge >= 50 ans: +{(2 if plat.calorie < 600 else 0) + (1 if plat.fibres > 5 else 0):.2f}")
        
        score += bonus_age_sexe
        
        score_final = round(score, 2)
        print(f"  ✅ Score final (avec facteurs personnels): {score_final}/100\n")
        return score_final
    
    def __str__(self):
        return f"{self.nom} - {self.calorie} kcal"
