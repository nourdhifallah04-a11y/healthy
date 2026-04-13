from django import forms
from .models import ProfilNutritionnel

class ProfilNutritionnelForm(forms.ModelForm):
    class Meta:
        model = ProfilNutritionnel
        fields = ['age', 'taille', 'poids', 'sexe', 'objectif', 'niveau_activite', 'allergies', 'restrictions_alimentaires']
        widgets = {
            'age': forms.NumberInput(attrs={'min': '10', 'max': '120'}),
            'taille': forms.NumberInput(attrs={'min': '100', 'max': '250', 'step': '0.1'}),
            'poids': forms.NumberInput(attrs={'min': '20', 'max': '300', 'step': '0.1'}),
            'sexe': forms.Select(),
            'objectif': forms.Select(),
            'niveau_activite': forms.Select(),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'restrictions_alimentaires': forms.Textarea(attrs={'rows': 3}),
        }


class AdminLoginForm(forms.Form):
    """Formulaire de connexion pour les administrateurs"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre email',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe',
            'autocomplete': 'current-password'
        })
    )