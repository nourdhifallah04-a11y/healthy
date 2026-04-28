from myapp.menu.serializers import MenuSerializer
from myapp.plat.serializers import PlatSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from myapp.commande.models import Commande, LigneCommande


Utilisateur = get_user_model()

class LigneCommandeSerializer(serializers.ModelSerializer):
    menu_detail = MenuSerializer(source='menu', read_only=True)
    plat_detail = PlatSerializer(source='plat', read_only=True)
    item_type = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    sous_total_display = serializers.SerializerMethodField()
    
    class Meta:
        model = LigneCommande
        fields = ['id', 'commande', 'menu', 'plat', 'menu_detail', 'plat_detail', 'item_type', 
                  'item_name', 'quantite', 'prix_unitaire', 'sous_total_display']
    
    def get_item_type(self, obj):
        return obj.get_item_type()
    
    def get_item_name(self, obj):
        return obj.get_item_name()
    
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

