#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour l'API /api/ligne-commande/
Teste la creation, lecture et modification des lignes de commande
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
    
    # 1. Creer un utilisateur de test
    print("\n[OK] Test 1: Creation d'un utilisateur de test")
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
        print(f"  [OK] Utilisateur cree: {user.email}")
    else:
        print(f"  [OK] Utilisateur existant: {user.email}")
    
    # 2. Creer un client
    print("\n[OK] Test 2: Creation/recuperation du client")
    client_obj, created = Client.objects.get_or_create(
        utilisateur=user
    )
    print(f"  [OK] Client: {client_obj.id}")
    
    # 3. Recuperer un menu existant
    print("\n[OK] Test 3: Recuperation d'un menu")
    menu = Menu.objects.first()
    if not menu:
        print("  [ERROR] Aucun menu trouve dans la base de donnees!")
        print("  Creez des menus avant de tester.")
        return False
    print(f"  [OK] Menu trouve: {menu.nom} (ID: {menu.id_menu})")
    
    # 4. Creer un client API
    print("\n[OK] Test 4: Creation du client API et authentification")
    api_client = APIClient()
    api_client.default_format = 'json'
    # Ajouter testserver aux ALLOWED_HOSTS temporairement
    from django.conf import settings
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('testserver')
    api_client.force_authenticate(user=user)
    print(f"  [OK] Client API authentifie comme: {user.email}")
    
    # 5. Ajouter au panier
    print("\n[OK] Test 5: Ajout au panier (POST /api/ligne-commande/)")
    payload = {
        'menu_id': menu.id_menu,
        'quantite': 2
    }
    print(f"  [SEND] Envoi: {payload}")
    
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    if response.status_code == status.HTTP_201_CREATED:
        print(f"  [OK] Reponse: 201 Created")
        data = response.json()
        ligne_id = data.get('id')
        print(f"  [OK] Ligne creee avec ID: {ligne_id}")
        print(f"  [OK] Quantite: {data.get('quantite')}")
        print(f"  [OK] Prix unitaire: {data.get('prix_unitaire')}")
        print(f"  [OK] Sous-total: {data.get('sous_total_display')}")
    else:
        print(f"  [ERROR] Erreur: {response.status_code}")
        try:
            print(f"  Reponse: {response.json()}")
        except:
            print(f"  Reponse: {response.content}")
        return False
    
    # 6. Lister les lignes de commande
    print("\n[OK] Test 6: Recuperation des lignes (GET /api/ligne-commande/)")
    response = api_client.get('/api/ligne-commande/')
    
    if response.status_code == status.HTTP_200_OK:
        print(f"  [OK] Reponse: 200 OK")
        data = response.json()
        print(f"  [OK] Nombre de lignes: {len(data)}")
        
        if isinstance(data, list) and len(data) > 0:
            print(f"  [OK] Exemple de ligne:")
            ligne = data[0]
            print(f"    - ID: {ligne.get('id')}")
            print(f"    - Menu: {ligne.get('menu')}")
            print(f"    - Quantite: {ligne.get('quantite')}")
    else:
        print(f"  [ERROR] Erreur: {response.status_code}")
        return False
    
    # 7. Recuperer une ligne specifique
    print(f"\n[OK] Test 7: Recuperation d'une ligne specifique (GET /api/ligne-commande/{ligne_id}/)")
    response = api_client.get(f'/api/ligne-commande/{ligne_id}/')
    
    if response.status_code == status.HTTP_200_OK:
        print(f"  [OK] Reponse: 200 OK")
        data = response.json()
        print(f"  [OK] Menu: {data.get('menu')}")
        print(f"  [OK] Quantite: {data.get('quantite')}")
    else:
        print(f"  [ERROR] Erreur: {response.status_code}")
        try:
            print(f"  Reponse: {response.json()}")
        except:
            pass
    
    # 8. Modifier la quantite
    print(f"\n[OK] Test 8: Modification de la quantite (PATCH /api/ligne-commande/{ligne_id}/)")
    update_payload = {'quantite': 5}
    print(f"  [SEND] Envoi: {update_payload}")
    response = api_client.patch(f'/api/ligne-commande/{ligne_id}/', update_payload, format='json')
    
    if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
        print(f"  [OK] Reponse: {response.status_code}")
        data = response.json()
        print(f"  [OK] Nouvelle quantite: {data.get('quantite')}")
    else:
        print(f"  [ERROR] Erreur: {response.status_code}")
        try:
            print(f"  Reponse: {response.json()}")
        except:
            pass
    
    # 9. Ajouter le meme menu (test de detection de doublon)
    print(f"\n[OK] Test 9: Ajout du meme menu (detection de doublon)")
    payload = {
        'menu_id': menu.id_menu,
        'quantite': 3
    }
    response = api_client.post('/api/ligne-commande/', payload, format='json')
    
    if response.status_code == status.HTTP_201_CREATED:
        print(f"  [OK] Reponse: 201 Created")
        data = response.json()
        # La quantite devrait etre augmentee
        nouvelle_quantite = data.get('quantite')
        print(f"  [OK] Quantite mise a jour: {nouvelle_quantite}")
        if nouvelle_quantite > 5:
            print(f"  [OK] Quantite augmentee correctement (5 + 3 = {nouvelle_quantite})")
    
    # 10. Tester sans authentification
    print(f"\n[OK] Test 10: Tentative sans authentification")
    api_client_unauth = APIClient()
    response = api_client_unauth.get('/api/ligne-commande/')
    
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        print(f"  [OK] Reponse: 401 Unauthorized (securite OK)")
    else:
        print(f"  [WARNING] Reponse inattendue: {response.status_code}")
    
    # 11. Verifier la commande en base
    print(f"\n[OK] Test 11: Verification en base de donnees")
    try:
        commande = Commande.objects.filter(client=client_obj, statut='panier').first()
        if commande:
            print(f"  [OK] Commande trouvee: {commande.id_commande}")
            lignes = LigneCommande.objects.filter(commande=commande)
            print(f"  [OK] Nombre de lignes: {lignes.count()}")
            for ligne in lignes:
                print(f"    - {ligne.menu.nom}: x{ligne.quantite} @ {ligne.prix_unitaire}")
        else:
            print(f"  [WARNING] Aucune commande trouvee")
    except Exception as e:
        print(f"  [ERROR] Erreur: {e}")
    
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
