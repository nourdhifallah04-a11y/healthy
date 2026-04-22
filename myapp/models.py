from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from decimal import Decimal
from typing import Dict, List

# ========== IMPORTS CONSTANTES SCORING CENTRALISÃ‰ES ==========
try:
    from .score_constants import (
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


class UtilisateurManager(BaseUserManager):
    """Manager personnalisÃ© pour utiliser l'email comme identifiant"""

    def create_user(self, email: str, password: str = None, **extra_fields) -> "Utilisateur":
        """CrÃ©e un utilisateur avec un email unique"""
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None, **extra_fields) -> "Utilisateur":
        """CrÃ©e un superutilisateur"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)
    
class Utilisateur(AbstractUser):
    """ModÃ¨le utilisateur personnalisÃ©"""

    username = None  # On supprime le champ username
    email = models.EmailField(unique=True)

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]

    objects = UtilisateurManager()

    class Meta:
        db_table = "myapp_utilisateur"
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Client(models.Model):
    """ModÃ¨le Client"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='client')
    date_naissance = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
    
    def __str__(self):
        return f"Client: {self.utilisateur.nom} {self.utilisateur.prenom}"

class Administrateur(models.Model):
    """ModÃ¨le Administrateur"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='administrateur')
    role = models.CharField(max_length=50, default='admin')
    permissions = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"
    
    def __str__(self):
        return f"Admin: {self.utilisateur.nom} {self.utilisateur.prenom}"

class ProfilNutritionnel(models.Model):
    """Profil nutritionnel du client"""
    OBJECTIFS = [
        ('perte_poids', 'Perte de poids'),
        ('maintien', 'Maintien'),
        ('prise_muscle', 'Prise de muscle'),
        ('performance', 'Performance sportive'),
    ]
    
    NIVEAU_ACTIVITE = [
        ('sedentaire', 'SÃ©dentaire'),
        ('leger', 'LÃ©gÃ¨rement actif'),
        ('modere', 'ModÃ©rÃ©ment actif'),
        ('actif', 'TrÃ¨s actif'),
        ('extremement_actif', 'ExtrÃªmement actif'),
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculer_imc(self) -> float:
        """Calcule l'IMC du client"""
        taille_m = float(self.taille) / 100
        imc = float(self.poids) / (taille_m ** 2)
        return round(imc, 2)
    
    def calculer_bmr(self) -> float:
        """Calcule le mÃ©tabolisme de base (Formule de Harris-Benedict) selon le sexe"""
        poids_kg = float(self.poids)
        taille_cm = float(self.taille)
        age_ans = self.age
        
        # Formule de Harris-Benedict rÃ©visÃ©e (plus prÃ©cise que l'originale)
        if self.sexe == 'homme':
            # Formule pour homme
            bmr = 88.362 + (13.397 * poids_kg) + (4.799 * taille_cm) - (5.677 * age_ans)
        else:
            # Formule pour femme
            bmr = 447.593 + (9.247 * poids_kg) + (3.098 * taille_cm) - (4.330 * age_ans)
        
        return round(bmr, 2)
    
    def besoins_caloriques_journaliers(self) -> float:
        """Calcule les besoins caloriques journaliers basÃ©s sur le mÃ©tabolisme et l'activitÃ©"""
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
        """DÃ©termine la catÃ©gorie d'IMC du client"""
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
        Recommande des plats basÃ©s sur le statut IMC, allergies et restrictions alimentaires
        et les valeurs nutritionnelles
        
        Args:
            limite: Nombre maximal de plats Ã  recommander (dÃ©faut: 10)
        
        Returns:
            Liste des plats recommandÃ©s triÃ©e par score de recommandation
        """
        from django.db.models import F
        
        categorie_imc = self.determiner_categorie_imc()
        plats_disponibles = Plat.objects.filter(est_disponible=True)
        
        print(f"\n{'='*60}")
        print(f"RECOMMANDATION DE PLATS")
        print(f"{'='*60}")
        print(f"CatÃ©gorie IMC: {categorie_imc}")
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
        
        # Trier par score dÃ©croissant (les scores de 0 seront rejetÃ©s)
        plats_avec_score.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n{'='*60}")
        print(f"PLATS RECOMMANDÃ‰S (Score > 0)")
        print(f"{'='*60}\n")
        
        plats_recommandes = [item['plat'] for item in plats_avec_score[:limite] if item['score'] > 0]
        
        for i, item in enumerate(plats_avec_score[:limite], 1):
            if item['score'] > 0:
                print(f"{i}. {item['plat'].nom}: {item['score']:.2f}/100")
        
        print(f"\n{'='*60}\n")
        
        # Retourner les plats recommandÃ©s (uniquement ceux avec un score > 0)
        return plats_recommandes
    
    def __str__(self):
        return f"Profil de {self.client.utilisateur.nom}"

class Plat(models.Model):
    """ModÃ¨le Plat"""
    id_plat = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    calorie = models.FloatField(help_text="Calories en kcal")
    proteine = models.FloatField(help_text="ProtÃ©ines en grammes")
    glucides = models.FloatField(default=0, help_text="Glucides en grammes")
    lipides = models.FloatField(default=0, help_text="Lipides en grammes")
    fibres = models.FloatField(default=0, help_text="Fibres en grammes")
    prix = models.DecimalField(max_digits=10, decimal_places=3)
    est_disponible = models.BooleanField(default=True)
    isNew = models.BooleanField(default=False)
    image = models.ImageField(upload_to='plats/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def afficher_detail(self) -> Dict:
        """Affiche les dÃ©tails du plat"""
        return {
            'nom': self.nom,
            'calories': self.calorie,
            'proteines': self.proteine,
            'glucides': self.glucides,
            'lipides': self.lipides,
            'prix': str(self.prix)
        }
    
    def get_diet_categories(self) -> List[str]:
        """Retourne les catÃ©gories de rÃ©gime auxquelles appartient ce plat"""
        categories = []
        
        # High-protein: protÃ©ine >= 35g
        if self.proteine >= 35:
            categories.append('high-protein')
        
        # Low-carb: glucides <= 20g
        if self.glucides <= 20:
            categories.append('low-carb')
        
        # Vegan: check description for vegan indicators
        desc_lower = (self.description or "").lower()
        if any(word in desc_lower for word in ['vegan', 'vÃ©gÃ©tal', 'sans produit animal', 'plant-based']):
            categories.append('vegan')
        
        # Gluten-free: check description
        if any(word in desc_lower for word in ['sans gluten', 'gluten-free', 'gluten free']):
            categories.append('gluten-free')
        
        return categories if categories else ['autre']
    
    def calculer_score_nutritionnel(self) -> int:
        """Calcule un score nutritionnel de 0 Ã  100 basÃ© sur les valeurs nutritionnelles (optimisÃ© avec cache)"""
        # ClÃ© de cache basÃ©e sur les valeurs nutritionnelles du plat
        cache_key = f"score_{self.id_plat}_{self.calorie}_{self.proteine}_{self.fibres}_{self.lipides}"
        
        # VÃ©rifier le cache
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
        
        # Bonus/malus protÃ©ines
        if self.proteine > cfg['protein']['high_threshold']:
            score += cfg['protein']['high_bonus']
        elif self.proteine > cfg['protein']['medium_threshold']:
            score += cfg['protein']['medium_bonus']
        elif self.proteine < cfg['protein'].get('low_threshold', 10):
            # Malus pour plats trÃ¨s pauvres en protÃ©ines (ex: Riz Nature 4g)
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
        """Calcule un score de recommandation pour un plat basÃ© sur IMC, allergies, restrictions (optimisÃ©)"""
        # ClÃ© de cache
        cache_key = f"rec_{plat.id_plat}_{categorie_imc}_{allergies}_{restrictions}_{age}_{sexe}"
        cached = get_cached_score(cache_key)
        if cached is not None:
            return cached
        
        texte_plat = (plat.nom + " " + plat.description).lower()
        
        # Utiliser les constantes avec fallback
        dietary_res = DIETARY_RESTRICTIONS if DIETARY_RESTRICTIONS else {
            'vegetarien': {'keywords': ['viande', 'poulet', 'boeuf', 'poisson', 'saumon', 'thon', 'canard']},
            'vegane': {'keywords': ['viande', 'poulet', 'boeuf', 'poisson', 'oeuf', 'lait', 'fromage', 'beurre']},
            'sans gluten': {'keywords': ['blÃ©', 'gluten', 'pain', 'pate', 'biscuit', 'cereale']},
            'sans lactose': {'keywords': ['lait', 'fromage', 'beurre', 'creme', 'yaourt']}
        }
        
        # 1. VÃ©rifier allergies et restrictions
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
        
        # 2. Score basÃ© sur la catÃ©gorie IMC (0-100 directement)
        strategies = BMI_STRATEGIES if BMI_STRATEGIES else {}
        strategy = strategies.get(categorie_imc, strategies.get('normal', {}))
        strategy_score = Plat._score_by_strategy(plat, strategy)  # DÃ©jÃ  0-100 avec caps
        
        # 3. Ajouter bonus/malus d'Ã¢ge/sexe (max Â±15 pour rester dans [0,100])
        age_bonus = Plat._bonus_age_sexe(plat, age, sexe, categorie_imc)
        
        # Clamp le bonus Ã  -15 Ã  +15 pour Ã©viter dÃ©passer 100
        age_bonus = max(-15, min(15, age_bonus))
        
        # Score final avec validation post-calcul
        final_score = strategy_score + (age_bonus * 0.5)  # RÃ©duire impact bonus age
        
        # VALIDATION POST-CALCUL: Garantir score âˆˆ [0, 100]
        final_score = max(0, min(100, final_score))
        final_score = round(final_score, 2)
        set_cached_score(cache_key, final_score)
        
        return final_score
    
    @staticmethod
    def _score_by_strategy(plat: "Plat", strategy: Dict) -> float:
        """
        Calcule le score basÃ© sur une stratÃ©gie nutritionnelle.
        Chaque nutriment est capÃ© Ã  son max individuel.
        Score total max = 25 + 30 + 20 + 15 + 10 = 100 pts.

        Formule corrigÃ©e :
          - DÃ©gradation progressive (pas de cliff-edge binaire)
          - Caps individuels par nutriment (min(score, max_pts))
          - Validation finale : max(0, min(100, total))
        """
        scores = {}

        # === CALORIES (max 25 pts) ===
        cal_score = 0
        if 'calories_max' in strategy:
            cal_max = strategy['calories_max']
            if plat.calorie <= cal_max:
                cal_score = 25  # Parfait
            elif plat.calorie <= cal_max * 1.3:
                # DÃ©gradation linÃ©aire entre cal_max et cal_max*1.3
                ratio = (plat.calorie - cal_max) / (cal_max * 0.3)
                cal_score = max(5, int(25 - ratio * 20))
            else:
                cal_score = 0   # Trop calorique
        elif 'calories_range' in strategy:
            cal_min, cal_max = strategy['calories_range']
            if cal_min <= plat.calorie <= cal_max:
                cal_score = 25  # Parfait
            elif plat.calorie < cal_min:
                # Sous la plage : dÃ©gradation proportionnelle
                ratio = (cal_min - plat.calorie) / cal_min
                cal_score = max(5, int(25 - ratio * 20))
            else:
                # Sur la plage : dÃ©gradation proportionnelle
                ratio = (plat.calorie - cal_max) / cal_max
                cal_score = max(0, int(25 - ratio * 25))
        elif 'calories_min' in strategy:
            cal_min = strategy['calories_min']
            if plat.calorie >= cal_min:
                cal_score = 25  # Bon
            elif plat.calorie >= cal_min * 0.7:
                ratio = (cal_min - plat.calorie) / (cal_min * 0.3)
                cal_score = max(8, int(25 - ratio * 17))
            else:
                cal_score = 5   # TrÃ¨s insuffisant mais pas pÃ©nalitÃ© totale
        scores['calories'] = min(cal_score, 25)

        # === PROTÃ‰INES (max 30 pts) ===
        prot_score = 0
        if 'protein_range' in strategy:
            p_min, p_max = strategy['protein_range']
            if p_min <= plat.proteine <= p_max:
                prot_score = 30  # Parfait
            elif plat.proteine > p_max:
                # Plus que le max : lÃ©gÃ¨rement moins optimal mais pas pÃ©nalisÃ© fortement
                excess_ratio = (plat.proteine - p_max) / p_max
                prot_score = max(22, int(30 - excess_ratio * 10))
            elif plat.proteine >= p_min * 0.5:
                # Entre 50% et 100% du min : dÃ©gradation progressive
                ratio = (p_min - plat.proteine) / p_min
                prot_score = max(8, int(30 - ratio * 22))
            else:
                prot_score = 5   # TrÃ¨s faible mais pas 0 (pÃ©nalitÃ© dÃ©gradÃ©e)
        elif 'protein_min' in strategy:
            p_min = strategy['protein_min']
            if plat.proteine >= p_min:
                prot_score = 30  # Bon
            elif plat.proteine >= p_min * 0.6:
                ratio = (p_min - plat.proteine) / p_min
                prot_score = max(10, int(30 - ratio * 20))
            else:
                prot_score = 5   # TrÃ¨s faible mais pas 0
        scores['protein'] = min(prot_score, 30)

        # === GLUCIDES (max 20 pts) ===
        carbs_score = 0
        if 'carbs_max' in strategy:
            c_max = strategy['carbs_max']
            if plat.glucides <= c_max:
                carbs_score = 20  # Excellent
            elif plat.glucides <= c_max * 1.5:
                ratio = (plat.glucides - c_max) / (c_max * 0.5)
                carbs_score = max(5, int(20 - ratio * 15))
            else:
                carbs_score = 0   # Trop
        elif 'carbs_range' in strategy:
            c_min, c_max = strategy['carbs_range']
            if c_min <= plat.glucides <= c_max:
                carbs_score = 20  # Parfait
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
                fat_score = 15  # Excellent
            elif plat.lipides <= f_max * 1.5:
                ratio = (plat.lipides - f_max) / (f_max * 0.5)
                fat_score = max(5, int(15 - ratio * 10))
            else:
                fat_score = 0   # Trop gras
        elif 'fat_range' in strategy:
            f_min, f_max = strategy['fat_range']
            if f_min <= plat.lipides <= f_max:
                fat_score = 15  # Parfait
            elif plat.lipides < f_min:
                fat_score = 12  # LÃ©gÃ¨rement sous la plage = ok
            else:
                ratio = (plat.lipides - f_max) / f_max
                fat_score = max(0, int(15 - ratio * 15))
        scores['fat'] = min(fat_score, 15)

        # === FIBRES (max 10 pts) ===
        fiber_score = 0
        if 'fiber_range' in strategy:
            fib_min, fib_max = strategy['fiber_range']
            if fib_min <= plat.fibres <= fib_max:
                fiber_score = 10  # Parfait
            elif plat.fibres > fib_max:
                fiber_score = 8   # Plus de fibres que nÃ©cessaire = OK
            elif plat.fibres >= fib_min * 0.5:
                ratio = (fib_min - plat.fibres) / fib_min
                fiber_score = max(4, int(10 - ratio * 6))
            else:
                fiber_score = 3   # Insuffisant mais pas 0
        elif 'fiber_min' in strategy:
            fib_min = strategy['fiber_min']
            if plat.fibres >= fib_min:
                fiber_score = 10  # Bon
            elif plat.fibres >= fib_min * 0.5:
                ratio = (fib_min - plat.fibres) / fib_min
                fiber_score = max(4, int(10 - ratio * 6))
            else:
                fiber_score = 3   # Insuffisant mais pas 0
        scores['fiber'] = min(fiber_score, 10)

        # Total : max 25 + 30 + 20 + 15 + 10 = 100
        total = sum(scores.values())
        # VALIDATION POST-CALCUL : garantir score âˆˆ [0, 100]
        return max(0, min(100, total))


    @staticmethod
    def _bonus_age_sexe(plat: "Plat", age: int = None, sexe: str = None, imc_cat: str = 'normal') -> float:
        """
        Calcule un bonus intelligent basÃ© sur l'Ã¢ge, le sexe et les besoins nutritionnels spÃ©cifiques.
        
        Les bonus rÃ©compensent les plats qui correspondent aux besoins rÃ©els de chaque profil :
        - Jeunes: besoins Ã©nergÃ©tiques Ã©levÃ©s, croissance musculaire, glucides Ã©nergÃ©tiques
        - Adultes: Ã©quilibre nutritionnel optimalisÃ©
        - Seniors: protÃ©ines et fibres pour santÃ©, calories modÃ©rÃ©es
        """
        bonus = 0.0
        
        # Obtenir le profil d'Ã¢ge/sexe
        profile = get_age_gender_profile(age, sexe)
        if not profile:
            return 0.0
        
        # === BONUS Ã‰NERGÃ‰TIQUE (PRIMAIRE POUR JEUNES) ===
        energy_bonus = profile.get('energy_bonus', 0)
        
        # SUPER BONUS Ã‰NERGIE POUR JEUNES (< 20 ans)
        if age and age < 20:
            # Jeunes ont ABSOLUMENT BESOIN de calories et protÃ©ines
            if plat.calorie >= 650 and plat.proteine >= 40:
                # Profil musculaire/Ã©nergÃ©tique idÃ©al pour jeunes
                bonus += 30
            elif plat.calorie >= 550 and plat.proteine >= 35:
                # Bon profil Ã©nergÃ©tique
                bonus += 25
            elif plat.calorie >= 450 and plat.proteine >= 30:
                # Acceptable
                bonus += 15
            elif plat.calorie >= 350 and plat.proteine >= 20:
                # ModÃ©rÃ©
                bonus += 8
            elif plat.calorie < 300:
                # Insuffisant pour jeunes
                bonus -= 10
        elif plat.calorie >= profile.get('preferred_calories_min', 400):
            # Non-jeunes: approche par calories
            if plat.calorie <= profile.get('preferred_calories_max', 700):
                # Calories dans la plage idÃ©ale
                bonus += energy_bonus
            elif plat.calorie <= profile.get('preferred_calories_max', 700) + 200:
                # LÃ©gÃ¨rement au-dessus
                if age and age < 50:
                    bonus += energy_bonus * 0.5
                else:
                    bonus += energy_bonus * 0.2
            else:
                # Calories trÃ¨s hautes
                if age and age >= 50:
                    bonus -= 8  # Seniors: trop calorique
                else:
                    bonus -= 3  # Adultes: modÃ©rÃ©
        else:
            # Calories insuffisantes
            if age and age >= 50:
                bonus -= 2  # Seniors: c'est ok si lÃ©ger
            else:
                bonus -= 5  # Jeunes/adultes: besoin de calories
        
        # === BONUS PROTÃ‰INES (TRÃˆS IMPORTANT POUR JEUNES ET SENIORS) ===
        protein_bonus = profile.get('protein_bonus', 0)
        protein_min = profile.get('preferred_protein_min', 20)
        protein_max = profile.get('preferred_protein_max', 40)
        
        if plat.proteine >= protein_min:
            if plat.proteine <= protein_max + 15:  # Accepte un peu plus
                bonus += protein_bonus
            else:
                # ProtÃ©ines trÃ¨s Ã©levÃ©es (> 55g) - bon surtout pour jeunes/seniors
                if age and (age < 20 or age >= 50):
                    bonus += protein_bonus * 0.7
                else:
                    bonus += protein_bonus * 0.3
        elif plat.proteine >= protein_min - 5:
            # LÃ©gÃ¨rement au-dessous du min
            bonus += protein_bonus * 0.4
        else:
            # ProtÃ©ines insuffisantes
            bonus -= 8
        
        # === BONUS GLUCIDES POUR JEUNES (Ã‰NERGIE) ===
        if age and age < 20:
            # Jeunes ont BESOIN de glucides pour Ã©nergie
            if plat.glucides >= 30:
                bonus += 12  # Excellent
            elif plat.glucides >= 20:
                bonus += 8   # Bon
            elif plat.glucides >= 10:
                bonus += 4   # ModÃ©rÃ©
            elif plat.glucides < 5:
                # TrÃ¨s peu de glucides
                if plat.calorie >= 600 and plat.proteine >= 40:
                    # Profil fortement protÃ©inÃ©/calorique (ex: steak)
                    # C'est acceptable car fournit l'Ã©nergie par calories
                    bonus += 0   # Neutre, compensÃ© par bonus Ã©nergÃ©tique
                else:
                    # Manque d'Ã©nergie globale
                    bonus -= 5
        
        # === BONUS FIBRES (IMPORTANT POUR SENIORS) ===
        fiber_bonus = profile.get('fiber_bonus', 0)
        fiber_min = profile.get('preferred_fiber_min', 5)
        
        if plat.fibres >= fiber_min:
            if plat.fibres <= 15:
                bonus += fiber_bonus * (min(plat.fibres, 12) / 10)
            else:
                # Beaucoup de fibres - bon pour tous
                bonus += fiber_bonus
        elif age and age >= 50 and plat.fibres >= fiber_min - 2:
            # Seniors tolÃ©rent un peu moins de fibres
            bonus += fiber_bonus * 0.4
        elif age and age < 50 and plat.fibres >= 3:
            # Jeunes/adultes avec quelques fibres
            bonus += fiber_bonus * 0.2
        
        # === MALUS POUR LIPIDES TRÃˆS Ã‰LEVÃ‰S (SANS JUSTIFICATION) ===
        if plat.lipides > 40:
            if plat.proteine < 30:
                # Gras sans protÃ©ines justifie = malus fort
                bonus -= 10
            elif age and age < 20:
                # Jeunes en croissance peuvent tolÃ©rer
                bonus -= 2
            else:
                # Adultes/seniors: malus modÃ©rÃ©
                bonus -= 5
        elif plat.lipides > 25:
            if plat.proteine < 25:
                bonus -= 3
        
        # === BONUS Ã‰QUILIBRE GLOBAL POUR ADULTES ===
        if profile.get('prefer_balanced') and age and 20 <= age < 50:
            # Adultes apprÃ©cient l'Ã©quilibre macros
            if plat.calorie > 0:
                ratio_carbs = (plat.glucides * 4) / plat.calorie
                ratio_prot = (plat.proteine * 4) / plat.calorie
                ratio_lipides = (plat.lipides * 9) / plat.calorie
                
                if 0.30 <= ratio_carbs <= 0.60 and 0.20 <= ratio_prot <= 0.50 and 0.15 <= ratio_lipides <= 0.40:
                    bonus += 8
        
        # === BONUS SPÃ‰CIAL SENIOR: PLATS LÃ‰GERS MAIS NUTRITIFS ===
        if age and age >= 50:
            if plat.calorie <= 600 and plat.proteine >= 25 and plat.fibres >= 5:
                # Combinaison idÃ©ale pour senior
                bonus += 10
        
        return bonus
    
    # =========================================================================
    #  SCORE PROFESSIONNEL â€” RefactorisÃ©
    # =========================================================================
    #
    #  â•­â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•®
    #  â”‚  QUAND UTILISER calculer_score_professionnel() ?                     â”‚
    #  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
    #  â”‚  âœ” Quand vous disposez d'un ProfilNutritionnel COMPLET (taille,      â”‚
    #  â”‚    poids, Ã¢ge, sexe, niveau d'activitÃ©, objectif).                   â”‚
    #  â”‚  âœ” Pour des recommandations de haute prÃ©cision (ex : tableau de bord â”‚
    #  â”‚    professionnel diÃ©tÃ©tique, suivi mÃ©dical, app sportive).           â”‚
    #  â”‚  âœ” Quand vous voulez personnaliser via Harris-Benedict + ratios      â”‚
    #  â”‚    macros par objectif.                                              â”‚
    #  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
    #  â”‚  Ã€ NE PAS UTILISER POUR :                                            â”‚
    #  â”‚  âœ˜ Affichage rapide de tuiles plats         â†’ calculer_score_nutritionnel() â”‚
    #  â”‚  âœ˜ Recommandations basÃ©es seulement sur IMC â†’ calculer_score_recommendation()â”‚
    #  â”‚  âœ˜ Batch sur > 1000 plats sans cache        â†’ prÃ©fÃ©rer score IMC     â”‚
    #  â•°â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•¯
    # =========================================================================

    # --- Constantes (extraites pour lisibilitÃ© & testabilitÃ©) -----------------
    _PRO_FACTEURS_ACTIVITE = {
        'sedentaire': 1.2, 'leger': 1.375, 'modere': 1.55,
        'actif': 1.725, 'extremement_actif': 1.9,
    }
    _PRO_AJUSTEMENTS_OBJECTIF = {
        'perte_poids': 0.8, 'maintien': 1.0,
        'prise_muscle': 1.2, 'performance': 1.15,
    }
    _PRO_PROTEINES_G_PER_KG = {
        'perte_poids': 1.8, 'maintien': 1.2,
        'prise_muscle': 2.0, 'performance': 1.4,
    }
    _PRO_BESOINS_FIBRES = {
        'perte_poids': 35, 'maintien': 30,
        'prise_muscle': 28, 'performance': 25,
    }
    # PondÃ©rations totales : 25 + 30 + 15 + 15 + 10 + 5 = 100
    _PRO_MAX_POINTS = {
        'calories': 25, 'proteines': 30, 'glucides': 15,
        'lipides': 15, 'fibres': 10, 'age_sexe': 5,
    }

    # ------------------------------------------------------------------ HELPERS
    @staticmethod
    def _pro_check_restrictions(plat: "Plat", profil: "ProfilNutritionnel") -> bool:
        """Retourne True si le plat est INTERDIT (allergies / restrictions)."""
        texte = (plat.nom + " " + plat.description).lower()
        for source in (profil.allergies, profil.restrictions_alimentaires):
            if not source:
                continue
            for token in (t.strip().lower() for t in source.split(',')):
                if token and token in texte:
                    return True
        return False

    @staticmethod
    def _pro_calc_besoins(profil: "ProfilNutritionnel") -> Dict[str, float]:
        """Calcule les besoins personnalisÃ©s (calories, protÃ©ines, fibres)."""
        poids = float(profil.poids)
        taille = float(profil.taille)
        age = profil.age

        if profil.sexe == 'homme':
            bmr = 88.362 + (13.397 * poids) + (4.799 * taille) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * poids) + (3.098 * taille) - (4.330 * age)

        facteur = Plat._PRO_FACTEURS_ACTIVITE.get(profil.niveau_activite, 1.55)
        ajustement = Plat._PRO_AJUSTEMENTS_OBJECTIF.get(profil.objectif, 1.0)
        besoins_cal = bmr * facteur * ajustement

        besoins_prot = poids * Plat._PRO_PROTEINES_G_PER_KG.get(profil.objectif, 1.2)
        besoins_fib = Plat._PRO_BESOINS_FIBRES.get(profil.objectif, 30)

        return {
            'bmr': round(bmr, 2),
            'calories': round(besoins_cal, 2),
            'proteines': round(besoins_prot, 2),
            'fibres': float(besoins_fib),
        }

    @staticmethod
    def _pro_score_calories(plat: "Plat", categorie_imc: str) -> float:
        """Score calories (max 25) selon la catÃ©gorie IMC."""
        c = plat.calorie
        if categorie_imc == 'insuffisance_ponderale':
            if 800 <= c <= 1200:   return 25
            if 600 <= c < 800 or 1200 < c <= 1400: return 20
            if 400 <= c < 600:     return 12
            return max(0.0, 25 - abs(1000 - c) / 100)
        if categorie_imc == 'normal':
            if 400 <= c <= 800:    return 25
            if 300 <= c < 400 or 800 < c <= 900: return 18
            return max(0.0, 25 - abs(600 - c) / 50)
        if categorie_imc == 'surpoids':
            if 250 <= c <= 450:    return 25
            if 150 <= c < 250 or 450 < c <= 600: return 18
            if c <= 150 or 600 < c <= 750:       return 10
            return 5.0
        # ObÃ©sitÃ©
        if 200 <= c <= 350:        return 25
        if 150 <= c < 200 or 350 < c <= 450: return 18
        if c <= 150 or 450 < c <= 550:        return 8
        return 2.0

    @staticmethod
    def _pro_score_proteines(plat: "Plat", categorie_imc: str) -> float:
        """Score protÃ©ines (max 30)."""
        p = plat.proteine
        if categorie_imc == 'insuffisance_ponderale':
            if p >= 35: return 30
            if 25 <= p < 35: return 22
            if 15 <= p < 25: return 12
            return 5.0
        if categorie_imc == 'normal':
            if 20 <= p <= 35: return 30
            if 15 <= p < 20 or 35 < p <= 40: return 22
            if p < 15: return 8
            return 18.0
        if categorie_imc == 'surpoids':
            if 25 <= p <= 45: return 30
            if 20 <= p < 25 or 45 < p <= 50: return 22
            if 15 <= p < 20: return 12
            return 5.0
        # ObÃ©sitÃ© (prioritÃ© maximale aux protÃ©ines)
        if 30 <= p <= 50: return 30
        if 25 <= p < 30 or p > 50: return 24
        if 20 <= p < 25: return 16
        return 5.0

    @staticmethod
    def _pro_score_glucides(plat: "Plat", objectif: str) -> float:
        """Score glucides (max 15) selon l'objectif."""
        g = plat.glucides
        if objectif == 'perte_poids':
            if g <= 20: return 15
            if g <= 30: return 10
            if g <= 45: return 5
            return 0.0
        if objectif == 'performance':
            if 40 <= g <= 60: return 15
            if 30 <= g < 40 or 60 < g <= 75: return 10
            return 5.0
        # maintien / prise_muscle
        if 30 <= g <= 50: return 15
        if 20 <= g < 30 or 50 < g <= 60: return 10
        return 3.0

    @staticmethod
    def _pro_score_lipides(plat: "Plat", categorie_imc: str) -> float:
        """Score lipides (max 15)."""
        l = plat.lipides
        if categorie_imc in ('surpoids', 'obesite'):
            max_lip = 10 if categorie_imc == 'obesite' else 15
            if l <= max_lip * 0.7: return 15
            if l <= max_lip:       return 10
            if l <= max_lip * 1.5: return 5
            return 0.0
        # normal / insuffisance
        if 10 <= l <= 25: return 15
        if 5 <= l < 10 or 25 < l <= 30: return 10
        return 3.0

    @staticmethod
    def _pro_score_fibres(plat: "Plat", besoins_fibre_g: float) -> float:
        """Score fibres (max 10) basÃ© sur 1/3 des besoins journaliers."""
        seuil = besoins_fibre_g / 3
        if plat.fibres >= seuil:        return 10
        if plat.fibres >= seuil * 0.6:  return 7
        if plat.fibres >= seuil * 0.3:  return 3
        return 0.0

    @staticmethod
    def _pro_score_age_sexe(plat: "Plat", profil: "ProfilNutritionnel") -> float:
        """Bonus Ã¢ge/sexe (max 5)."""
        bonus = 0.0
        if profil.sexe == 'femme' and plat.calorie <= 700:
            bonus += 2
        elif profil.sexe == 'homme' and plat.proteine > 25:
            bonus += 2
        if profil.age < 25 and plat.calorie >= 600:
            bonus += 1.5
        elif profil.age >= 50 and plat.calorie <= 600 and plat.fibres > 5:
            bonus += 2
        return min(bonus, 5.0)

    @staticmethod
    def _pro_evaluation(score: float) -> str:
        if score >= 85: return "ðŸŒŸ EXCELLENT - TrÃ¨s recommandÃ©"
        if score >= 70: return "âœ… BON - RecommandÃ©"
        if score >= 55: return "âš ï¸ ACCEPTABLE - Peut Ãªtre inclus"
        if score >= 40: return "âŒ FAIBLE - Ã€ limiter"
        return "ðŸš« TRÃˆS FAIBLE - Non recommandÃ©"

    # --------------------------------------------------------- API PUBLIQUE
    @staticmethod
    def calculer_score_professionnel(plat: "Plat",
                                     profil: "ProfilNutritionnel",
                                     verbose: bool = False,
                                     return_details: bool = False):
        """
        Calcule un score de recommandation PROFESSIONNEL (0-100).

        MÃ©thodologie :
            1. Filtre allergies / restrictions  â†’ 0 immÃ©diat
            2. Calcul besoins personnalisÃ©s (Harris-Benedict + activitÃ© + objectif)
            3. 6 sous-scores pondÃ©rÃ©s (calories, protÃ©ines, glucides, lipides,
               fibres, Ã¢ge/sexe), chacun capÃ© individuellement
            4. Validation post-calcul : score âˆˆ [0, 100]
            5. Enregistrement dans le monitor (`score_monitor`) pour le dashboard

        Args:
            plat (Plat): Le plat Ã  Ã©valuer.
            profil (ProfilNutritionnel): Profil utilisateur complet requis.
            verbose (bool): Si True, affiche le breakdown dÃ©taillÃ© (debug).
            return_details (bool): Si True, retourne (score, details_dict).

        Returns:
            float | tuple[float, dict]: Score normalisÃ© [0, 100], ou tuple
            (score, dÃ©tails) si `return_details=True`.

        Examples:
            >>> score = Plat.calculer_score_professionnel(plat, profil)
            >>> score, details = Plat.calculer_score_professionnel(
            ...     plat, profil, return_details=True
            ... )
        """
        # Import tardif pour Ã©viter cycles & ne pas charger en cas d'absence
        try:
            from .score_monitoring import score_monitor
        except Exception:
            score_monitor = None

        ctx = {'plat_id': getattr(plat, 'id_plat', None),
               'plat_nom': plat.nom,
               'client_nom': str(profil.client.utilisateur),
               'client_id': profil.client.utilisateur.id,
               'profil_objectif': profil.objectif}

        # --- 1. Restrictions / allergies -----------------------------------
        if Plat._pro_check_restrictions(plat, profil):
            if verbose:
                print(f"âŒ {plat.nom}: allergie/restriction â†’ score 0")
            if score_monitor:
                score_monitor.record('professionnel', 0.0,
                                     client_id=profil.client.utilisateur.id,
                                     plat_id=plat.id_plat,
                                     context={**ctx, 'reason': 'restriction'})
            return (0.0, {'reason': 'restriction_violee'}) if return_details else 0.0

        # --- 2. Besoins personnalisÃ©s --------------------------------------
        besoins = Plat._pro_calc_besoins(profil)
        categorie_imc = profil.determiner_categorie_imc()

        # --- 3. Sous-scores (chacun capÃ© Ã  son max individuel) -------------
        details = {
            'calories':  min(Plat._pro_score_calories(plat, categorie_imc),
                             Plat._PRO_MAX_POINTS['calories']),
            'proteines': min(Plat._pro_score_proteines(plat, categorie_imc),
                             Plat._PRO_MAX_POINTS['proteines']),
            'glucides':  min(Plat._pro_score_glucides(plat, profil.objectif),
                             Plat._PRO_MAX_POINTS['glucides']),
            'lipides':   min(Plat._pro_score_lipides(plat, categorie_imc),
                             Plat._PRO_MAX_POINTS['lipides']),
            'fibres':    min(Plat._pro_score_fibres(plat, besoins['fibres']),
                             Plat._PRO_MAX_POINTS['fibres']),
            'age_sexe':  min(Plat._pro_score_age_sexe(plat, profil),
                             Plat._PRO_MAX_POINTS['age_sexe']),
        }

        # --- 4. Total + VALIDATION POST-CALCUL -----------------------------
        total = sum(details.values())
        score_final = round(max(0.0, min(100.0, total)), 2)

        # --- 5. Logging verbeux (optionnel) -------------------------------
        if verbose:
            print(f"\n{'='*70}\nSCORE PROFESSIONNEL â€” {plat.nom}\n{'='*70}")
            print(f"IMC: {profil.calculer_imc():.1f} ({categorie_imc.upper()}) | "
                  f"Objectif: {profil.objectif}")
            print(f"Besoins: {besoins['calories']:.0f} kcal/j, "
                  f"{besoins['proteines']:.0f}g prot, "
                  f"{besoins['fibres']:.0f}g fibres")
            for k, v in details.items():
                maxp = Plat._PRO_MAX_POINTS[k]
                print(f"  â€¢ {k:10s}: {v:5.2f}/{maxp}")
            print(f"  {'â”€'*30}\n  TOTAL: {score_final:.2f}/100")
            print(f"  â†’ {Plat._pro_evaluation(score_final)}\n{'='*70}\n")

        # --- 6. Monitoring -------------------------------------------------
        if score_monitor:
            score_monitor.record('professionnel', score_final,
                                 client_id=profil.client.utilisateur.id,
                                 plat_id=plat.id_plat,
                                 context={
                **ctx,
                'imc_cat': categorie_imc,
                'breakdown': details,
            })

        if return_details:
            return score_final, {
                'score': score_final,
                'breakdown': details,
                'besoins': besoins,
                'categorie_imc': categorie_imc,
                'evaluation': Plat._pro_evaluation(score_final),
            }
        return score_final

    def __str__(self):
        return f"{self.nom} - {self.calorie} kcal"

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
    plats = models.ManyToManyField("Plat", related_name="menus")

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

class Commande(models.Model):
    """ModÃ¨le Commande"""
    STATUTS = [
        ('panier', 'Panier'),
        ('en_attente', 'En attente'),
        ('confirmee', 'ConfirmÃ©e'),
        ('en_preparation', 'En prÃ©paration'),
        ('livree', 'LivrÃ©e'),
        ('annulee', 'AnnulÃ©e'),
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
            # GÃ©rer les deux cas: menu ou plat
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

class SystemeIA(models.Model):
    """SystÃ¨me d'intelligence artificielle pour les recommandations"""
    nom = models.CharField(max_length=100, default="Nutrition AI")
    version = models.CharField(max_length=20)
    est_actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def analyser_preferences(self, client: "Client") -> Dict:
        """Analyse les prÃ©fÃ©rences alimentaires du client basÃ©es sur l'historique"""
        commandes = client.commandes.filter(statut='livree')
        plats_frequents = []
        categories_populaires = {}
        
        for commande in commandes:
            for ligne in commande.lignecommande_set.all():
                if ligne.menu:
                    for plat in ligne.menu.plats.all():
                        plats_frequents.append(plat)
                        
                        # CatÃ©gorisation par calories
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
        """Recommande des menus personnalisÃ©s basÃ©s sur le profil et l'historique"""
        profil = client.profil_nutritionnel
        menus_actifs = Menu.objects.filter(est_actif=True)
        
        # Analyser les prÃ©fÃ©rences
        preferences = self.analyser_preferences(client)
        
        # Calculer le score pour chaque menu
        menus_scores = []
        for menu in menus_actifs:
            valeurs = menu.calculer_valeur_nutritionnelle_totale()
            score = 0
            
            # Score basÃ© sur l'objectif nutritionnel
            if profil.objectif == 'perte_poids' and valeurs['calories'] < 600:
                score += 30
            elif profil.objectif == 'prise_muscle' and valeurs['proteines'] > 30:
                score += 30
            elif profil.objectif == 'performance' and valeurs['calories'] > 700:
                score += 30
                
            # Score basÃ© sur les prÃ©fÃ©rences historiques
            if preferences.get('preferences'):
                if valeurs['calories'] < 400 and preferences['preferences'].get('leger', 0) > 0:
                    score += 20
                elif valeurs['calories'] > 700 and preferences['preferences'].get('energetique', 0) > 0:
                    score += 20
                    
            # Score nutritionnel
            score_nutritionnel = (valeurs['proteines'] * 2 - valeurs['lipides']) / 100
            score += max(0, min(20, score_nutritionnel))
            
            menus_scores.append((menu, score))
        
        # Trier par score (dÃ©croissant) et retourner les meilleurs
        menus_scores.sort(key=lambda x: x[1], reverse=True)
        return [menu for menu, score in menus_scores[:limite]]
    
    def __str__(self):
        return f"{self.nom} v{self.version}"
