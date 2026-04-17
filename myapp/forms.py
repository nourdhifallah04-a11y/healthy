from django import forms
from django.contrib.auth import get_user_model
from .models import ProfilNutritionnel, Client, Utilisateur, Commande

User = get_user_model()


class RegistrationForm(forms.Form):
    """Formulaire d'inscription pour créer un Utilisateur et un Client"""
    
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
            'autocomplete': 'new-password'
        }),
        min_length=8,
        help_text='Au moins 8 caractères'
    )
    
    password_confirm = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password'
        })
    )
    
    nom = forms.CharField(
        label='Nom',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom'
        })
    )
    
    prenom = forms.CharField(
        label='Prénom',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre prénom'
        })
    )
    
    telephone = forms.CharField(
        label='Téléphone (optionnel)',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre téléphone'
        })
    )
    
    adresse = forms.CharField(
        label='Adresse (optionnel)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Votre adresse',
            'rows': 3
        })
    )
    
    date_naissance = forms.DateField(
        label='Date de naissance (optionnel)',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean_email(self):
        """Vérifier que l'email n'existe pas déjà"""
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def clean(self):
        """Vérifier que les mots de passe correspondent"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        return cleaned_data
    
    def save(self):
        """Créer l'Utilisateur et le Client"""
        try:
            # Créer l'Utilisateur
            utilisateur = Utilisateur.objects.create_user(
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                nom=self.cleaned_data['nom'],
                prenom=self.cleaned_data['prenom'],
                telephone=self.cleaned_data['telephone'],
                adresse=self.cleaned_data['adresse']
            )
            
            # Créer le Client associé
            client = Client.objects.create(
                utilisateur=utilisateur,
                date_naissance=self.cleaned_data['date_naissance']
            )
            
            return utilisateur, client
        except Exception as e:
            raise forms.ValidationError(f"Erreur lors de la création du compte: {str(e)}")


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
