#!/usr/bin/env python
"""
Script de test pour l'endpoint webhook n8n
Usage: python test_n8n_webhook.py --help
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, Dict, Any


class N8nWebhookTester:
    """Classe pour tester l'endpoint webhook N8N"""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 n8n_url: str = "http://192.168.1.184:5678/webhook/reco-nutrition",
                 token: Optional[str] = None):
        self.base_url = base_url
        self.n8n_url = n8n_url
        self.token = token
        self.endpoint = f"{base_url}/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/"
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
        else:
            self.session.headers.update({
                "Content-Type": "application/json"
            })
    
    def test_n8n_connectivity(self) -> bool:
        """Teste si le webhook N8N est accessible"""
        print(f"\n[TEST] Vérification de la connectivité N8N: {self.n8n_url}")
        try:
            # Envoyer un test ping vide
            response = requests.post(
                self.n8n_url,
                json={"test": True},
                timeout=5
            )
            if response.status_code in [200, 400, 422]:
                print("✅ N8N est accessible")
                return True
            else:
                print(f"⚠️  N8N retourne un code inattendu: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ N8N n'est pas accessible: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
            return False
    
    def test_endpoint_without_auth(self) -> None:
        """Teste l'endpoint sans authentification"""
        print(f"\n[TEST] Appel sans authentification")
        try:
            response = requests.post(
                self.endpoint,
                json={},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 401:
                print("✅ L'endpoint retourne correctement 401 (non authentifié)")
            else:
                print(f"⚠️  Code inattendu: {response.status_code}")
                print(f"   Réponse: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
    
    def test_endpoint_with_invalid_profile(self) -> None:
        """Teste l'endpoint avec un profil invalide"""
        print(f"\n[TEST] Appel avec profil_id invalide")
        try:
            response = self.session.post(
                self.endpoint,
                json={"profil_id": 99999}
            )
            if response.status_code == 404:
                print("✅ L'endpoint retourne correctement 404 (profil non trouvé)")
                print(f"   Message: {response.json().get('error', 'N/A')}")
            else:
                print(f"⚠️  Code inattendu: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
    
    def test_endpoint_success(self, profil_id: Optional[int] = None) -> Dict[str, Any]:
        """Teste l'endpoint avec un appel valide"""
        print(f"\n[TEST] Appel nominal avec profil_id={profil_id}")
        payload = {}
        if profil_id:
            payload["profil_id"] = profil_id
        
        try:
            response = self.session.post(
                self.endpoint,
                json=payload
            )
            
            print(f"Status: {response.status_code}")
            
            try:
                data = response.json()
                print(f"Response:\n{json.dumps(data, indent=2)}")
                
                if response.status_code == 200 and data.get('success'):
                    print("\n✅ Appel réussi!")
                    return data
                elif response.status_code == 404:
                    print("\n⚠️  Profil non trouvé - créez d'abord un profil")
                elif response.status_code == 503:
                    print("\n❌ N8N n'est pas accessible")
                else:
                    print(f"\n⚠️  Erreur: {data.get('error', 'Erreur inconnue')}")
            except json.JSONDecodeError:
                print(f"⚠️  Réponse non-JSON:\n{response.text}")
            
            return {"success": False, "status_code": response.status_code}
        
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self, profil_id: Optional[int] = None) -> None:
        """Exécute tous les tests"""
        print("="*60)
        print("TESTS DE L'ENDPOINT WEBHOOK N8N")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"  Endpoint: {self.endpoint}")
        print(f"  N8N Webhook: {self.n8n_url}")
        print(f"  Authentification: {'Oui (Token)' if self.token else 'Non'}")
        
        # Tests
        n8n_ok = self.test_n8n_connectivity()
        
        if not self.token:
            print("\n⚠️  Pas de token fourni, tests limités")
            self.test_endpoint_without_auth()
        else:
            self.test_endpoint_with_invalid_profile()
            if n8n_ok:
                self.test_endpoint_success(profil_id)
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Tester l'endpoint webhook N8N",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Test basique
  python test_n8n_webhook.py --token YOUR_TOKEN
  
  # Test avec profil spécifique
  python test_n8n_webhook.py --token YOUR_TOKEN --profil-id 1
  
  # Test N8N uniquement
  python test_n8n_webhook.py --test-n8n
        """
    )
    
    parser.add_argument(
        '--base-url',
        default='http://localhost:8000',
        help='URL de base du serveur Django (défaut: http://localhost:8000)'
    )
    parser.add_argument(
        '--n8n-url',
        default='http://192.168.1.184:5678/webhook/reco-nutrition',
        help='URL du webhook N8N (défaut: http://192.168.1.184:5678/webhook/reco-nutrition)'
    )
    parser.add_argument(
        '--token',
        help='Token JWT pour l\'authentification'
    )
    parser.add_argument(
        '--profil-id',
        type=int,
        help='ID du profil à tester (optionnel)'
    )
    parser.add_argument(
        '--test-n8n',
        action='store_true',
        help='Tester uniquement la connectivité N8N'
    )
    
    args = parser.parse_args()
    
    # Créer le testeur
    tester = N8nWebhookTester(
        base_url=args.base_url,
        n8n_url=args.n8n_url,
        token=args.token
    )
    
    if args.test_n8n:
        tester.test_n8n_connectivity()
    else:
        if not args.token:
            print("⚠️  Token non fourni. Utilisez --token pour tester pleinement.")
            print("   Les tests seront limités aux vérifications publiques.\n")
        tester.run_all_tests(args.profil_id)


if __name__ == '__main__':
    main()
