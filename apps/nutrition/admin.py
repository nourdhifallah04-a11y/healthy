"""
Admin pour l'app nutrition
"""
from django.contrib import admin
from .models import Food, NutritionalProfile, ProfilNutritionnel, Plat, Menu


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'calories', 'proteins', 'carbs', 'fats']
    search_fields = ['name']
    list_filter = ['calories']


@admin.register(NutritionalProfile)
class NutritionalProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'weight', 'daily_calorie_goal']
    search_fields = ['user__username']
    list_filter = ['gender', 'activity_level']


@admin.register(ProfilNutritionnel)
class ProfilNutritionnelAdmin(admin.ModelAdmin):
    list_display = ['client', 'age', 'poids', 'objectif', 'niveau_activite']
    list_filter = ['objectif', 'niveau_activite', 'sexe']
    search_fields = ['client__utilisateur__email', 'client__utilisateur__nom']
    fieldsets = (
        ('Profil', {'fields': ('client', 'age', 'taille', 'poids', 'sexe')}),
        ('Alimentation', {'fields': ('objectif', 'niveau_activite', 'allergies', 'restrictions_alimentaires')}),
        ('Consentement', {'fields': ('donnees_sante_sensibles', 'learning_collectif')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'calorie', 'proteine', 'glucides', 'prix', 'est_disponible']
    list_filter = ['est_disponible', 'isNew', 'created_at']
    search_fields = ['nom', 'description']
    fieldsets = (
        ('Informations', {'fields': ('nom', 'description', 'prix', 'image')}),
        ('Nutritionnel', {'fields': ('calorie', 'proteine', 'glucides', 'lipides', 'fibres')}),
        ('Statut', {'fields': ('est_disponible', 'isNew')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_debut', 'date_fin', 'est_actif', 'diet_category']
    list_filter = ['est_actif', 'diet_category', 'date_debut']
    search_fields = ['nom', 'description']
    filter_horizontal = ['plats']
    fieldsets = (
        ('Informations', {'fields': ('nom', 'description')}),
        ('Dates', {'fields': ('date_debut', 'date_fin')}),
        ('Catégorie', {'fields': ('diet_category',)}),
        ('Plats', {'fields': ('plats',)}),
        ('Statut', {'fields': ('est_actif',)}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at']

