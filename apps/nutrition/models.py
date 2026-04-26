"""
Modèles pour l'app nutrition
"""
from django.db import models
from apps.core.models import TimeStampedModel
from django.contrib.auth import get_user_model
from decimal import Decimal
from typing import Dict, List
from apps.users.models import Client

User = get_user_model()

# ========== IMPORTS CONSTANTES SCORING CENTRALISÉES ==========
try:
    from myapp.score_constants import (
        get_cached_score, 
        set_cached_score, 
        clear_score_cache,
        get_age_gender_profile,
        SIMPLE_SCORE_CONFIG, 
        BMI_STRATEGIES, 
        DIETARY_RESTRICTIONS,
        AGE_GENDER_PROFILES
    )
except ImportError:
    # Fallback si score_constants.py n'existe pas encore
    def get_cached_score(key, func=None):
        return func() if func else None
    def set_cached_score(key, value):
        return value
    def clear_score_cache():
        pass
    SIMPLE_SCORE_CONFIG = {}
    BMI_STRATEGIES = {}
    DIETARY_RESTRICTIONS = {}


class Food(TimeStampedModel):
    """Modèle pour les aliments"""
    name = models.CharField(max_length=200, unique=True, verbose_name='Nom')
    calories = models.IntegerField(verbose_name='Calories (kcal/100g)')
    proteins = models.FloatField(verbose_name='Protéines (g/100g)')
    carbs = models.FloatField(verbose_name='Glucides (g/100g)')
    fats = models.FloatField(verbose_name='Lipides (g/100g)')
    fiber = models.FloatField(default=0, verbose_name='Fibres (g/100g)')
    
    class Meta:
        verbose_name = 'Aliment'
        verbose_name_plural = 'Aliments'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NutritionalProfile(TimeStampedModel):
    """Profil nutritionnel utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Utilisateur')
    age = models.IntegerField(verbose_name='Âge')
    height = models.IntegerField(verbose_name='Taille (cm)')
    weight = models.FloatField(verbose_name='Poids (kg)')
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Masculin'), ('F', 'Féminin')],
        verbose_name='Genre'
    )
    activity_level = models.CharField(
        max_length=20,
        choices=[
            ('sedentary', 'Sédentaire'),
            ('lightly_active', 'Légèrement actif'),
            ('moderately_active', 'Modérément actif'),
            ('very_active', 'Très actif'),
        ],
        default='moderately_active',
        verbose_name='Niveau d\'activité'
    )
    daily_calorie_goal = models.IntegerField(verbose_name='Apport calorique quotidien')
    
    class Meta:
        verbose_name = 'Profil nutritionnel'
        verbose_name_plural = 'Profils nutritionnels'
    
    def __str__(self):
        return f"Profil de {self.user.username}"


class ProfilNutritionnel(models.Model):
    """Profil nutritionnel du client"""
    OBJECTIFS = [
        ('perte_poids', 'Perte de poids'),
        ('maintien', 'Maintien'),
        ('prise_muscle', 'Prise de muscle'),
        ('performance', 'Performance sportive'),
    ]
    
    NIVEAU_ACTIVITE = [
        ('sedentaire', 'Sédentaire'),
        ('leger', 'Légèrement actif'),
        ('modere', 'Modérément actif'),
        ('actif', 'Très actif'),
        ('extremement_actif', 'Extrêmement actif'),
    ]
    
    SEXE_CHOICES = [
        ('homme', 'Homme'),
        ('femme', 'Femme'),
    ]
    
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='profil_nutritionnel')
    age = models.IntegerField()
    taille = models.DecimalField(max_digits=5, decimal_places=2, help_text="Taille en cm")
    poids = models.DecimalField(max_digits=5, decimal_places=2, help_text="Poids en kg")
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES, blank=True)
    allergies = models.TextField(blank=True, help_text="Allergies alimentaires")
    objectif = models.CharField(max_length=20, choices=OBJECTIFS)
    restrictions_alimentaires = models.TextField(blank=True)
    niveau_activite = models.CharField(max_length=20, choices=NIVEAU_ACTIVITE, default='modere')
    donnees_sante_sensibles = models.BooleanField(default=False, help_text="Autorisation de traiter les données de santé sensibles")
    learning_collectif = models.BooleanField(default=False, help_text="Autorisation de participer à l'apprentissage collectif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculer_imc(self) -> float:
        """Calcule l'IMC du client"""
        taille_m = float(self.taille) / 100
        imc = float(self.poids) / (taille_m ** 2)
        return round(imc, 2)
    
    def calculer_bmr(self) -> float:
        """Calcule le métabolisme de base (Formule de Harris-Benedict) selon le sexe"""
        poids_kg = float(self.poids)
        taille_cm = float(self.taille)
        age_ans = self.age
        
        # Formule de Harris-Benedict révisée (plus précise que l'originale)
        if self.sexe == 'homme':
            # Formule pour homme
            bmr = 88.362 + (13.397 * poids_kg) + (4.799 * taille_cm) - (5.677 * age_ans)
        else:
            # Formule pour femme
            bmr = 447.593 + (9.247 * poids_kg) + (3.098 * taille_cm) - (4.330 * age_ans)
        
        return round(bmr, 2)
    
    def besoins_caloriques_journaliers(self) -> float:
        """Calcule les besoins caloriques journaliers basés sur le métabolisme et l'activité"""
        bmr = self.calculer_bmr()
        facteurs = {
            'sedentaire': 1.2,
            'leger': 1.375,
            'modere': 1.55,
            'actif': 1.725,
            'extremement_actif': 1.9
        }
        
        facteur = facteurs.get(self.niveau_activite, 1.55)
        
        # Ajustement selon l'objectif
        if self.objectif == 'perte_poids':
            facteur -= 0.2
        elif self.objectif == 'prise_muscle':
            facteur += 0.2
            
        return round(bmr * facteur, 2)
    
    def determiner_categorie_imc(self) -> str:
        """Détermine la catégorie d'IMC du client"""
        imc = self.calculer_imc()
        if imc < 18.5:
            return 'insuffisance_ponderale'
        elif imc < 25:
            return 'normal'
        elif imc < 30:
            return 'surpoids'
        else:
            return 'obesite'
    
    def recommander_plats(self, limite: int = 10) -> List["Plat"]:
        """
        Recommande des plats basés sur le statut IMC, allergies et restrictions alimentaires
        et les valeurs nutritionnelles
        
        Args:
            limite: Nombre maximal de plats à recommander (défaut: 10)
        
        Returns:
            Liste des plats recommandés triée par score de recommandation
        """
        from django.db.models import F
        
        categorie_imc = self.determiner_categorie_imc()
        plats_disponibles = Plat.objects.filter(est_disponible=True)
        
        print(f"\n{'='*60}")
        print(f"RECOMMANDATION DE PLATS")
        print(f"{'='*60}")
        print(f"Catégorie IMC: {categorie_imc}")
        print(f"Allergies: {self.allergies if self.allergies else 'Aucune'}")
        print(f"Restrictions: {self.restrictions_alimentaires if self.restrictions_alimentaires else 'Aucune'}")
        print(f"{'='*60}\n")
        
        plats_avec_score = []
        
        for plat in plats_disponibles:
            score = Plat.calculer_score_recommendation(
                plat, 
                categorie_imc,
                allergies=self.allergies,
                restrictions=self.restrictions_alimentaires,
                age=self.age,
                sexe=self.sexe
            )
            plats_avec_score.append({
                'plat': plat,
                'score': score
            })
            print(f"Plat: {plat.nom:30} | Score: {score:6.2f} | Cal: {plat.calorie:5.0f} | Prot: {plat.proteine:5.1f}g")
        
        # Trier par score décroissant (les scores de 0 seront rejetés)
        plats_avec_score.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n{'='*60}")
        print(f"PLATS RECOMMANDÉS (Score > 0)")
        print(f"{'='*60}\n")
        
        plats_recommandes = [item['plat'] for item in plats_avec_score[:limite] if item['score'] > 0]
        
        for i, item in enumerate(plats_avec_score[:limite], 1):
            if item['score'] > 0:
                print(f"{i}. {item['plat'].nom}: {item['score']:.2f}/100")
        
        print(f"\n{'='*60}\n")
        
        # Retourner les plats recommandés (uniquement ceux avec un score > 0)
        return plats_recommandes
    
    def __str__(self):
        return f"Profil de {self.client.utilisateur.nom}"


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
        """Calcule un score nutritionnel de 0 à 100 basé sur les valeurs nutritionnelles (optimisé avec cache)"""
        # Clé de cache basée sur les valeurs nutritionnelles du plat
        cache_key = f"score_{self.id_plat}_{self.calorie}_{self.proteine}_{self.fibres}_{self.lipides}"
        
        # Vérifier le cache
        cached_score = get_cached_score(cache_key)
        if cached_score is not None:
            return cached_score
        
        cfg = SIMPLE_SCORE_CONFIG if SIMPLE_SCORE_CONFIG else {
            'base': 50,
            'protein': {'high_threshold': 30, 'high_bonus': 20, 'medium_threshold': 20, 'medium_bonus': 10},
            'calories': {'high_threshold': 800, 'high_malus': 20, 'medium_threshold': 600, 'medium_malus': 10},
            'fiber': {'high_threshold': 10, 'high_bonus': 15, 'medium_threshold': 5, 'medium_bonus': 8},
            'fat': {'high_threshold': 30, 'high_malus': 15, 'medium_threshold': 20, 'medium_malus': 8}
        }
        score = cfg['base']
        
        # Bonus/malus protéines
        if self.proteine > cfg['protein']['high_threshold']:
            score += cfg['protein']['high_bonus']
        elif self.proteine > cfg['protein']['medium_threshold']:
            score += cfg['protein']['medium_bonus']
        elif self.proteine < cfg['protein'].get('low_threshold', 10):
            score -= cfg['protein'].get('low_malus', 10)

        # Malus calories
        if self.calorie > cfg['calories']['high_threshold']:
            score -= cfg['calories']['high_malus']
        elif self.calorie > cfg['calories']['medium_threshold']:
            score -= cfg['calories']['medium_malus']
        
        # Bonus fibres
        if self.fibres > cfg['fiber']['high_threshold']:
            score += cfg['fiber']['high_bonus']
        elif self.fibres > cfg['fiber']['medium_threshold']:
            score += cfg['fiber']['medium_bonus']
        
        # Malus lipides
        if self.lipides > cfg['fat']['high_threshold']:
            score -= cfg['fat']['high_malus']
        elif self.lipides > cfg['fat']['medium_threshold']:
            score -= cfg['fat']['medium_malus']
        
        # Clamp le score entre 0 et 100 et mettre en cache
        final_score = max(0, min(100, score))
        set_cached_score(cache_key, final_score)
        
        return final_score
    
    @staticmethod
    def calculer_score_recommendation(plat: "Plat", categorie_imc: str, 
                                     allergies: str = "", restrictions: str = "",
                                     age: int = None, sexe: str = None, debug: bool = False) -> float:
        """Calcule un score de recommandation pour un plat basé sur IMC, allergies, restrictions"""
        # Clé de cache
        cache_key = f"rec_{plat.id_plat}_{categorie_imc}_{allergies}_{restrictions}_{age}_{sexe}"
        cached = get_cached_score(cache_key)
        if cached is not None:
            return cached
        
        texte_plat = (plat.nom + " " + plat.description).lower()
        
        # Utiliser les constantes avec fallback
        dietary_res = DIETARY_RESTRICTIONS if DIETARY_RESTRICTIONS else {
            'vegetarien': {'keywords': ['viande', 'poulet', 'boeuf', 'poisson', 'saumon', 'thon', 'canard']},
            'vegane': {'keywords': ['viande', 'poulet', 'boeuf', 'poisson', 'oeuf', 'lait', 'fromage', 'beurre']},
            'sans gluten': {'keywords': ['blé', 'gluten', 'pain', 'pate', 'biscuit', 'cereale']},
            'sans lactose': {'keywords': ['lait', 'fromage', 'beurre', 'creme', 'yaourt']}
        }
        
        # 1. Vérifier allergies et restrictions
        if allergies:
            for allergie in [a.strip().lower() for a in allergies.split(',') if a.strip()]:
                if allergie in texte_plat:
                    set_cached_score(cache_key, 0.0)
                    return 0.0
        
        if restrictions:
            for restriction in [r.strip().lower() for r in restrictions.split(',') if r.strip()]:
                if restriction in dietary_res:
                    keywords = dietary_res[restriction]['keywords']
                    if any(kw in texte_plat for kw in keywords):
                        set_cached_score(cache_key, 0.0)
                        return 0.0
        
        # 2. Score basé sur la catégorie IMC
        strategies = BMI_STRATEGIES if BMI_STRATEGIES else {}
        strategy = strategies.get(categorie_imc, strategies.get('normal', {}))
        strategy_score = Plat._score_by_strategy(plat, strategy)
        
        # 3. Ajouter bonus/malus d'âge/sexe
        age_bonus = Plat._bonus_age_sexe(plat, age, sexe, categorie_imc)
        age_bonus = max(-15, min(15, age_bonus))
        
        # Score final
        final_score = strategy_score + (age_bonus * 0.5)
        final_score = max(0, min(100, final_score))
        final_score = round(final_score, 2)
        set_cached_score(cache_key, final_score)
        
        return final_score
    
    @staticmethod
    def _score_by_strategy(plat: "Plat", strategy: Dict) -> float:
        """Calcule le score basé sur une stratégie nutritionnelle"""
        scores = {}

        # === CALORIES (max 25 pts) ===
        cal_score = 0
        if 'calories_max' in strategy:
            cal_max = strategy['calories_max']
            if plat.calorie <= cal_max:
                cal_score = 25
            elif plat.calorie <= cal_max * 1.3:
                ratio = (plat.calorie - cal_max) / (cal_max * 0.3)
                cal_score = max(5, int(25 - ratio * 20))
            else:
                cal_score = 0
        elif 'calories_range' in strategy:
            cal_min, cal_max = strategy['calories_range']
            if cal_min <= plat.calorie <= cal_max:
                cal_score = 25
            elif plat.calorie < cal_min:
                ratio = (cal_min - plat.calorie) / cal_min
                cal_score = max(5, int(25 - ratio * 20))
            else:
                ratio = (plat.calorie - cal_max) / cal_max
                cal_score = max(0, int(25 - ratio * 25))
        elif 'calories_min' in strategy:
            cal_min = strategy['calories_min']
            if plat.calorie >= cal_min:
                cal_score = 25
            elif plat.calorie >= cal_min * 0.7:
                ratio = (cal_min - plat.calorie) / (cal_min * 0.3)
                cal_score = max(8, int(25 - ratio * 17))
            else:
                cal_score = 5
        scores['calories'] = min(cal_score, 25)

        # === PROTÉINES (max 30 pts) ===
        prot_score = 0
        if 'protein_range' in strategy:
            p_min, p_max = strategy['protein_range']
            if p_min <= plat.proteine <= p_max:
                prot_score = 30
            elif plat.proteine > p_max:
                excess_ratio = (plat.proteine - p_max) / p_max
                prot_score = max(22, int(30 - excess_ratio * 10))
            elif plat.proteine >= p_min * 0.5:
                ratio = (p_min - plat.proteine) / p_min
                prot_score = max(8, int(30 - ratio * 22))
            else:
                prot_score = 5
        elif 'protein_min' in strategy:
            p_min = strategy['protein_min']
            if plat.proteine >= p_min:
                prot_score = 30
            elif plat.proteine >= p_min * 0.6:
                ratio = (p_min - plat.proteine) / p_min
                prot_score = max(10, int(30 - ratio * 20))
            else:
                prot_score = 5
        scores['protein'] = min(prot_score, 30)

        # === GLUCIDES (max 20 pts) ===
        carbs_score = 0
        if 'carbs_max' in strategy:
            c_max = strategy['carbs_max']
            if plat.glucides <= c_max:
                carbs_score = 20
            elif plat.glucides <= c_max * 1.5:
                ratio = (plat.glucides - c_max) / (c_max * 0.5)
                carbs_score = max(5, int(20 - ratio * 15))
            else:
                carbs_score = 0
        elif 'carbs_range' in strategy:
            c_min, c_max = strategy['carbs_range']
            if c_min <= plat.glucides <= c_max:
                carbs_score = 20
            elif plat.glucides < c_min:
                ratio = (c_min - plat.glucides) / c_min
                carbs_score = max(8, int(20 - ratio * 12))
            else:
                ratio = (plat.glucides - c_max) / c_max
                carbs_score = max(5, int(20 - ratio * 15))
        scores['carbs'] = min(carbs_score, 20)

        # === LIPIDES (max 15 pts) ===
        fat_score = 0
        if 'fat_max' in strategy:
            f_max = strategy['fat_max']
            if plat.lipides <= f_max:
                fat_score = 15
            elif plat.lipides <= f_max * 1.5:
                ratio = (plat.lipides - f_max) / (f_max * 0.5)
                fat_score = max(5, int(15 - ratio * 10))
            else:
                fat_score = 0
        elif 'fat_range' in strategy:
            f_min, f_max = strategy['fat_range']
            if f_min <= plat.lipides <= f_max:
                fat_score = 15
            elif plat.lipides < f_min:
                fat_score = 12
            else:
                ratio = (plat.lipides - f_max) / f_max
                fat_score = max(0, int(15 - ratio * 15))
        scores['fat'] = min(fat_score, 15)

        # === FIBRES (max 10 pts) ===
        fiber_score = 0
        if 'fiber_range' in strategy:
            fib_min, fib_max = strategy['fiber_range']
            if fib_min <= plat.fibres <= fib_max:
                fiber_score = 10
            elif plat.fibres > fib_max:
                fiber_score = 8
            elif plat.fibres >= fib_min * 0.5:
                ratio = (fib_min - plat.fibres) / fib_min
                fiber_score = max(4, int(10 - ratio * 6))
            else:
                fiber_score = 3
        elif 'fiber_min' in strategy:
            fib_min = strategy['fiber_min']
            if plat.fibres >= fib_min:
                fiber_score = 10
            elif plat.fibres >= fib_min * 0.5:
                ratio = (fib_min - plat.fibres) / fib_min
                fiber_score = max(4, int(10 - ratio * 6))
            else:
                fiber_score = 3
        scores['fiber'] = min(fiber_score, 10)

        total = sum(scores.values())
        return max(0, min(100, total))

    @staticmethod
    def _bonus_age_sexe(plat: "Plat", age: int = None, sexe: str = None, imc_cat: str = 'normal') -> float:
        """Calcule un bonus basé sur l'âge, le sexe et les besoins nutritionnels"""
        bonus = 0.0
        
        profile = get_age_gender_profile(age, sexe) if 'get_age_gender_profile' in dir() else {}
        if not profile:
            return 0.0
        
        energy_bonus = profile.get('energy_bonus', 0)
        
        # SUPER BONUS ÉNERGIE POUR JEUNES (< 20 ans)
        if age and age < 20:
            if plat.calorie >= 650 and plat.proteine >= 40:
                bonus += 30
            elif plat.calorie >= 550 and plat.proteine >= 35:
                bonus += 25
            elif plat.calorie >= 450 and plat.proteine >= 30:
                bonus += 15
            elif plat.calorie >= 350 and plat.proteine >= 20:
                bonus += 8
            elif plat.calorie < 300:
                bonus -= 10
        elif plat.calorie >= profile.get('preferred_calories_min', 400):
            if plat.calorie <= profile.get('preferred_calories_max', 700):
                bonus += energy_bonus
            elif plat.calorie <= profile.get('preferred_calories_max', 700) + 200:
                if age and age < 50:
                    bonus += energy_bonus * 0.5
                else:
                    bonus += energy_bonus * 0.2
            else:
                if age and age >= 50:
                    bonus -= 8
                else:
                    bonus -= 3
        else:
            if age and age >= 50:
                bonus -= 2
            else:
                bonus -= 5
        
        return bonus
    
    def __str__(self):
        return f"{self.nom} - {self.calorie} kcal"


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
    plats = models.ManyToManyField("Plat", related_name="menus")

    def get_diet_category(self) -> str:
        """Détermine automatiquement la catégorie de régime basée sur les valeurs nutritionnelles"""
        valeurs = self.calculer_valeur_nutritionnelle_totale()
        
        # High-protein: protéine >= 35g
        if valeurs.get('proteines', 0) >= 35:
            return 'high-protein'
        
        # Low-carb: glucides <= 20g
        if valeurs.get('glucides', 0) <= 20:
            return 'low-carb'
        
        # Vegan: check description for vegan indicators
        desc_lower = (self.description or "").lower()
        if any(word in desc_lower for word in ['vegan', 'végétal', 'sans produit animal', 'plant-based']):
            return 'vegan'
        
        # Gluten-free: check description
        if any(word in desc_lower for word in ['sans gluten', 'gluten-free', 'gluten free']):
            return 'gluten-free'
        
        return 'autre'

    def ajouter_plat(self, plat: "Plat") -> None:
        """Ajoute un plat au menu"""
        self.plats.add(plat)
    
    def supprimer_plat(self, plat: "Plat") -> None:
        """Supprime un plat du menu"""
        self.plats.remove(plat)
    
    def calculer_valeur_nutritionnelle_totale(self) -> Dict:
        """Calcule les valeurs nutritionnelles totales du menu"""
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
            
        return total
    
    def __str__(self):
        return f"Menu: {self.nom}"
