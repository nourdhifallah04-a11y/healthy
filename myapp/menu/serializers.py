from myapp.plat.serializers import PlatSerializer
from rest_framework import serializers
from myapp.plat.models import Plat
from myapp.menu.models import Menu
# Importer les fonctions cache et constantes



class MenuSerializer(serializers.ModelSerializer):
    plats = PlatSerializer(many=True, read_only=True)
    valeur_nutritionnelle = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = '__all__'
    
    def get_valeur_nutritionnelle(self, obj):
        """Retourne les valeurs nutritionnelles totales du menu"""
        return obj.calculer_valeur_nutritionnelle_totale()

class MenuRecommandationSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour les menus recommandés avec liste de plats"""
    plats = serializers.SerializerMethodField()
    valeur_nutritionnelle = serializers.SerializerMethodField()
    prix_total = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = ['id_menu', 'nom', 'description', 'date_debut', 'date_fin', 'prix_total',
                  'est_actif', 'score', 'plats', 'valeur_nutritionnelle']
    
    def get_plats(self, obj):
        """Retourne la liste simplifiée des plats du menu"""
        plats_list = []
        for plat in obj.plats.all():
            # Gérer le cas où l'image peut être vide
            image_url = None
            if plat.image:
                try:
                    image_url = plat.image.url
                except ValueError:
                    image_url = None
            
            plats_list.append({
                'id': plat.id_plat,
                'nom': plat.nom,
                'calorie': plat.calorie,
                'proteine': plat.proteine,
                'glucides': plat.glucides,
                'lipides': plat.lipides,
                'fibres': plat.fibres,
                'image': image_url,
                'prix': plat.prix,
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

