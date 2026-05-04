from django.contrib import admin
from myapp.users.models import Utilisateur, Client, Administrateur
from myapp.profilNutritionnel.models import ProfilNutritionnel
from myapp.commande.models import Commande, LigneCommande

from myapp.plat.models import Plat
from myapp.menu.models import Menu
from myapp.systemeIA.models import SystemeIA
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
    fields = ['utilisateur', 'role', 'permissions', 'n8n_basic_auth_password']

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


class LigneCommandeInline(admin.TabularInline):
    """Inline admin pour les lignes de commande"""
    model = LigneCommande
    extra = 1
    readonly_fields = ['prix_unitaire']
    fields = ['menu', 'quantite', 'prix_unitaire']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id_commande', 'client', 'date', 'statut', 'total']
    list_filter = ['statut', 'date']
    search_fields = ['client__utilisateur__email', 'client__utilisateur__nom']
    readonly_fields = ['id_commande', 'date', 'total']
    fieldsets = (
        ('Informations', {
            'fields': ('id_commande', 'client', 'date', 'statut')
        }),
        ('Livraison', {
            'fields': ('adresse_livraison',)
        }),
        ('Montant', {
            'fields': ('total',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    inlines = [LigneCommandeInline]


@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ['commande', 'menu', 'quantite', 'prix_unitaire', 'get_sous_total']
    list_filter = ['commande__statut', 'commande__date']
    search_fields = ['commande__id_commande', 'menu__nom']
    readonly_fields = ['get_sous_total']
    
    def get_sous_total(self, obj):
        return f"{obj.sous_total}€"
    get_sous_total.short_description = 'Sous-total'

@admin.register(SystemeIA)
class SystemeIAAdmin(admin.ModelAdmin):
    list_display = ['nom', 'version', 'est_actif']