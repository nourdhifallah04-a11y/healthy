


from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from decimal import Decimal
class UtilisateurManager(BaseUserManager):
    """Manager personnalisé pour utiliser l'email comme identifiant"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
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
    permissions = models.JSONField(default=dict)
    
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
    
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='profil_nutritionnel')
    age = models.IntegerField()
    taille = models.DecimalField(max_digits=5, decimal_places=2, help_text="Taille en cm")
    poids = models.DecimalField(max_digits=5, decimal_places=2, help_text="Poids en kg")
    allergies = models.TextField(blank=True, help_text="Allergies alimentaires")
    objectif = models.CharField(max_length=20, choices=OBJECTIFS)
    restrictions_alimentaires = models.TextField(blank=True)
    niveau_activite = models.CharField(max_length=20, choices=NIVEAU_ACTIVITE, default='modere')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculer_imc(self):
        """Calcule l'IMC du client"""
        taille_m = float(self.taille) / 100
        return float(self.poids) / (taille_m ** 2)
    
    def calculer_bmr(self):
        """Calcule le métabolisme de base (Formule de Harris-Benedict)"""
        if self.client.utilisateur.is_superuser:
            return 0  # À implémenter selon le sexe
        
        poids_kg = float(self.poids)
        taille_cm = float(self.taille)
        age_ans = self.age
        
        # Formule pour homme par défaut
        bmr = 88.362 + (13.397 * poids_kg) + (4.799 * taille_cm) - (5.677 * age_ans)
        return round(bmr, 2)
    
    def besoins_caloriques_journaliers(self):
        """Calcule les besoins caloriques journaliers"""
        bmr = self.calculer_bmr()
        facteurs = {
            'sedentaire': 1.2,
            'leger': 1.375,
            'modere': 1.55,
            'actif': 1.725,
            'extremement_actif': 1.9
        }
        
        facteur = facteurs.get(self.niveau_activite, 1.55)
        
        if self.objectif == 'perte_poids':
            facteur -= 0.2
        elif self.objectif == 'prise_muscle':
            facteur += 0.2
            
        return round(bmr * facteur, 2)
    
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
    image = models.ImageField(upload_to='plats/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def afficher_detail(self):
        """Affiche les détails du plat"""
        return {
            'nom': self.nom,
            'calories': self.calorie,
            'proteines': self.proteine,
            'glucides': self.glucides,
            'lipides': self.lipides,
            'prix': str(self.prix)
        }
    
    def calculer_score_nutritionnel(self):
        """Calcule un score nutritionnel de 0 à 100"""
        score = 50  # Score de base
        
        # Bonus pour les protéines
        if self.proteine > 30:
            score += 20
        elif self.proteine > 20:
            score += 10
            
        # Malus pour les calories élevées
        if self.calorie > 800:
            score -= 20
        elif self.calorie > 600:
            score -= 10
            
        # Bonus pour les fibres
        if self.fibres > 10:
            score += 15
        elif self.fibres > 5:
            score += 8
            
        # Malus pour les lipides
        if self.lipides > 30:
            score -= 15
        elif self.lipides > 20:
            score -= 8
            
        return max(0, min(100, score))
    
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

    def ajouter_plat(self, plat, quantite=1):
        """Ajoute un plat au menu"""
        composition, created = CompositionMenu.objects.get_or_create(
            menu=self,
            plat=plat,
            defaults={'quantite': quantite}
        )
        if not created:
            composition.quantite += quantite
            composition.save()
        return composition
    
    def supprimer_plat(self, plat):
        """Supprime un plat du menu"""
        CompositionMenu.objects.filter(menu=self, plat=plat).delete()
    
    def calculer_valeur_nutritionnelle_totale(self):
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
    
    def valider_commande(self):
        """Valide la commande"""
        if self.statut == 'panier':
            self.statut = 'confirmee'
            self.save()
            return True
        return False
    
    def calculer_total(self):
        """Calcule le total de la commande"""
        lignes = self.lignecommande_set.all()
        total = sum(float(ligne.sous_total) for ligne in lignes)
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
    
    def analyser_preferences(self, client):
        """Analyse les préférences du client"""
        commandes = client.commandes.filter(statut='livree')
        plats_frequents = []
        categories_populaires = {}
        
        for commande in commandes:
            for ligne in commande.lignecommande_set.all():
                for composition in ligne.menu.compositionmenu_set.all():
                    plat = composition.plat
                    plats_frequents.append(plat)
                    
                    # Catégorisation simple
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
    
    def recommander_menus(self, client, limite=5):
        """Recommande des menus personnalisés"""
        profil = client.profil_nutritionnel
        menus_actifs = Menu.objects.filter(est_actif=True)
        
        # Analyser les préférences
        preferences = self.analyser_preferences(client)
        
        # Calculer le score pour chaque menu
        menus_scores = []
        for menu in menus_actifs:
            valeurs = menu.calculer_valeur_nutritionnelle_totale()
            score = 0
            
            # Score basé sur l'objectif
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
            score_nutritionnel = sum(valeurs['proteines'] * 2 - valeurs['lipides']) / 100
            score += max(0, min(20, score_nutritionnel))
            
            menus_scores.append((menu, score))
        
        # Trier par score
        menus_scores.sort(key=lambda x: x[1], reverse=True)
        return [menu for menu, score in menus_scores[:limite]]
    
    def __str__(self):
        return f"{self.nom} v{self.version}"