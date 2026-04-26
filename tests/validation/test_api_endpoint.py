#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the API endpoint for ligne-commande
"""

import os
import sys
import django
import requests
from django.contrib.auth import get_user_model

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

# Add testserver to ALLOWED_HOSTS for testing
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from rest_framework.test import APIClient
from myapp.models import Client, Menu, Commande

Utilisateur = get_user_model()

def test_ligne_commande_post():
    """Test POST to /api/ligne-commande/"""
    
    # Create test user
    user, created = Utilisateur.objects.get_or_create(
        email='test_api@test.com',
        defaults={
            'nom': 'Test',
            'prenom': 'User',
            'est_actif': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Create test client
    client_obj, _ = Client.objects.get_or_create(utilisateur=user)
    
    # Create test commande
    commande, _ = Commande.objects.get_or_create(
        client=client_obj,
        defaults={'statut': 'en_cours'}
    )
    
    # Get first menu
    menu = Menu.objects.first()
    
    if not menu:
        print("❌ No menu found. Please create a menu first.")
        return
    
    # Create API client and authenticate
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    
    # Test POST
    print("\n" + "="*60)
    print("Testing POST /api/ligne-commande/")
    print("="*60)
    
    payload = {
        'menu_id': menu.id_menu,
        'quantite': 2
    }
    
    print(f"\nPayload: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 201:
        print("\n✅ SUCCESS: POST request worked!")
    else:
        print(f"\n❌ ERROR: Expected 201, got {response.status_code}")

if __name__ == '__main__':
    test_ligne_commande_post()
