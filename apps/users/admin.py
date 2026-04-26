"""
Admin pour l'app users
"""
from django.contrib import admin
from .models import User, Utilisateur, Client, Administrateur


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = (
        ('Identité', {'fields': ('username', 'email', 'first_name', 'last_name')}),
        ('Sécurité', {'fields': ('password', 'is_active', 'is_staff', 'is_superuser')}),
        ('Profil', {'fields': ('role', 'bio', 'avatar', 'is_verified')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ['email', 'nom', 'prenom', 'telephone', 'est_actif', 'date_inscription']
    list_filter = ['est_actif', 'date_inscription']
    search_fields = ['email', 'nom', 'prenom']
    fieldsets = (
        ('Identité', {'fields': ('email', 'nom', 'prenom')}),
        ('Contact', {'fields': ('telephone', 'adresse')}),
        ('Statut', {'fields': ('est_actif', 'date_inscription')}),
    )
    readonly_fields = ['date_inscription']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'date_naissance']
    search_fields = ['utilisateur__email', 'utilisateur__nom']
    list_filter = ['date_naissance']


@admin.register(Administrateur)
class AdministrateurAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'role']
    search_fields = ['utilisateur__email', 'role']
    list_filter = ['role']

