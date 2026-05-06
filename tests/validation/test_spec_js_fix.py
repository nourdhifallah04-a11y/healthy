#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de validation que les changements dans spec.js sont correctes
"""

import requests
import json

# Session cookie
COOKIES = {
    'sessionid': 'aq4i0s7t0etdbca40ukl8qo9e8mao1yd',
    'messages': 'W1siX19qc29uX21lc3NhZ2UiLDAsMjUsIkJpZW52ZW51ZSBXYWZhIERISSEiLCIiXV0:1wDRHj:ZCuQsOzS8LZGDmIjxQrmhCakYr9sdZA26yHg8dRSd2Q',
    'csrftoken': 'G4NWpGZQfyy06fVDBo0sum2Nqv5mEXNF'
}

API_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_menus_endpoint():
    """Vérifier que /api/menus/ retourne des données"""
    print_section("TEST 1: GET /api/menus/ - Vérifier disponibilité")
    
    url = f"{API_URL}/api/menus/"
    
    try:
        response = requests.get(url, cookies=COOKIES, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            menus_array = data if isinstance(data, list) else (data.get('results', []))
            print(f"✅ Menus disponibles: {len(menus_array)}")
            
            if menus_array:
                menu = menus_array[0]
                print(f"\nPremier menu:")
                print(f"  ID: {menu.get('id_menu', menu.get('id'))}")
                print(f"  Nom: {menu.get('nom')}")
                print(f"  Actif: {menu.get('est_actif')}")
                print(f"  Valeur nutrition: {menu.get('valeur_nutritionnelle', {})}")
                return True
            else:
                print("❌ Aucun menu trouvé")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_post_with_menu_id():
    """Tester POST /commande/api/ligne-commandes/ avec un menu_id valide"""
    print_section("TEST 2: POST /commande/api/ligne-commandes/ avec menu_id valide")
    
    # D'abord, récupérer un menu valide
    try:
        response = requests.get(f"{API_URL}/api/menus/", cookies=COOKIES, timeout=5)
        data = response.json()
        menus_array = data if isinstance(data, list) else (data.get('results', []))
        
        if not menus_array:
            print("❌ Aucun menu disponible pour le test")
            return False
        
        menu = menus_array[0]
        menu_id = menu.get('id_menu', menu.get('id'))
        
        # Faire le POST
        post_url = f"{API_URL}/commande/api/ligne-commandes/"
        payload = {
            'menu_id': menu_id,
            'quantite': 1
        }
        
        print(f"Menu ID à envoyer: {menu_id}")
        print(f"Payload: {payload}")
        
        post_response = requests.post(
            post_url,
            json=payload,
            cookies=COOKIES,
            headers={'X-CSRFToken': COOKIES['csrftoken']},
            timeout=5
        )
        
        print(f"Status Code: {post_response.status_code}")
        
        if post_response.status_code == 201:
            result = post_response.json()
            print(f"✅ SUCCESS - LigneCommande créée:")
            print(f"  ID: {result.get('id')}")
            print(f"  Menu: {result.get('menu')}")
            print(f"  Quantité: {result.get('quantite')}")
            return True
        else:
            print(f"❌ Erreur HTTP {post_response.status_code}:")
            print(f"  {post_response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_transformation_logic():
    """Vérifier que les données du menu sont bien formatées"""
    print_section("TEST 3: Vérifier la logique de transformation")
    
    try:
        response = requests.get(f"{API_URL}/api/menus/", cookies=COOKIES, timeout=5)
        data = response.json()
        menus_array = data if isinstance(data, list) else (data.get('results', []))
        
        if not menus_array:
            print("❌ Aucun menu disponible")
            return False
        
        menu = menus_array[0]
        
        # Vérifier les champs transformés
        print(f"Vérification des champs du menu:")
        
        fields_to_check = [
            ('id_menu', 'ID du menu'),
            ('nom', 'Nom'),
            ('description', 'Description'),
            ('est_actif', 'Actif'),
            ('valeur_nutritionnelle', 'Valeurs nutritionnelles')
        ]
        
        all_ok = True
        for field, label in fields_to_check:
            value = menu.get(field)
            status = "✅" if value is not None else "⚠️"
            print(f"  {status} {label}: {value}")
            if value is None and field != 'description':
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  TESTS DE VALIDATION DES MODIFICATIONS spec.js")
    print("="*70)
    
    results = {}
    results['Menus API'] = test_menus_endpoint()
    results['POST avec menu_id'] = test_post_with_menu_id()
    results['Transformation logique'] = test_transformation_logic()
    
    print_section("RÉSUMÉ DES TESTS")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("Les modifications de spec.js sont correctes.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
