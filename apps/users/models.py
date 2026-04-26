"""
Modèles pour l'app users
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from apps.core.models import TimeStampedModel


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
        db_table = "users_utilisateur"
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


class User(AbstractUser, TimeStampedModel):
    """Modèle utilisateur étendu (gardé pour compatibilité)"""
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('nutritionist', 'Nutritionniste'),
        ('admin', 'Administrateur'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Rôle'
    )
    bio = models.TextField(blank=True, verbose_name='Biographie')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Vérifiée'
    )
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.get_full_name() or self.username
