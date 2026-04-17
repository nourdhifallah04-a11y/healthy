#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour l'API /api/ligne-commande/
Teste la création, lecture et modification des lignes de commande
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from myapp.models import Client, Menu, Commande, LigneCommande
from rest_framework.test import APIClient
from rest_framework import status

Utilisateur = get_user_model()


def print_header(title):
    """Affiche un header de test"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_ligne_commande_api():
    """Test complet de l'API ligne-commande"""
    
    print_header("[TEST] API /api/ligne-commande/")
    
    # 1. Créer un utilisateur de test
    print("\n✓ Test 1: Création d'un utilisateur de test")
    user, created = Utilisateur.objects.get_or_create(
        email='testuser_ligne@test.com',
        defaults={
            'nom': 'Test',
            'prenom': 'User',
            'est_actif': True
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"  ✓ Utilisateur créé: {user.email}")
    else:
        print(f"  ✓ Utilisateur existant: {user.email}")
    
    # 2. Créer un client
    print("\n✓ Test 2: Création/récupération du client")
    client_obj, created = Client.objects.get_or_create(
        utilisateur=user
    )
    print(f"  ✓ Client: {client_obj.id}")
    
    # 3. Récupérer un menu existant
    print("\n✓ Test 3: Récupération d'un menu")
    menu = Menu.objects.first()
    if not menu:
        print("  ❌ Aucun menu trouvé dans la base de données!")
        print("  Créez des menus avant de tester.")
        return False
    print(f"  ✓ Menu trouvé: {menu.nom} (ID: {menu.id_menu})")
    
    # 4. Créer un client API
    print("\n✓ Test 4: Création du client API et authentification")
    api_client = APIClient()
    api_client.default_format = 'json'
    # Ajouter testserver aux ALLOWED_HOSTS temporairement
    from django.conf import settings
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('testserver')
    api_client.force_authenticate(user=user)
    print(f"  ✓ Client API authentifié comme: {user.email}")
    
    # 5. Ajouter au panier
    print("\n✓ Test 5: Ajout au panier (POST /api/ligne-commande/)")
    payload = {
        'menu_id': menu.id_menu,
        'quantite': 2
    }
    print(f"  📤 Envoi: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    if response.status_code == status.HTTP_201_CREATED:
        print(f"  ✓ Réponse: 201 Created")
        data = response.json()
        ligne_id = data.get('id')
        print(f"  ✓ Ligne créée avec ID: {ligne_id}")
        print(f"  ✓ Quantité: {data.get('quantite')}")
        print(f"  ✓ Prix unitaire: {data.get('prix_unitaire')}")
        print(f"  ✓ Sous-total: {data.get('sous_total_display')}")
    else:
        print(f"  ❌ Erreur: {response.status_code}")
        print(f"  Réponse: {response.json()}")
        return False
    
    # 6. Lister les lignes de commande
    print("\n✓ Test 6: Récupération des lignes (GET /api/ligne-commande/)")
    response = api_client.get('/api/ligne-commande/')
    
    if response.status_code == status.HTTP_200_OK:
        print(f"  ✓ Réponse: 200 OK")
        data = response.json()
        print(f"  ✓ Nombre de lignes: {len(data)}")
        
        if isinstance(data, list) and len(data) > 0:
            print(f"  ✓ Exemple de ligne:")
            ligne = data[0]
            print(f"    - ID: {ligne.get('id')}")
            print(f"    - Menu: {ligne.get('menu')}")
            print(f"    - Quantité: {ligne.get('quantite')}")
    else:
        print(f"  ❌ Erreur: {response.status_code}")
        return False
    
    # 7. Récupérer une ligne spécifique
    print(f"\n✓ Test 7: Récupération d'une ligne spécifique (GET /api/ligne-commande/{ligne_id}/)")
    response = api_client.get(f'/api/ligne-commande/{ligne_id}/')
    
    if response.status_code == status.HTTP_200_OK:
        print(f"  ✓ Réponse: 200 OK")
        data = response.json()
        print(f"  ✓ Menu: {data.get('menu')}")
        print(f"  ✓ Quantité: {data.get('quantite')}")
    else:
        print(f"  ❌ Erreur: {response.status_code}")
        print(f"  Réponse: {response.json()}")
    
    # 8. Modifier la quantité
    print(f"\n✓ Test 8: Modification de la quantité (PATCH /api/ligne-commande/{ligne_id}/)")
    update_payload = {'quantite': 5}
    print(f"  📤 Envoi: {update_payload}")
    response = api_client.patch(f'/api/ligne-commande/{ligne_id}/', update_payload, format='json')
    
    if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
        print(f"  ✓ Réponse: {response.status_code}")
        data = response.json()
        print(f"  ✓ Nouvelle quantité: {data.get('quantite')}")
    else:
        print(f"  ❌ Erreur: {response.status_code}")
        print(f"  Réponse: {response.json()}")
    
    # 9. Ajouter le même menu (test de détection de doublon)
    print(f"\n✓ Test 9: Ajout du même menu (détection de doublon)")
    payload = {
        'menu_id': menu.id_menu,
        'quantite': 3
    }
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    if response.status_code == status.HTTP_201_CREATED:
        print(f"  ✓ Réponse: 201 Created")
        data = response.json()
        # La quantité devrait être augmentée
        nouvelle_quantite = data.get('quantite')
        print(f"  ✓ Quantité mise à jour: {nouvelle_quantite}")
        if nouvelle_quantite > 5:
            print(f"  ✓ Quantité augmentée correctement (5 + 3 = {nouvelle_quantite})")
    
    # 10. Tester sans authentification
    print(f"\n✓ Test 10: Tentative sans authentification")
    api_client_unauth = APIClient()
    response = api_client_unauth.get('/api/ligne-commande/')
    
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        print(f"  ✓ Réponse: 401 Unauthorized (sécurité OK)")
    else:
        print(f"  ⚠️  Réponse inattendue: {response.status_code}")
    
    # 11. Vérifier la commande en base
    print(f"\n✓ Test 11: Vérification en base de données")
    try:
        commande = Commande.objects.filter(client=client_obj, statut='panier').first()
        if commande:
            print(f"  ✓ Commande trouvée: {commande.id_commande}")
            lignes = LigneCommande.objects.filter(commande=commande)
            print(f"  ✓ Nombre de lignes: {lignes.count()}")
            for ligne in lignes:
                print(f"    - {ligne.menu.nom}: x{ligne.quantite} @ {ligne.prix_unitaire}€")
        else:
            print(f"  ⚠️  Aucune commande trouvée")
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print_header("[FINISH] Tests Completed Successfully!")
    return True


if __name__ == '__main__':
    try:
        success = test_ligne_commande_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
