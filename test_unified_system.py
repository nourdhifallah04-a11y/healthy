#!/usr/bin/env python
"""
Test script for unified menu and plats functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, r'c:\Users\achra\Desktop\wockspace\healthy')
django.setup()

from myapp.models import Menu, Plat, LigneCommande, Commande, Client, Utilisateur
from myapp.serializers import UnifiedMenuItemSerializer

print("=" * 60)
print("TESTING UNIFIED MENU SYSTEM")
print("=" * 60)

# Test 1: Check if Menus and Plats exist
print("\n1. Checking available items...")
menus = Menu.objects.filter(est_actif=True)
plats = Plat.objects.filter(est_disponible=True)

print(f"   ✓ Active Menus: {menus.count()}")
print(f"   ✓ Available Plats: {plats.count()}")

# Test 2: Check diet categories
print("\n2. Testing diet category detection...")
if menus.exists():
    menu = menus.first()
    print(f"   Menu: {menu.nom}")
    print(f"   Diet Category: {menu.diet_category}")
    auto_category = menu.get_diet_category()
    print(f"   Auto-detected category: {auto_category}")

if plats.exists():
    plat = plats.first()
    print(f"   Plat: {plat.nom}")
    categories = plat.get_diet_categories()
    print(f"   Diet Categories: {categories}")

# Test 3: Test serializers
print("\n3. Testing UnifiedMenuItemSerializer...")
if menus.exists():
    menu = menus.first()
    serializer = UnifiedMenuItemSerializer(menu)
    print(f"   Menu Item:")
    print(f"     - ID: {serializer.data.get('id')}")
    print(f"     - Type: {serializer.data.get('type')}")
    print(f"     - Name: {serializer.data.get('nom')}")
    print(f"     - Diet Categories: {serializer.data.get('diet_categories')}")

if plats.exists():
    plat = plats.first()
    serializer = UnifiedMenuItemSerializer(plat)
    print(f"   Plat Item:")
    print(f"     - ID: {serializer.data.get('id')}")
    print(f"     - Type: {serializer.data.get('type')}")
    print(f"     - Name: {serializer.data.get('nom')}")
    print(f"     - Diet Categories: {serializer.data.get('diet_categories')}")

# Test 4: Test LigneCommande with both Menu and Plat
print("\n4. Testing LigneCommande model changes...")
try:
    # Get or create a user and client
    utilisateur, _ = Utilisateur.objects.get_or_create(
        email='test@example.com',
        defaults={'nom': 'Test', 'prenom': 'User', 'is_active': True}
    )
    client, _ = Client.objects.get_or_create(utilisateur=utilisateur)
    
    # Get or create a commande
    commande, _ = Commande.objects.get_or_create(
        client=client,
        statut='panier'
    )
    
    # Test creating a LigneCommande with Plat
    if plats.exists():
        plat = plats.first()
        ligne, created = LigneCommande.objects.get_or_create(
            commande=commande,
            plat=plat,
            menu=None,
            defaults={'quantite': 1, 'prix_unitaire': plat.prix}
        )
        print(f"   ✓ LigneCommande with Plat:")
        print(f"     - Item Type: {ligne.get_item_type()}")
        print(f"     - Item Name: {ligne.get_item_name()}")
        print(f"     - Created: {created}")
    
    # Test creating a LigneCommande with Menu
    if menus.exists():
        menu = menus.first()
        menu_vals = menu.calculer_valeur_nutritionnelle_totale()
        ligne2, created2 = LigneCommande.objects.get_or_create(
            commande=commande,
            menu=menu,
            plat=None,
            defaults={'quantite': 1, 'prix_unitaire': menu_vals.get('prix', 0)}
        )
        print(f"   ✓ LigneCommande with Menu:")
        print(f"     - Item Type: {ligne2.get_item_type()}")
        print(f"     - Item Name: {ligne2.get_item_name()}")
        print(f"     - Created: {created2}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED!")
print("=" * 60)
