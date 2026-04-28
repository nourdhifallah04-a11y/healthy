from myapp.profilNutritionnel.models import ProfilNutritionnel
from rest_framework import serializers
from myapp.plat.models import Plat
# Importer les fonctions cache et constantes
try:
    from .score_constants import get_cached_score, set_cached_score
except ImportError:
    def get_cached_score(key, func=None):
        return func() if func else None
    def set_cached_score(key, value):
        return value

class PlatSerializer(serializers.ModelSerializer):
    score_nutritionnel = serializers.SerializerMethodField()
    
    class Meta:
        model = Plat
        fields = '__all__'
    
    def get_score_nutritionnel(self, obj):
        """Obtient le score nutritionnel du plat (utilise le cache du modèle)"""
        return obj.calculer_score_nutritionnel()

class PlatRecommandationSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour les plats recommandés avec score"""
    valeur_nutritionnelle = serializers.SerializerMethodField()
    score = serializers.FloatField(read_only=True)
    score_nutritionnel = serializers.SerializerMethodField()
    
    class Meta:
        model = Plat
        fields = ['id_plat', 'nom', 'description', 'calorie', 'proteine', 'glucides', 'lipides', 
                  'fibres', 'prix', 'est_disponible', 'isNew', 'image', 'score', 'score_nutritionnel', 
                  'valeur_nutritionnelle']
    
    def get_valeur_nutritionnelle(self, obj):
        """Retourne les valeurs nutritionnelles du plat (optimisé)"""
        return {
            'calories': obj.calorie,
            'proteines': obj.proteine,
            'glucides': obj.glucides,
            'lipides': obj.lipides,
            'fibres': obj.fibres,
            'prix': float(obj.prix) if obj.prix else 0.0
        }
    
    def get_score_nutritionnel(self, obj):
        """Calcule le score nutritionnel du plat (optimisé)"""
        cache_key = f"score_nutr_{obj.id_plat}"
        cached = get_cached_score(cache_key)
        if cached is not None:
            return cached
        
        # Formule rapide : (protéines * 2 - lipides) / 100
        score = 0.0
        if obj.proteine > 0:
            score = (obj.proteine * 2 - obj.lipides) / 100
        
        final_score = round(score, 2)
        set_cached_score(cache_key, final_score)
        return final_score

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