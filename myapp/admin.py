from django.contrib import admin
from myapp.models import (
    Utilisateur, Client, Administrateur, ProfilNutritionnel, Plat,
    Menu, Commande, SystemeIA
)

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ['email', 'nom', 'prenom', 'date_inscription']
    search_fields = ['email', 'nom', 'prenom']
    list_filter = ['est_actif']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur']
    search_fields = ['utilisateur__nom', 'utilisateur__email']

@admin.register(Administrateur)
class AdministrateurAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'role']
    search_fields = ['utilisateur__nom', 'utilisateur__email']
    list_filter = ['role']
    fields = ['utilisateur', 'role', 'permissions']

@admin.register(ProfilNutritionnel)
class ProfilNutritionnelAdmin(admin.ModelAdmin):
    list_display = ['client', 'age', 'taille', 'poids', 'objectif']
    list_filter = ['objectif', 'niveau_activite']

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'calorie', 'proteine', 'prix', 'est_disponible']
    list_filter = ['est_disponible']
    search_fields = ['nom']

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_debut', 'date_fin', 'est_actif']
    list_filter = ['est_actif']
    filter_horizontal = ['plats']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id_commande', 'client', 'date', 'statut', 'total']
    list_filter = ['statut', 'date']

@admin.register(SystemeIA)
class SystemeIAAdmin(admin.ModelAdmin):
    list_display = ['nom', 'version', 'est_actif']