from django import forms
from django.contrib.auth import get_user_model
from myapp.commande.models import Commande
from myapp.profilNutritionnel.models import ProfilNutritionnel
from myapp.users.models import Client, Utilisateur
User = get_user_model()


# ============================================
# COMMANDE FORMS
# ============================================

class CheckoutForm(forms.ModelForm):
    """Formulaire pour la validation et le paiement d'une commande"""
    
    class Meta:
        model = Commande
        fields = ['adresse_livraison', 'notes']
        widgets = {
            'adresse_livraison': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre adresse de livraison',
                'rows': 4,
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Remarques ou instructions spéciales (optionnel)',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['adresse_livraison'].label = 'Adresse de livraison'
        self.fields['notes'].label = 'Notes spéciales'
        self.fields['notes'].required = False


class CommandeFilterForm(forms.Form):
    """Formulaire pour filtrer les commandes"""
    STATUT_CHOICES = [
        ('', 'Tous les statuts'),
    ] + Commande.STATUTS
    
    statut = forms.ChoiceField(
        choices=STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        label='Du',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        label='Au',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class LigneCommandeForm(forms.Form):
    """Formulaire pour ajouter une ligne de commande"""
    
    menu_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    
    quantite = forms.IntegerField(
        label='Quantité',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1'
        })
    )
    
    def clean_quantite(self):
        """Valider la quantité"""
        quantite = self.cleaned_data.get('quantite')
        if quantite < 1:
            raise forms.ValidationError("La quantité doit être au minimum 1.")
        if quantite > 100:
            raise forms.ValidationError("La quantité ne peut pas dépasser 100.")
        return quantite


class PromoCodeForm(forms.Form):
    """Formulaire pour appliquer un code promo"""
    
    promo_code = forms.CharField(
        label='Code promo',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control promo-input',
            'placeholder': 'Entrez votre code promo',
            'autocomplete': 'off'
        })
    )
    
    def clean_promo_code(self):
        """Valider le code promo"""
        code = self.cleaned_data.get('promo_code')
        if not code:
            raise forms.ValidationError("Le code promo ne peut pas être vide.")
        return code.upper()
