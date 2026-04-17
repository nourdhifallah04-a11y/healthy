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

class PlatRecommandationSerializer(serializers.ModelSerializer):
    """Serializer pour les plats recommandés avec score"""
    valeur_nutritionnelle = serializers.SerializerMethodField()
    score = serializers.FloatField(read_only=True)
    score_nutritionnel = serializers.SerializerMethodField()
    
    class Meta:
        model = Plat
        fields = ['id_plat', 'nom', 'description', 'calorie', 'proteine', 'glucides', 'lipides', 
                  'fibres', 'prix', 'est_disponible', 'isNew', 'image', 'score', 'score_nutritionnel', 
                  'valeur_nutritionnelle']
    
    def get_valeur_nutritionnelle(self, obj):
        """Retourne les valeurs nutritionnelles du plat"""
        return {
            'calories': obj.calorie,
            'proteines': obj.proteine,
            'glucides': obj.glucides,
            'lipides': obj.lipides,
            'fibres': obj.fibres,
            'prix': float(obj.prix) if obj.prix else 0.0
        }
    
    def get_score_nutritionnel(self, obj):
        """Calcule le score nutritionnel du plat"""
        if obj.proteine > 0:
            return round((obj.proteine * 2 - obj.lipides) / 100, 2)
        return 0.0

class MenuRecommandationSerializer(serializers.ModelSerializer):
    """Serializer pour les menus recommandés avec liste de plats"""
    plats = serializers.SerializerMethodField()
    valeur_nutritionnelle = serializers.SerializerMethodField()
    prix_total = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    compositions = CompositionMenuSerializer(source='compositionmenu_set', many=True, read_only=True)
    
    class Meta:
        model = Menu
        fields = ['id_menu', 'nom', 'description', 'date_debut', 'date_fin', 'prix_total',
                  'est_actif', 'score', 'plats', 'compositions', 'valeur_nutritionnelle']
    
    def get_plats(self, obj):
        """Retourne la liste simplifiée des plats du menu"""
        compositions = obj.compositionmenu_set.all()
        plats_list = []
        for comp in compositions:
            # Gérer le cas où l'image peut être vide
            image_url = None
            if comp.plat.image:
                try:
                    image_url = comp.plat.image.url
                except ValueError:
                    image_url = None
            
            plats_list.append({
                'id': comp.plat.id_plat,
                'nom': comp.plat.nom,
                'quantite': comp.quantite,
                'calorie': comp.plat.calorie,
                'proteine': comp.plat.proteine,
                'glucides': comp.plat.glucides,
                'lipides': comp.plat.lipides,
                'fibres': comp.plat.fibres,
                'image': image_url,
                'prix': comp.plat.prix,
            })
        return plats_list
    
    def get_prix_total(self, obj):
        """Retourne le prix total du menu"""
        valeur = obj.calculer_valeur_nutritionnelle_totale()
        return valeur.get('prix', 0)
    
    def get_score(self, obj):
        """Retourne le score du menu (défini par la vue)"""
        # Le score est ajouté par la vue, retourner 0 par défaut
        return 0.0
    
    def get_valeur_nutritionnelle(self, obj):
        return obj.calculer_valeur_nutritionnelle_totale()

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

class SystemeIASerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemeIA
        fields = '__all__'


class UnifiedMenuItemSerializer(serializers.Serializer):
    """
    Sérialiseur unifié pour combiner Plat et Menu
    """
    id = serializers.SerializerMethodField()
    item_id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    nom = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    calories = serializers.SerializerMethodField()
    proteines = serializers.SerializerMethodField()
    glucides = serializers.SerializerMethodField()
    lipides = serializers.SerializerMethodField()
    fibres = serializers.SerializerMethodField()
    prix = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    diet_categories = serializers.SerializerMethodField()
    score_nutritionnel = serializers.SerializerMethodField()
    est_disponible = serializers.SerializerMethodField()
    
    def __init__(self, *args, data_obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_obj = data_obj
    
    def get_id(self, obj):
        if isinstance(obj, Plat):
            return f"plat_{obj.id_plat}"
        else:
            return f"menu_{obj.id_menu}"
    
    def get_item_id(self, obj):
        if isinstance(obj, Plat):
            return obj.id_plat
        else:
            return obj.id_menu
    
    def get_type(self, obj):
        return "plat" if isinstance(obj, Plat) else "menu"
    
    def get_nom(self, obj):
        return obj.nom
    
    def get_description(self, obj):
        return obj.description
    
    def get_calories(self, obj):
        if isinstance(obj, Plat):
            return obj.calorie
        else:
            return obj.calculer_valeur_nutritionnelle_totale().get('calories', 0)
    
    def get_proteines(self, obj):
        if isinstance(obj, Plat):
            return obj.proteine
        else:
            return obj.calculer_valeur_nutritionnelle_totale().get('proteines', 0)
    
    def get_glucides(self, obj):
        if isinstance(obj, Plat):
            return obj.glucides
        else:
            return obj.calculer_valeur_nutritionnelle_totale().get('glucides', 0)
    
    def get_lipides(self, obj):
        if isinstance(obj, Plat):
            return obj.lipides
        else:
            return obj.calculer_valeur_nutritionnelle_totale().get('lipides', 0)
    
    def get_fibres(self, obj):
        if isinstance(obj, Plat):
            return obj.fibres
        else:
            return 0  # Fibres not easily computable for Menu
    
    def get_prix(self, obj):
        if isinstance(obj, Plat):
            return float(obj.prix)
        else:
            return obj.calculer_valeur_nutritionnelle_totale().get('prix', 0)
    
    def get_image(self, obj):
        if isinstance(obj, Plat) and obj.image:
            try:
                return obj.image.url
            except ValueError:
                return None
        return None
    
    def get_diet_categories(self, obj):
        if isinstance(obj, Plat):
            return obj.get_diet_categories()
        else:
            return [obj.diet_category] if obj.diet_category else []
    
    def get_score_nutritionnel(self, obj):
        if isinstance(obj, Plat):
            return obj.calculer_score_nutritionnel()
        else:
            return 0
    
    def get_est_disponible(self, obj):
        if isinstance(obj, Plat):
            return obj.est_disponible
        else:
            return obj.est_actif
        fields = '__all__'