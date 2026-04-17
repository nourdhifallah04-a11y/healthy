from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from decimal import Decimal
from typing import Dict, List


class UtilisateurManager(BaseUserManager):
    """Manager personnalisé pour utiliser l'email comme identifiant"""

    def create_user(self, email: str, password: str = None, **extra_fields) -> "Utilisateur":
        """Crée un utilisateur avec un email unique"""
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None, **extra_fields) -> "Utilisateur":
        """Crée un superutilisateur"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)
    
class Utilisateur(AbstractUser):
    """Modèle utilisateur personnalisé"""

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
    """Modèle Client"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='client')
    date_naissance = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
    
    def __str__(self):
        return f"Client: {self.utilisateur.nom} {self.utilisateur.prenom}"

class Administrateur(models.Model):
    """Modèle Administrateur"""
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
        
        Stratégies par catégorie IMC:
        - Insuffisance pondérale: Calories élevées, protéines modérées
        - Normal: Équilibre optimal entre tous les nutriments
        - Surpoids: Faibles calories, protéines élevées, lipides bas, fibres élevées
        - Obésité: Très faibles calories, protéines très élevées, très faibles lipides
        
        Facteurs d'âge et de sexe:
        - Les femmes ont des besoins caloriques et en fer plus spécifiques
        - Les hommes ont généralement des besoins protéiques plus élevés
        - Les jeunes ont des besoins énergétiques supérieurs
        
        Args:
            plat: Instance du modèle Plat
            categorie_imc: Catégorie d'IMC ('insuffisance_ponderale', 'normal', 'surpoids', 'obesite')
            allergies: Chaîne contenant les allergies du client (ex: "arachide, lactose")
            restrictions: Chaîne contenant les restrictions alimentaires (ex: "végétarien, sans gluten")
            age: Âge du client (optionnel)
            sexe: Sexe du client ('homme', 'femme') (optionnel)
        
        Returns:
            Score de recommandation (0-100), retourne 0 si allergie/restriction détectée
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
                    return 0.0  # Score nul si allergie détectée
        
        # Vérifier les restrictions
        if restrictions:
            restrictions_list = [r.strip().lower() for r in restrictions.split(',')]
            for restriction in restrictions_list:
                if restriction:
                    # Restreint si le texte du plat le mentionne
                    if restriction in texte_plat:
                        print(f"  ❌ RESTRICTION VIOLÉE: {restriction}")
                        return 0.0  # Score nul si restriction violée
                    
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
        
        print(f"  ✓ Pas d'allergie/restriction")
        score = 0.0
        
        if categorie_imc == 'insuffisance_ponderale':
            print(f"  📊 Catégorie: INSUFFISANCE PONDÉRALE")
            # Pour insuffisance pondérale: favoriser calories, protéines, glucides
            # Bonus calories (1000 kcal = max bonus)
            bonus_cal = min((plat.calorie / 1000) * 25, 25)
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f} (idéal: 1000 kcal)")
            
            # Bonus protéines (40g = max bonus)
            bonus_prot = min((plat.proteine / 40) * 25, 25)
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f} (idéal: 40g)")
            
            # Bonus glucides (50g = max bonus)
            bonus_gluc = min((plat.glucides / 50) * 20, 20)
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f} (idéal: 50g)")
            
            # Bonus lipides modérés (30g = max bonus)
            bonus_lip = min((plat.lipides / 30) * 15, 15)
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f} (idéal: 30g)")
            
            # Bonus fibres (10g = max bonus)
            bonus_fib = min((plat.fibres / 10) * 15, 15)
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f} (idéal: 10g)")
        
        elif categorie_imc == 'normal':
            print(f"  📊 Catégorie: NORMAL")
            # Équilibre optimal
            # Score de base: calories modérées (500-700 kcal idéal)
            if 400 <= plat.calorie <= 800:
                bonus_cal = 20
            elif 300 <= plat.calorie <= 900:
                bonus_cal = 15
            elif plat.calorie <= 200 or plat.calorie > 1000:
                bonus_cal = 5
            else:
                bonus_cal = 10
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f} (idéal: 400-800 kcal)")
            
            # Protéines bonnes (20-35g idéal)
            if 20 <= plat.proteine <= 35:
                bonus_prot = 25
            elif 15 <= plat.proteine <= 40:
                bonus_prot = 18
            elif plat.proteine > 40:
                bonus_prot = 12
            else:
                bonus_prot = 5
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f} (idéal: 20-35g)")
            
            # Glucides équilibrés (30-50g idéal)
            if 30 <= plat.glucides <= 50:
                bonus_gluc = 20
            elif 20 <= plat.glucides <= 60:
                bonus_gluc = 15
            else:
                bonus_gluc = 5
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f} (idéal: 30-50g)")
            
            # Lipides modérés (10-25g idéal)
            if 10 <= plat.lipides <= 25:
                bonus_lip = 15
            elif 5 <= plat.lipides <= 30:
                bonus_lip = 10
            else:
                bonus_lip = 3
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f} (idéal: 10-25g)")
            
            # Fibres bonnes (5-12g idéal)
            if 5 <= plat.fibres <= 12:
                bonus_fib = 20
            elif plat.fibres > 3:
                bonus_fib = 12
            else:
                bonus_fib = 5
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f} (idéal: 5-12g)")
        
        elif categorie_imc == 'surpoids':
            print(f"  📊 Catégorie: SURPOIDS")
            # Faibles calories, protéines élevées, lipides bas, fibres élevées
            # Malus calories élevées (500 kcal max)
            if plat.calorie <= 500:
                bonus_cal = 30
            elif plat.calorie <= 700:
                bonus_cal = 20
            elif plat.calorie <= 900:
                bonus_cal = 10
            else:
                bonus_cal = 2
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f} (max: 500 kcal)")
            
            # Bonus protéines élevées (25-40g idéal)
            if 25 <= plat.proteine <= 40:
                bonus_prot = 30
            elif 20 <= plat.proteine <= 45:
                bonus_prot = 22
            elif plat.proteine >= 15:
                bonus_prot = 15
            else:
                bonus_prot = 5
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f} (idéal: 25-40g)")
            
            # Malus glucides (limiter à 30-40g)
            if plat.glucides <= 30:
                bonus_gluc = 18
            elif plat.glucides <= 45:
                bonus_gluc = 12
            elif plat.glucides <= 60:
                bonus_gluc = 6
            else:
                bonus_gluc = 1
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f} (max: 30g)")
            
            # Malus lipides (max 15g idéal)
            if plat.lipides <= 15:
                bonus_lip = 20
            elif plat.lipides <= 20:
                bonus_lip = 14
            elif plat.lipides <= 30:
                bonus_lip = 8
            else:
                bonus_lip = 2
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f} (max: 15g)")
            
            # Bonus fibres (8-15g idéal)
            if 8 <= plat.fibres <= 15:
                bonus_fib = 22
            elif plat.fibres >= 5:
                bonus_fib = 15
            else:
                bonus_fib = 5
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f} (idéal: 8-15g)")
        
        elif categorie_imc == 'obesite':
            print(f"  📊 Catégorie: OBÉSITÉ")
            # Très faibles calories, protéines très élevées, très faibles lipides
            # Malus calories très strictes (≤ 400 kcal)
            if plat.calorie <= 350:
                bonus_cal = 35
            elif plat.calorie <= 450:
                bonus_cal = 25
            elif plat.calorie <= 600:
                bonus_cal = 12
            else:
                bonus_cal = 1
            score += bonus_cal
            print(f"    • Calories: +{bonus_cal:.2f} (max: 350 kcal)")
            
            # Bonus protéines très élevées (30-50g idéal)
            if 30 <= plat.proteine <= 50:
                bonus_prot = 35
            elif 25 <= plat.proteine <= 55:
                bonus_prot = 25
            elif plat.proteine >= 20:
                bonus_prot = 15
            else:
                bonus_prot = 3
            score += bonus_prot
            print(f"    • Protéines: +{bonus_prot:.2f} (idéal: 30-50g)")
            
            # Malus glucides très stricts (≤ 25g)
            if plat.glucides <= 20:
                bonus_gluc = 20
            elif plat.glucides <= 35:
                bonus_gluc = 12
            elif plat.glucides <= 50:
                bonus_gluc = 5
            else:
                bonus_gluc = 1
            score += bonus_gluc
            print(f"    • Glucides: +{bonus_gluc:.2f} (max: 20g)")
            
            # Malus lipides très stricts (≤ 10g)
            if plat.lipides <= 10:
                bonus_lip = 25
            elif plat.lipides <= 15:
                bonus_lip = 15
            elif plat.lipides <= 25:
                bonus_lip = 8
            else:
                bonus_lip = 2
            score += bonus_lip
            print(f"    • Lipides: +{bonus_lip:.2f} (max: 10g)")
            
            # Bonus fibres très élevées (10-20g idéal)
            if 10 <= plat.fibres <= 20:
                bonus_fib = 25
            elif plat.fibres >= 6:
                bonus_fib = 16
            else:
                bonus_fib = 4
            score += bonus_fib
            print(f"    • Fibres: +{bonus_fib:.2f} (idéal: 10-20g)")
        
        # Facteurs d'âge et de sexe
        print(f"  👤 Facteurs personnels: Âge={age} ans, Sexe={sexe}")
        bonus_age_sexe = 0.0
        
        # Bonus pour les femmes: besoins en fer élevés, moins de calories
        if sexe == 'femme':
            bonus_age_sexe += 2  # Léger bonus pour inclusivité
            # Malus léger si calories très élevées (les femmes ont généralement moins de besoins caloriques)
            if categorie_imc in ['normal', 'insuffisance_ponderale']:
                if plat.calorie > 700:
                    bonus_age_sexe -= 3
            print(f"    • Genre: Femme +{2:.1f} (besoins nutritionnels spécifiques)")
        
        # Bonus pour les hommes: protéines élevées, plus de calories
        elif sexe == 'homme':
            bonus_age_sexe += 1  # Bonus modéré
            # Bonus si protéines élevées (les hommes ont généralement plus de besoins protéiques)
            if plat.proteine > 25:
                bonus_age_sexe += 2
            print(f"    • Genre: Homme +{1 + (2 if plat.proteine > 25 else 0):.1f} (besoins protéiques)")
        
        # Bonus pour l'âge
        if age:
            if age < 20:
                # Jeunes: besoins énergétiques élevés
                bonus_age_sexe += min((plat.calorie / 1000) * 3, 3)
                print(f"    • Âge < 20 ans: +{min((plat.calorie / 1000) * 3, 3):.2f} (besoins énergétiques élevés)")
            elif age >= 50:
                # Seniors: moins de calories, plus de fibres et calcium
                if plat.calorie < 600:
                    bonus_age_sexe += 2
                if plat.fibres > 5:
                    bonus_age_sexe += 1
                print(f"    • Âge >= 50 ans: +{(2 if plat.calorie < 600 else 0) + (1 if plat.fibres > 5 else 0):.2f} (nutrition pour seniors)")
            else:
                # Adultes: balance normale
                bonus_age_sexe += 0
                print(f"    • Âge 20-49 ans: +0.00 (nutrition standard adulte)")
        
        score += bonus_age_sexe
        
        score_final = round(score, 2)
        print(f"  ✅ Score final (avec facteurs personnels): {score_final}/100\n")
        return score_final
    
    @staticmethod
    def calculer_score_professionnel(plat: "Plat", profil: "ProfilNutritionnel") -> float:
        """
        Calcule un score de recommandation PROFESSIONNEL basé sur les meilleures pratiques nutritionnistes.
        
        Méthodologie :
        - Calcul des besoins caloriques personnalisés (Harris-Benedict + activité)
        - Évaluation du plat selon la catégorie IMC
        - Analyse des ratios macronutriments optimaux
        - Évaluation de la densité énergétique
        - Vérification des restrictions et allergies
        - Ajustements spécifiques par âge et sexe
        
        Returns:
            Score normalisé 0-100 où 100 = recommandation idéale
        """
        print(f"\n{'='*70}")
        print(f"CALCUL SCORE PROFESSIONNEL - {plat.nom}")
        print(f"{'='*70}")
        
        # === 1. VÉRIFIER ALLERGIES ET RESTRICTIONS ===
        texte_plat = (plat.nom + " " + plat.description).lower()
        
        if profil.allergies:
            allergies_list = [a.strip().lower() for a in profil.allergies.split(',')]
            for allergie in allergies_list:
                if allergie and allergie in texte_plat:
                    print(f"❌ ALLERGIE DÉTECTÉE: {allergie} → SCORE = 0")
                    print(f"{'='*70}\n")
                    return 0.0
        
        if profil.restrictions_alimentaires:
            restrictions_list = [r.strip().lower() for r in profil.restrictions_alimentaires.split(',')]
            for restriction in restrictions_list:
                if restriction and restriction in texte_plat:
                    print(f"❌ RESTRICTION VIOLÉE: {restriction} → SCORE = 0")
                    print(f"{'='*70}\n")
                    return 0.0
        
        # === 2. CALCULER BESOINS CALORIQUES PERSONNALISÉS ===
        # BMR avec Harris-Benedict révisée
        if profil.sexe == 'homme':
            bmr = 88.362 + (13.397 * float(profil.poids)) + (4.799 * float(profil.taille)) - (5.677 * profil.age)
        else:
            bmr = 447.593 + (9.247 * float(profil.poids)) + (3.098 * float(profil.taille)) - (4.330 * profil.age)
        
        # Appliquer facteur d'activité
        facteurs_activite = {
            'sedentaire': 1.2,
            'leger': 1.375,
            'modere': 1.55,
            'actif': 1.725,
            'extremement_actif': 1.9
        }
        facteur = facteurs_activite.get(profil.niveau_activite, 1.55)
        besoins_calorique_base = bmr * facteur
        
        # Ajustement selon l'objectif
        ajustements_objectif = {
            'perte_poids': 0.8,      # Déficit 20%
            'maintien': 1.0,
            'prise_muscle': 1.2,     # Surplus 20%
            'performance': 1.15
        }
        besoins_calorique = besoins_calorique_base * ajustements_objectif.get(profil.objectif, 1.0)
        
        # === 3. DÉTERMINER RATIOS MACRONUTRIMENTS OPTIMAUX ===
        ratios_macros = {
            'perte_poids': {'protein': 0.38, 'carbs': 0.42, 'fat': 0.20},    # 35-40% prot, 40-45% gluc, 20-25% lip
            'maintien': {'protein': 0.27, 'carbs': 0.50, 'fat': 0.23},       # 25-30% prot, 45-55% gluc, 20-25% lip
            'prise_muscle': {'protein': 0.32, 'carbs': 0.47, 'fat': 0.21},   # 30-35% prot, 45-50% gluc, 20-25% lip
            'performance': {'protein': 0.27, 'carbs': 0.60, 'fat': 0.13}     # 25-30% prot, 55-65% gluc, 10-20% lip
        }
        
        ratios = ratios_macros.get(profil.objectif, ratios_macros['maintien'])
        
        # Besoins en protéines (g/kg)
        besoins_proteines_g_per_kg = {
            'perte_poids': 1.8,           # 1.5-2.0 pour préservation musculaire
            'maintien': 1.2,              # 0.8-1.2 pour sédentaire/léger
            'prise_muscle': 2.0,          # 1.6-2.2 pour hypertrophie
            'performance': 1.4             # 1.2-1.4 pour endurance
        }
        besoins_protein_g = float(profil.poids) * besoins_proteines_g_per_kg.get(profil.objectif, 1.2)
        
        # Besoins en fibres
        besoins_fibres = {
            'perte_poids': 35,            # Augmente satiété
            'maintien': 30,               # Femmes: 25g, Hommes: 38g (moyennes)
            'prise_muscle': 28,
            'performance': 25
        }
        besoins_fibre_g = besoins_fibres.get(profil.objectif, 30)
        
        imc = profil.calculer_imc()
        categorie_imc = profil.determiner_categorie_imc()
        
        print(f"\n📊 PROFIL UTILISATEUR:")
        print(f"  • IMC: {imc:.1f} ({categorie_imc.replace('_', ' ').upper()})")
        print(f"  • Objectif: {dict(ProfilNutritionnel.OBJECTIFS).get(profil.objectif, profil.objectif)}")
        print(f"  • Besoins caloriques: {besoins_calorique:.0f} kcal/jour")
        print(f"  • Besoins protéines: {besoins_protein_g:.1f}g/jour")
        print(f"  • Besoins fibres: {besoins_fibre_g:.0f}g/jour")
        
        print(f"\n🍽️ ANALYSE DU PLAT: {plat.nom}")
        print(f"  • Calories: {plat.calorie:.0f} kcal")
        print(f"  • Protéines: {plat.proteine:.1f}g")
        print(f"  • Glucides: {plat.glucides:.1f}g")
        print(f"  • Lipides: {plat.lipides:.1f}g")
        print(f"  • Fibres: {plat.fibres:.1f}g")
        
        # === 4. ÉVALUER DENSITÉ ÉNERGÉTIQUE ===
        # Poids estimé du plat (généralement 200-400g pour un plat complet)
        poids_estime_plat_g = 300  # Valeur moyenne
        densité_energetique = plat.calorie / poids_estime_plat_g if poids_estime_plat_g > 0 else 0
        
        # === 5. CALCULER SCORES PARTIELS ===
        score_total = 0.0
        scores_details = {}
        
        # **A. SCORE CALORIES** (25 points max)
        pourcentage_besoins = (plat.calorie / besoins_calorique * 100) if besoins_calorique > 0 else 0
        
        if categorie_imc == 'insuffisance_ponderale':
            # Favoriser calories hautes
            if 800 <= plat.calorie <= 1200:
                score_cal = 25
            elif 600 <= plat.calorie < 800 or 1200 < plat.calorie <= 1400:
                score_cal = 20
            elif 400 <= plat.calorie < 600:
                score_cal = 12
            else:
                score_cal = max(0, 25 - abs(1000 - plat.calorie) / 100)
        
        elif categorie_imc == 'normal':
            # Cible 400-800 kcal
            if 400 <= plat.calorie <= 800:
                score_cal = 25
            elif 300 <= plat.calorie < 400 or 800 < plat.calorie <= 900:
                score_cal = 18
            else:
                score_cal = max(0, 25 - abs(600 - plat.calorie) / 50)
        
        elif categorie_imc == 'surpoids':
            # Cible max 500 kcal (sévère)
            if 250 <= plat.calorie <= 450:
                score_cal = 25
            elif 150 <= plat.calorie < 250 or 450 < plat.calorie <= 600:
                score_cal = 18
            elif plat.calorie <= 150 or 600 < plat.calorie <= 750:
                score_cal = 10
            else:
                score_cal = max(0, 5)
        
        else:  # Obésité
            # Cible max 350 kcal (très strict)
            if 200 <= plat.calorie <= 350:
                score_cal = 25
            elif 150 <= plat.calorie < 200 or 350 < plat.calorie <= 450:
                score_cal = 18
            elif plat.calorie <= 150 or 450 < plat.calorie <= 550:
                score_cal = 8
            else:
                score_cal = max(0, 2)
        
        score_cal = round(score_cal, 2)
        scores_details['calories'] = score_cal
        score_total += score_cal
        print(f"\n  📈 Score Calories: {score_cal:.2f}/25")
        
        # **B. SCORE PROTÉINES** (30 points max)
        pourcentage_protein = (plat.proteine / besoins_protein_g * 100) if besoins_protein_g > 0 else 0
        
        if categorie_imc == 'insuffisance_ponderale':
            if plat.proteine >= 35:
                score_prot = 30
            elif 25 <= plat.proteine < 35:
                score_prot = 22
            elif 15 <= plat.proteine < 25:
                score_prot = 12
            else:
                score_prot = max(0, 5)
        
        elif categorie_imc == 'normal':
            if 20 <= plat.proteine <= 35:
                score_prot = 30
            elif 15 <= plat.proteine < 20 or 35 < plat.proteine <= 40:
                score_prot = 22
            elif plat.proteine < 15:
                score_prot = 8
            else:
                score_prot = 18
        
        elif categorie_imc == 'surpoids':
            # Haute priorité aux protéines
            if 25 <= plat.proteine <= 45:
                score_prot = 30
            elif 20 <= plat.proteine < 25 or 45 < plat.proteine <= 50:
                score_prot = 22
            elif 15 <= plat.proteine < 20:
                score_prot = 12
            else:
                score_prot = max(0, 5)
        
        else:  # Obésité
            # TRÈS haute priorité aux protéines
            if 30 <= plat.proteine <= 50:
                score_prot = 30
            elif 25 <= plat.proteine < 30 or 50 < plat.proteine:
                score_prot = 24
            elif 20 <= plat.proteine < 25:
                score_prot = 16
            else:
                score_prot = max(0, 5)
        
        score_prot = round(score_prot, 2)
        scores_details['proteines'] = score_prot
        score_total += score_prot
        print(f"  📈 Score Protéines: {score_prot:.2f}/30")
        
        # **C. SCORE GLUCIDES** (15 points max - important mais moins que protéines)
        if profil.objectif == 'perte_poids':
            # Limiter glucides
            if plat.glucides <= 20:
                score_gluc = 15
            elif 20 < plat.glucides <= 30:
                score_gluc = 10
            elif 30 < plat.glucides <= 45:
                score_gluc = 5
            else:
                score_gluc = 0
        
        elif profil.objectif == 'performance':
            # Glucides plus hauts acceptés
            if 40 <= plat.glucides <= 60:
                score_gluc = 15
            elif 30 <= plat.glucides < 40 or 60 < plat.glucides <= 75:
                score_gluc = 10
            else:
                score_gluc = max(0, 5)
        
        else:  # maintien, prise muscle
            if 30 <= plat.glucides <= 50:
                score_gluc = 15
            elif 20 <= plat.glucides < 30 or 50 < plat.glucides <= 60:
                score_gluc = 10
            else:
                score_gluc = max(0, 3)
        
        score_gluc = round(score_gluc, 2)
        scores_details['glucides'] = score_gluc
        score_total += score_gluc
        print(f"  📈 Score Glucides: {score_gluc:.2f}/15")
        
        # **D. SCORE LIPIDES** (15 points max)
        if categorie_imc in ['surpoids', 'obesite']:
            # Limiter lipides sévèrement
            max_lipides = 10 if categorie_imc == 'obesite' else 15
            if plat.lipides <= max_lipides * 0.7:
                score_lip = 15
            elif plat.lipides <= max_lipides:
                score_lip = 10
            elif plat.lipides <= max_lipides * 1.5:
                score_lip = 5
            else:
                score_lip = 0
        else:
            # Normal à insuffisance
            if 10 <= plat.lipides <= 25:
                score_lip = 15
            elif 5 <= plat.lipides < 10 or 25 < plat.lipides <= 30:
                score_lip = 10
            else:
                score_lip = max(0, 3)
        
        score_lip = round(score_lip, 2)
        scores_details['lipides'] = score_lip
        score_total += score_lip
        print(f"  📈 Score Lipides: {score_lip:.2f}/15")
        
        # **E. SCORE FIBRES** (10 points max)
        if plat.fibres >= besoins_fibre_g / 3:  # 1/3 des besoins journaliers
            score_fib = 10
        elif plat.fibres >= (besoins_fibre_g / 3) * 0.6:
            score_fib = 7
        elif plat.fibres >= (besoins_fibre_g / 3) * 0.3:
            score_fib = 3
        else:
            score_fib = 0
        
        score_fib = round(score_fib, 2)
        scores_details['fibres'] = score_fib
        score_total += score_fib
        print(f"  📈 Score Fibres: {score_fib:.2f}/10")
        
        # **F. BONUS ÂGE & SEXE** (5 points max)
        score_age_sexe = 0.0
        
        # Bonus sexe
        if profil.sexe == 'femme':
            # Besoin fer, moins de calories
            if plat.calorie <= 700:
                score_age_sexe += 2
        else:  # homme
            # Besoins protéiques
            if plat.proteine > 25:
                score_age_sexe += 2
        
        # Bonus âge
        if profil.age < 25:
            # Jeunes ont besoins énergétiques élevés
            if plat.calorie >= 600:
                score_age_sexe += 1.5
        elif profil.age >= 50:
            # Seniors: moins de calories, plus de fibres
            if plat.calorie <= 600 and plat.fibres > 5:
                score_age_sexe += 2
        
        score_age_sexe = round(min(score_age_sexe, 5.0), 2)
        scores_details['age_sexe'] = score_age_sexe
        score_total += score_age_sexe
        print(f"  📈 Score Âge & Sexe: {score_age_sexe:.2f}/5")
        
        # === 6. NORMALISER LE SCORE ===
        score_max_possible = 25 + 30 + 15 + 15 + 10 + 5  # 100
        score_normalisé = (score_total / score_max_possible) * 100
        score_normalisé = round(max(0, min(100, score_normalisé)), 2)
        
        # === 7. RÉSUMÉ ===
        print(f"\n✅ RÉSUMÉ DES SCORES:")
        print(f"  • Calories:     {scores_details['calories']:.2f}/25")
        print(f"  • Protéines:    {scores_details['proteines']:.2f}/30")
        print(f"  • Glucides:     {scores_details['glucides']:.2f}/15")
        print(f"  • Lipides:      {scores_details['lipides']:.2f}/15")
        print(f"  • Fibres:       {scores_details['fibres']:.2f}/10")
        print(f"  • Âge & Sexe:   {scores_details['age_sexe']:.2f}/5")
        print(f"  {'─' * 40}")
        print(f"  SCORE TOTAL: {score_total:.2f}/100")
        print(f"  SCORE NORMALISÉ: {score_normalisé:.2f}/100")
        
        # Évaluation qualitative
        if score_normalisé >= 85:
            evaluation = "🌟 EXCELLENT - Très recommandé"
        elif score_normalisé >= 70:
            evaluation = "✅ BON - Recommandé"
        elif score_normalisé >= 55:
            evaluation = "⚠️ ACCEPTABLE - Peut être inclus"
        elif score_normalisé >= 40:
            evaluation = "❌ FAIBLE - À limiter"
        else:
            evaluation = "🚫 TRÈS FAIBLE - Non recommandé"
        
        print(f"  ÉVALUATION: {evaluation}")
        print(f"{'='*70}\n")
        
        return score_normalisé
    
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

    def ajouter_plat(self, plat: "Plat", quantite: int = 1) -> "CompositionMenu":
        """Ajoute un plat au menu avec gestion des quantités"""
        composition, created = CompositionMenu.objects.get_or_create(
            menu=self,
            plat=plat,
            defaults={'quantite': quantite}
        )
        if not created:
            composition.quantite += quantite
            composition.save()
        return composition
    
    def supprimer_plat(self, plat: "Plat") -> None:
        """Supprime un plat du menu"""
        CompositionMenu.objects.filter(menu=self, plat=plat).delete()
    
    def calculer_valeur_nutritionnelle_totale(self) -> Dict:
        """Calcule les valeurs nutritionnelles totales du menu"""
        compositions = self.compositionmenu_set.all()
        
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

class CompositionMenu(models.Model):
    """Table de liaison entre Menu et Plat"""
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ['menu', 'plat']
        verbose_name = "Composition du menu"
        verbose_name_plural = "Compositions des menus"
    
    def __str__(self):
        return f"{self.menu.nom} - {self.plat.nom} x{self.quantite}"

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

class SystemeIA(models.Model):
    """Système d'intelligence artificielle pour les recommandations"""
    nom = models.CharField(max_length=100, default="Nutrition AI")
    version = models.CharField(max_length=20)
    est_actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def analyser_preferences(self, client: "Client") -> Dict:
        """Analyse les préférences alimentaires du client basées sur l'historique"""
        commandes = client.commandes.filter(statut='livree')
        plats_frequents = []
        categories_populaires = {}
        
        for commande in commandes:
            for ligne in commande.lignecommande_set.all():
                for composition in ligne.menu.compositionmenu_set.all():
                    plat = composition.plat
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