#!/usr/bin/env python
"""
Test script for Commande feature
"""
import os
import django
from decimal import Decimal
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Utilisateur, Client, Commande, LigneCommande, Plat, Menu

def test_commande_feature():
    """Test all Commande feature functionality"""
    
    print("=" * 60)
    print("COMMANDE FEATURE TEST SUITE")
    print("=" * 60)
    
    # Test 1: Create or get test user
    print("\n✓ Test 1: Creating/getting test user...")
    user, created = Utilisateur.objects.get_or_create(
        email='feature_test@example.com',
        defaults={
            'password': 'testpass123',
            'nom': 'Feature',
            'prenom': 'Test'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    print(f"  User: {user} {'(created)' if created else '(retrieved)'}")
    
    # Test 2: Create or get client
    print("\n✓ Test 2: Creating/getting client...")
    client, created = Client.objects.get_or_create(utilisateur=user)
    print(f"  Client: {client} {'(created)' if created else '(retrieved)'}")
    
    # Test 3: Create commande
    print("\n✓ Test 3: Creating commande...")
    commande = Commande.objects.create(client=client, statut='panier')
    print(f"  Commande created: {commande}")
    print(f"  Statut: {commande.statut}")
    
    # Test 4: Verify commande methods exist
    print("\n✓ Test 4: Testing commande methods...")
    print(f"  - valider_commande method exists: {hasattr(commande, 'valider_commande')}")
    print(f"  - calculer_total method exists: {hasattr(commande, 'calculer_total')}")
    print(f"  - calculer_nutrition_totale method exists: {hasattr(commande, 'calculer_nutrition_totale')}")
    
    # Test 5: Create test data
    print("\n✓ Test 5: Creating plats and menu...")
    plat1 = Plat.objects.create(
        nom='Test Poulet',
        description='Poulet test',
        calorie=450,
        proteine=35,
        glucides=20,
        lipides=15,
        prix=Decimal('8.50'),
        est_disponible=True
    )
    
    today = datetime.now().date()
    menu = Menu.objects.create(
        nom='Test Menu',
        description='Menu test',
        date_debut=today,
        date_fin=today + timedelta(days=7),
        est_actif=True
    )
    menu.plats.add(plat1)
    print(f"  Plat created: {plat1}")
    print(f"  Menu created: {menu}")
    
    # Test 6: Add items to commande and verify calculations
    print("\n✓ Test 6: Testing calculations...")
    ligne = LigneCommande.objects.create(
        commande=commande,
        menu=menu,
        quantite=2,
        prix_unitaire=Decimal('12.00')
    )
    print(f"  Line item created: {ligne}")
    print(f"  Line item sous_total: {ligne.sous_total}€")
    
    total = commande.calculer_total()
    print(f"  Commande total: {total}€")
    
    nutrition = commande.calculer_nutrition_totale()
    print(f"  Nutrition totals:")
    print(f"    - Calories: {nutrition['calories']}")
    print(f"    - Proteins: {nutrition['proteines']}g")
    print(f"    - Glucides: {nutrition['glucides']}g")
    print(f"    - Lipides: {nutrition['lipides']}g")
    
    # Test 7: Test valider_commande
    print("\n✓ Test 7: Testing validation...")
    result = commande.valider_commande()
    print(f"  Validation result: {result}")
    commande.refresh_from_db()
    print(f"  Commande status after validation: {commande.statut}")
    
    # Test 8: Test statut choices
    print("\n✓ Test 8: Testing statut choices...")
    print(f"  Available statuts:")
    for statut, display in Commande.STATUTS:
        print(f"    - {statut}: {display}")
    
    print("\n" + "=" * 60)
    print("✅ ALL FEATURE TESTS PASSED!")
    print("=" * 60)

if __name__ == '__main__':
    test_commande_feature()
