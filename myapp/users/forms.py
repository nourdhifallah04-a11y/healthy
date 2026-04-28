from django import forms
from django.contrib.auth import get_user_model
from myapp.commande.models import Commande
from myapp.profilNutritionnel.models import ProfilNutritionnel
from myapp.users.models import Client, Utilisateur
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


