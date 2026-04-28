from rest_framework import serializers
from myapp.profilNutritionnel.models import ProfilNutritionnel



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

