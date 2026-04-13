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
        """Calcule le métabolisme de base (Formule de Harris-Benedict)"""
        poids_kg = float(self.poids)
        taille_cm = float(self.taille)
        age_ans = self.age
        
        # Formule pour homme (à améliorer selon le sexe)
        bmr = 88.362 + (13.397 * poids_kg) + (4.799 * taille_cm) - (5.677 * age_ans)
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
                restrictions=self.restrictions_alimentaires
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
                                     allergies: str = "", restrictions: str = "") -> float:
        """
        Calcule un score de recommandation pour un plat basé sur la catégorie IMC, 
        allergies et restrictions alimentaires
        
        Stratégies par catégorie IMC:
        - Insuffisance pondérale: Calories élevées, protéines modérées
        - Normal: Équilibre optimal entre tous les nutriments
        - Surpoids: Faibles calories, protéines élevées, lipides bas, fibres élevées
        - Obésité: Très faibles calories, protéines très élevées, très faibles lipides
        
        Args:
            plat: Instance du modèle Plat
            categorie_imc: Catégorie d'IMC ('insuffisance_ponderale', 'normal', 'surpoids', 'obesite')
            allergies: Chaîne contenant les allergies du client (ex: "arachide, lactose")
            restrictions: Chaîne contenant les restrictions alimentaires (ex: "végétarien, sans gluten")
        
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
        
        score_final = round(score, 2)
        print(f"  ✅ Score final: {score_final}/100\n")
        return score_final
    
    def __str__(self):
        return f"{self.nom} - {self.calorie} kcal"

class Menu(models.Model):
    """Modèle Menu"""
    id_menu = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    plats = models.ManyToManyField("Plat", related_name="menus")

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
    
    def __str__(self):
        return f"Commande #{self.id_commande} - {self.client.utilisateur.nom}"

class LigneCommande(models.Model):
    """Ligne de commande"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=3)
    
    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
    
    def __str__(self):
        return f"{self.commande.id_commande} - {self.menu.nom} x{self.quantite}"

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