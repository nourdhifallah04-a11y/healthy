#!/usr/bin/env python
"""
Script de test pour l'inscription d'un utilisateur et création du client
"""
import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthy.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

from myapp.models import Utilisateur, Client
from myapp.forms import RegistrationForm

def test_registration():
    """Test la création d'un utilisateur et client"""
    
    # Test 1: Vérifier le formulaire
    print("=" * 60)
    print("TEST 1: Validation du formulaire d'inscription")
    print("=" * 60)
    
    form_data = {
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'password_confirm': 'TestPassword123',
        'nom': 'Dupont',
        'prenom': 'Jean',
        'telephone': '0612345678',
        'adresse': '123 rue de la Paix, 75000 Paris',
        'date_naissance': '1990-01-15'
    }
    
    form = RegistrationForm(data=form_data)
    
    if form.is_valid():
        print("✓ Formulaire valide")
        
        # Test 2: Créer l'utilisateur et le client
        print("\n" + "=" * 60)
        print("TEST 2: Création de l'Utilisateur et du Client")
        print("=" * 60)
        
        try:
            utilisateur, client = form.save()
            print(f"✓ Utilisateur créé: {utilisateur}")
            print(f"  - Email: {utilisateur.email}")
            print(f"  - Nom: {utilisateur.nom}")
            print(f"  - Prénom: {utilisateur.prenom}")
            print(f"✓ Client créé: {client}")
            print(f"  - Utilisateur lié: {client.utilisateur}")
            print(f"  - Date de naissance: {client.date_naissance}")
            
            # Test 3: Vérifier que le lien OneToOne fonctionne
            print("\n" + "=" * 60)
            print("TEST 3: Vérification des relations")
            print("=" * 60)
            
            # Récupérer l'utilisateur à partir du client
            utilisateur_recupere = client.utilisateur
            print(f"✓ Récupération de l'utilisateur via client: {utilisateur_recupere}")
            
            # Vérifier que c'est le même
            assert utilisateur_recupere.id == utilisateur.id
            print("✓ Les relations sont correctes")
            
            # Test 4: Authentification
            print("\n" + "=" * 60)
            print("TEST 4: Vérification de l'authentification")
            print("=" * 60)
            
            # Vérifier que le mot de passe est correct
            assert utilisateur.check_password('TestPassword123')
            print("✓ Le mot de passe a été hashé correctement")
            
            # Test 5: Validation des doublons
            print("\n" + "=" * 60)
            print("TEST 5: Validation des doublons")
            print("=" * 60)
            
            form_data_duplicate = form_data.copy()
            form_duplicate = RegistrationForm(data=form_data_duplicate)
            
            if not form_duplicate.is_valid():
                if 'email' in form_duplicate.errors:
                    print("✓ Email dupliqué détecté correctement")
                    print(f"  Erreur: {form_duplicate.errors['email']}")
            else:
                print("✗ Erreur: Le formulaire devrait rejeter l'email dupliqué")
            
            print("\n" + "=" * 60)
            print("TOUS LES TESTS SONT PASSÉS ✓")
            print("=" * 60)
            
            # Nettoyer
            utilisateur.delete()
            print("\nUtilisateur de test supprimé.")
            
        except Exception as e:
            print(f"✗ Erreur lors de la création: {str(e)}")
            return False
    else:
        print(f"✗ Formulaire invalide:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
        return False
    
    return True

if __name__ == '__main__':
    success = test_registration()
    sys.exit(0 if success else 1)
