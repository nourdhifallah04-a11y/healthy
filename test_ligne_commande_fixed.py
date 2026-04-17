#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test for POST /api/ligne-commande/ endpoint
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from myapp.models import Client, Menu, Commande, LigneCommande

Utilisateur = get_user_model()

def print_test(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_ligne_commande_post_authenticated():
    """Test POST /api/ligne-commande/ with authenticated user"""
    print_test("TEST 1: POST with Authenticated User")
    
    # Setup
    user, _ = Utilisateur.objects.get_or_create(
        email='test_ligne@example.com',
        defaults={'nom': 'Test', 'prenom': 'User', 'est_actif': True}
    )
    user.set_password('testpass123')
    user.save()
    
    client_obj, _ = Client.objects.get_or_create(utilisateur=user)
    menu = Menu.objects.first()
    
    if not menu:
        print("❌ No menu available. Skipping test.")
        return False
    
    # Create API client and authenticate
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    
    # Test POST
    payload = {
        'menu_id': menu.id_menu,
        'quantite': 2
    }
    
    print(f"User: {user.email}")
    print(f"Menu ID: {menu.id_menu} (Primary Key)")
    print(f"Payload: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 201:
        print("✅ SUCCESS: POST created LigneCommande (201)")
        return True
    else:
        print(f"❌ FAILED: Expected 201, got {response.status_code}")
        return False

def test_ligne_commande_post_unauthenticated():
    """Test POST /api/ligne-commande/ without authentication"""
    print_test("TEST 2: POST without Authentication")
    
    api_client = APIClient()
    menu = Menu.objects.first()
    
    if not menu:
        print("❌ No menu available. Skipping test.")
        return False
    
    payload = {
        'menu_id': menu.id_menu,
        'quantite': 1
    }
    
    print(f"Payload: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code in [401, 403]:
        print(f"✅ SUCCESS: Correctly rejected unauthenticated request ({response.status_code})")
        return True
    else:
        print(f"❌ FAILED: Expected 401 or 403, got {response.status_code}")
        return False

def test_ligne_commande_invalid_menu():
    """Test POST /api/ligne-commande/ with invalid menu_id"""
    print_test("TEST 3: POST with Invalid Menu ID")
    
    # Setup
    user, _ = Utilisateur.objects.get_or_create(
        email='test_invalid@example.com',
        defaults={'nom': 'Test', 'prenom': 'Invalid', 'est_actif': True}
    )
    user.set_password('testpass123')
    user.save()
    
    Client.objects.get_or_create(utilisateur=user)
    
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    
    payload = {
        'menu_id': 99999,  # Non-existent menu
        'quantite': 1
    }
    
    print(f"Payload: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 404:
        print("✅ SUCCESS: Correctly returned 404 for invalid menu")
        return True
    else:
        print(f"❌ FAILED: Expected 404, got {response.status_code}")
        return False

def test_ligne_commande_missing_menu_id():
    """Test POST /api/ligne-commande/ without menu_id"""
    print_test("TEST 4: POST without menu_id Parameter")
    
    # Setup
    user, _ = Utilisateur.objects.get_or_create(
        email='test_missing@example.com',
        defaults={'nom': 'Test', 'prenom': 'Missing', 'est_actif': True}
    )
    user.set_password('testpass123')
    user.save()
    
    Client.objects.get_or_create(utilisateur=user)
    
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    
    payload = {
        'quantite': 1
        # menu_id is missing
    }
    
    print(f"Payload: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 400:
        print("✅ SUCCESS: Correctly rejected missing menu_id (400)")
        return True
    else:
        print(f"❌ FAILED: Expected 400, got {response.status_code}")
        return False

def test_ligne_commande_invalid_quantity():
    """Test POST /api/ligne-commande/ with invalid quantite"""
    print_test("TEST 5: POST with Invalid Quantity")
    
    # Setup
    user, _ = Utilisateur.objects.get_or_create(
        email='test_qty@example.com',
        defaults={'nom': 'Test', 'prenom': 'Quantity', 'est_actif': True}
    )
    user.set_password('testpass123')
    user.save()
    
    Client.objects.get_or_create(utilisateur=user)
    menu = Menu.objects.first()
    
    if not menu:
        print("❌ No menu available. Skipping test.")
        return False
    
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    
    payload = {
        'menu_id': menu.id_menu,
        'quantite': -5  # Invalid negative quantity
    }
    
    print(f"Payload: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.data}")
    
    if response.status_code == 400:
        print("✅ SUCCESS: Correctly rejected invalid quantity (400)")
        return True
    else:
        print(f"❌ FAILED: Expected 400, got {response.status_code}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("  RUNNING COMPREHENSIVE TESTS FOR /api/ligne-commande/")
    print("="*70)
    
    results = {
        'Authenticated User': test_ligne_commande_post_authenticated(),
        'Unauthenticated User': test_ligne_commande_post_unauthenticated(),
        'Invalid Menu ID': test_ligne_commande_invalid_menu(),
        'Missing menu_id': test_ligne_commande_missing_menu_id(),
        'Invalid Quantity': test_ligne_commande_invalid_quantity(),
    }
    
    print_test("TEST RESULTS SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
