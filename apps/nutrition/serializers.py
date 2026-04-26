"""
Serializers pour l'app nutrition
"""
from rest_framework import serializers
from .models import Food, NutritionalProfile, ProfilNutritionnel, Plat, Menu


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'calories', 'proteins', 'carbs', 'fats', 'fiber',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NutritionalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalProfile
        fields = [
            'id', 'user', 'age', 'height', 'weight', 'gender',
            'activity_level', 'daily_calorie_goal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProfilNutritionnelSerializer(serializers.ModelSerializer):
    imc = serializers.SerializerMethodField()
    besoins_caloriques = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfilNutritionnel
        fields = [
            'id', 'client', 'age', 'taille', 'poids', 'sexe',
            'allergies', 'objectif', 'restrictions_alimentaires',
            'niveau_activite', 'donnees_sante_sensibles', 'learning_collectif',
            'created_at', 'updated_at', 'imc', 'besoins_caloriques'
        ]
        read_only_fields = ['created_at', 'updated_at', 'imc', 'besoins_caloriques']
    
    def get_imc(self, obj):
        return round(obj.calculer_imc(), 2)
    
    def get_besoins_caloriques(self, obj):
        return round(obj.besoins_caloriques_journaliers(), 2)


class PlatSerializer(serializers.ModelSerializer):
    diet_categories = serializers.SerializerMethodField()
    
    class Meta:
        model = Plat
        fields = [
            'id_plat', 'nom', 'description', 'calorie', 'proteine',
            'glucides', 'lipides', 'fibres', 'prix', 'est_disponible',
            'isNew', 'image', 'created_at', 'diet_categories'
        ]
        read_only_fields = ['id_plat', 'created_at']
    
    def get_diet_categories(self, obj):
        return obj.get_diet_categories()


class MenuSerializer(serializers.ModelSerializer):
    plats = PlatSerializer(many=True, read_only=True)
    valeurs_nutritionnelles = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = [
            'id_menu', 'nom', 'description', 'date_debut', 'date_fin',
            'est_actif', 'diet_category', 'created_at', 'plats',
            'valeurs_nutritionnelles'
        ]
        read_only_fields = ['id_menu', 'created_at']
    
    def get_valeurs_nutritionnelles(self, obj):
        return obj.calculer_valeur_nutritionnelle_totale()

