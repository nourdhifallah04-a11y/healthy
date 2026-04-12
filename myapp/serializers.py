from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Client, Administrateur, ProfilNutritionnel, Plat, 
    Menu, CompositionMenu, Commande, LigneCommande, SystemeIA
)

Utilisateur = get_user_model()

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'nom', 'prenom', 'telephone', 'adresse', 'date_inscription']
        read_only_fields = ['date_inscription']

class ClientSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer()
    
    class Meta:
        model = Client
        fields = ['id', 'utilisateur', 'date_naissance']
    
    def create(self, validated_data):
        utilisateur_data = validated_data.pop('utilisateur')
        utilisateur = Utilisateur.objects.create_user(**utilisateur_data)
        client = Client.objects.create(utilisateur=utilisateur, **validated_data)
        return client

class ProfilNutritionnelSerializer(serializers.ModelSerializer):
    imc = serializers.SerializerMethodField()
    besoins_caloriques = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfilNutritionnel
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_imc(self, obj):
        return round(obj.calculer_imc(), 2)
    
    def get_besoins_caloriques(self, obj):
        return obj.besoins_caloriques_journaliers()

class PlatSerializer(serializers.ModelSerializer):
    score_nutritionnel = serializers.SerializerMethodField()
    
    class Meta:
        model = Plat
        fields = '__all__'
    
    def get_score_nutritionnel(self, obj):
        return obj.calculer_score_nutritionnel()

class CompositionMenuSerializer(serializers.ModelSerializer):
    plat_detail = PlatSerializer(source='plat', read_only=True)
    
    class Meta:
        model = CompositionMenu
        fields = ['id', 'menu', 'plat', 'plat_detail', 'quantite']

class MenuSerializer(serializers.ModelSerializer):
    compositions = CompositionMenuSerializer(source='compositionmenu_set', many=True, read_only=True)
    valeur_nutritionnelle = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = '__all__'
    
    def get_valeur_nutritionnelle(self, obj):
        return obj.calculer_valeur_nutritionnelle_totale()

class LigneCommandeSerializer(serializers.ModelSerializer):
    menu_detail = MenuSerializer(source='menu', read_only=True)
    sous_total_display = serializers.SerializerMethodField()
    
    class Meta:
        model = LigneCommande
        fields = ['id', 'commande', 'menu', 'menu_detail', 'quantite', 'prix_unitaire', 'sous_total_display']
    
    def get_sous_total_display(self, obj):
        return str(obj.sous_total)

class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(source='lignecommande_set', many=True, read_only=True)
    client_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Commande
        fields = '__all__'
        read_only_fields = ['date', 'total']
    
    def get_client_nom(self, obj):
        return str(obj.client)

class SystemeIASerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemeIA
        fields = '__all__'