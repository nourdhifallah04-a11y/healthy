#!/usr/bin/env python
"""
MASTER TEST SUITE - Lance tous les tests des calculs de score
"""

import os
import sys
import subprocess

def run_test(test_file, test_name):
    """Exécute un test et affiche les résultats"""
    print("\n" + "=" * 80)
    print(f"▶️  Exécution: {test_name}")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print(f"✅ {test_name} - RÉUSSI")
            return True
        else:
            print(f"❌ {test_name} - ÉCHOUÉ (code {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {test_name} - ERREUR: {e}")
        return False

def main():
    """Menu principal"""
    tests = [
        ('test_1_score_simple.py', 'TEST 1: Score Simple (Plat)'),
        ('test_2_score_recommendation_imc.py', 'TEST 2: Score Recommandation (IMC)'),
        ('test_3_restrictions.py', 'TEST 3: Allergies et Restrictions'),
        ('test_4_age_sexe.py', 'TEST 4: Facteurs d\'Âge et Sexe'),
        ('test_5_performance_cache.py', 'TEST 5: Performance et Cache'),
        ('test_6_integration_menus.py', 'TEST 6: Intégration Menus/Profils'),
    ]
    
    print("\n" + "=" * 80)
    print("🧪 SUITE DE TESTS COMPLÈTE - CALCULS DE SCORE NUTRITIONNEL")
    print("=" * 80)
    print("\nOptions:")
    print("  1. Lancer TOUS les tests")
    print("  2. Lancer un test spécifique")
    print("  3. Afficher la liste des tests")
    print("  4. Quitter")
    
    while True:
        choice = input("\nChoisir une option (1-4): ").strip()
        
        if choice == '1':
            print("\n🚀 Lancement de tous les tests...")
            results = []
            for test_file, test_name in tests:
                if os.path.exists(test_file):
                    success = run_test(test_file, test_name)
                    results.append((test_name, success))
                else:
                    print(f"⚠️  {test_file} non trouvé")
                    results.append((test_name, False))
            
            # Résumé
            print("\n" + "=" * 80)
            print("📊 RÉSUMÉ GLOBAL")
            print("=" * 80)
            passed = sum(1 for _, success in results if success)
            total = len(results)
            print(f"\nTests réussis: {passed}/{total}")
            
            for test_name, success in results:
                status = "✅" if success else "❌"
                print(f"{status} {test_name}")
            
            if passed == total:
                print(f"\n🎉 TOUS LES TESTS SONT PASSÉS!")
            else:
                print(f"\n⚠️  {total - passed} test(s) échoué(s)")
            
            break
        
        elif choice == '2':
            print("\nTests disponibles:")
            for i, (test_file, test_name) in enumerate(tests, 1):
                print(f"  {i}. {test_name}")
            
            try:
                test_num = int(input("\nChoisir un test (numéro): ").strip())
                if 1 <= test_num <= len(tests):
                    test_file, test_name = tests[test_num - 1]
                    if os.path.exists(test_file):
                        run_test(test_file, test_name)
                    else:
                        print(f"❌ {test_file} non trouvé")
                else:
                    print("❌ Numéro invalide")
            except ValueError:
                print("❌ Entrée invalide")
        
        elif choice == '3':
            print("\n📋 LISTE DES TESTS:")
            print("\nTEST 1: Score Simple (Plat)")
            print("  - Teste les calculs de score nutritionnel simple")
            print("  - 5 cas: sain, gras, équilibré, bas-protéine, haute-protéine")
            print("  - Vérifie les seuils attendus et les performances du cache")
            
            print("\nTEST 2: Score Recommandation (IMC)")
            print("  - Teste les scores par catégorie IMC")
            print("  - 4 catégories: insuffisance pondérale, normal, surpoids, obésité")
            print("  - Vérifie que les plats sont bien classés pour chaque profil")
            
            print("\nTEST 3: Allergies et Restrictions")
            print("  - Teste la détection des allergies et restrictions")
            print("  - 4 restrictions: végétarien, vegan, sans gluten, sans lactose")
            print("  - Vérifie que les plats incompatibles sont bien rejetés (score 0)")
            
            print("\nTEST 4: Facteurs d'Âge et Sexe")
            print("  - Teste l'influence de l'âge et du sexe sur les scores")
            print("  - 6 profils: femmes/hommes jeunes, adultes, seniors")
            print("  - Vérifie les bonnes recommandations par profil")
            
            print("\nTEST 5: Performance et Cache")
            print("  - Teste la performance du système de cache")
            print("  - 100+ calculs par plat")
            print("  - Mesure le speedup (10-100x plus rapide en cache)")
            
            print("\nTEST 6: Intégration Menus/Profils")
            print("  - Teste l'intégration avec les menus et profils nutritionnels")
            print("  - Crée des clients avec différents profils")
            print("  - Calcule les scores et recommandations réalistes")
        
        elif choice == '4':
            print("\nAu revoir! 👋")
            break
        
        else:
            print("❌ Option invalide")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterruption par l'utilisateur")
        sys.exit(0)
