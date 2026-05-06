#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test POST /commande/api/ligne-commandes/ using provided session cookie
"""

import requests
import json

# Your session cookie
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

def test_get_ligne_commande():
    """Test GET /commande/api/ligne-commandes/"""
    print_section("TEST 1: GET /commande/api/ligne-commandes/ with Cookie")
    
    url = f"{API_URL}/commande/api/ligne-commandes/"
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': COOKIES['csrftoken']
    }
    
    try:
        response = requests.get(url, cookies=COOKIES, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_post_ligne_commande():
    """Test POST /commande/api/ligne-commandes/"""
    print_section("TEST 2: POST /commande/api/ligne-commandes/ with Cookie")
    
    url = f"{API_URL}/commande/api/ligne-commandes/"
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': COOKIES['csrftoken']
    }
    
    # Payload - adjust menu_id as needed
    payload = {
        'menu_id': 1,
        'quantite': 2
    }
    
    try:
        print(f"URL: {url}")
        print(f"Payload: {payload}")
        print(f"Cookies: {COOKIES}")
        
        response = requests.post(url, json=payload, cookies=COOKIES, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: LigneCommande created!")
            return True
        else:
            print("❌ FAILED: Unexpected status code")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_without_cookie():
    """Test POST without cookie to verify auth is required"""
    print_section("TEST 3: POST without Cookie (should fail)")
    
    url = f"{API_URL}/commande/api/ligne-commandes/"
    payload = {
        'menu_id': 1,
        'quantite': 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code in [401, 403]:
            print("✅ Correctly rejected unauthenticated request")
            return True
        else:
            print("❌ Should have been rejected")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  TESTING /commande/api/ligne-commandes/ WITH PROVIDED COOKIE")
    print("="*70)
    
    results = {}
    results['GET'] = test_get_ligne_commande()
    results['POST'] = test_post_ligne_commande()
    results['Without Auth'] = test_without_cookie()
    
    print_section("SUMMARY")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
