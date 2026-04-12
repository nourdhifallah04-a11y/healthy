from django import forms
from .models import ProfilNutritionnel

class ProfilNutritionnelForm(forms.ModelForm):
    class Meta:
        model = ProfilNutritionnel
        fields = ['age', 'poids', 'taille', 'objectif']  # adapte selon ton modèle