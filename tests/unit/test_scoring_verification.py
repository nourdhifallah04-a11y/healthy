#!/usr/bin/env python
"""
Test complet du système de scoring.
Vérifie que tous les types de scores fonctionnent correctement.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.models import Utilisateur, Client, ProfilNutritionnel, Plat, Menu
from myapp.monitoring.score_monitoring import score_monitor


def test_profil_nutritionnel_score():
    """Test du scoring simple d'un plat."""
    print("\n✓ Test 1: Score Nutritionnel Simple (Plat)")
    
    try:
        # Créer un plat test
        plat = Plat.objects.create(
            nom='Poulet Rôti',
            description='Poulet rôti simple',
            calorie=400,
            proteine=35,
            glucides=10,
            lipides=15,
            fibres=0,
            prix=10.00,
        )
        
        # Tester calculer_score_nutritionnel (c'est une méthode du Plat)
        score = plat.calculer_score_nutritionnel()
        
        print(f"  Score nutritionnel: {score}")
        assert isinstance(score, int), "Le score doit être un entier"
        assert 0 <= score <= 100, f"Le score doit être entre 0 et 100, reçu: {score}"
        
        # Nettoyer
        plat.delete()
        
        print(f"  ✅ Score nutritionnel OK: {score}/100")
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plat_recommendation_score():
    """Test du scoring de recommandation d'un plat."""
    print("\n✓ Test 2: Score de Recommandation (Simple)")
    
    try:
        # Créer un plat test
        plat = Plat.objects.create(
            nom='Salade Verte',
            description='Salade simple',
            calorie=150,
            proteine=8,
            glucides=20,
            lipides=2,
            fibres=5,
            prix=8.50,
        )
        
        # Tester calculer_score_recommendation
        score = Plat.calculer_score_recommendation(plat, categorie_imc='normal')
        
        print(f"  Score recommandation: {score}")
        assert isinstance(score, (int, float)), "Le score doit être numérique"
        assert 0 <= score <= 100, f"Le score doit être entre 0 et 100, reçu: {score}"
        
        # Nettoyer
        plat.delete()
        
        print(f"  ✅ Score recommandation OK: {score:.1f}/100")
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plat_professional_score():
    """Test du scoring professionnel d'un plat."""
    print("\n✓ Test 3: Score Professionnel")
    
    try:
        # Créer les données test
        user = Utilisateur.objects.create_user(
            email=f'test_pro_{id(object())}@test.com',
            password='test',
            nom='Test',
            prenom='Pro'
        )
        
        client = Client.objects.create(utilisateur=user)
        
        profil = ProfilNutritionnel.objects.create(
            client=client,
            age=35,
            poids=70.0,
            taille=175.0,
            sexe='M',
            objectif='prise_muscle',
            niveau_activite='actif',
            allergies='',
            restrictions_alimentaires='',
        )
        
        plat = Plat.objects.create(
            nom='Poulet Grill',
            description='Filet de poulet grillé',
            calorie=200,
            proteine=35,
            glucides=0,
            lipides=5,
            fibres=0,
            prix=12.50,
        )
        
        # Tester calculer_score_professionnel
        score = Plat.calculer_score_professionnel(plat, profil)
        
        print(f"  Score professionnel: {score}")
        assert isinstance(score, (int, float)), "Le score doit être numérique"
        assert 0 <= score <= 100, f"Le score doit être entre 0 et 100, reçu: {score}"
        
        # Tester avec return_details=True
        score_detail, details = Plat.calculer_score_professionnel(
            plat, profil, return_details=True
        )
        
        assert score_detail == score, "Les scores doivent être identiques"
        assert 'breakdown' in details, "Doit contenir breakdown"
        assert 'evaluation' in details, "Doit contenir evaluation"
        
        print(f"  Score: {score:.1f}/100")
        print(f"  Évaluation: {details['evaluation']}")
        print(f"  Breakdown: {details['breakdown']}")
        
        # Nettoyer
        plat.delete()
        profil.delete()
        client.delete()
        user.delete()
        
        print(f"  ✅ Score professionnel OK")
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitoring_integration():
    """Test que les scores sont correctement enregistrés dans le monitoring."""
    print("\n✓ Test 4: Intégration Monitoring")
    
    try:
        # Reset le monitor
        score_monitor.reset()
        
        # Créer les données test
        user = Utilisateur.objects.create_user(
            email=f'test_mon_{id(object())}@test.com',
            password='test',
            nom='Test',
            prenom='Mon'
        )
        
        client = Client.objects.create(utilisateur=user)
        
        profil = ProfilNutritionnel.objects.create(
            client=client,
            age=30,
            poids=75.0,
            taille=180.0,
            sexe='M',
            objectif='minceur',
            niveau_activite='moyen',
            allergies='',
            restrictions_alimentaires='',
        )
        
        plat = Plat.objects.create(
            nom='Poisson Vapeur',
            description='Poisson à la vapeur',
            calorie=180,
            proteine=30,
            glucides=0,
            lipides=3,
            fibres=0,
            prix=15.00,
        )
        
        # Enregistrer un score professionnel (qui utilise le monitoring)
        score = Plat.calculer_score_professionnel(plat, profil)
        
        # Vérifier que le score a été enregistré dans le monitoring
        # get_stats() sans paramètre retourne un dict avec tous les types de scores
        all_stats = score_monitor.get_stats()
        
        print(f"  Score enregistré: {score:.1f}")
        print(f"  Types de scores dans le monitoring: {list(all_stats.keys())}")
        
        assert len(all_stats) > 0, "Le monitoring doit avoir des données"
        
        # Récupérer les stats du score professionnel
        prof_stats = score_monitor.get_stats('professionnel')
        
        print(f"  Stats monitoring:")
        print(f"    - Score type: {prof_stats['score_type']}")
        print(f"    - Samples: {prof_stats['samples']}")
        print(f"    - Mean: {prof_stats['mean']}")
        print(f"    - Stddev: {prof_stats['stddev']}")
        print(f"    - Min/Max: {prof_stats['min']}/{prof_stats['max']}")
        
        assert prof_stats['samples'] >= 1, "Doit avoir au moins 1 sample"
        assert prof_stats['mean'] is not None, "La moyenne doit être définie"
        
        # Nettoyer
        plat.delete()
        profil.delete()
        client.delete()
        user.delete()
        
        print(f"  ✅ Monitoring integration OK")
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imc_calculation():
    """Test du calcul de l'IMC."""
    print("\n✓ Test 5: Calcul de l'IMC")
    
    try:
        user = Utilisateur.objects.create_user(
            email=f'test_imc_{id(object())}@test.com',
            password='test',
            nom='Test',
            prenom='IMC'
        )
        
        client = Client.objects.create(utilisateur=user)
        
        profil = ProfilNutritionnel.objects.create(
            client=client,
            age=30,
            poids=75.0,  # kg
            taille=180.0,  # cm
            sexe='M',
            objectif='minceur',
            niveau_activite='moyen',
        )
        
        # Calculer l'IMC
        imc = profil.calculer_imc()
        
        # IMC = poids / (taille_m)^2
        # IMC = 75 / (1.80)^2 = 75 / 3.24 = 23.15
        expected_imc = 75 / (1.8 ** 2)
        
        print(f"  IMC calculé: {imc:.2f}")
        print(f"  IMC attendu: {expected_imc:.2f}")
        print(f"  Catégorie: {profil.determiner_categorie_imc()}")
        
        assert abs(imc - expected_imc) < 0.1, f"IMC incorrect: {imc} vs {expected_imc}"
        
        categorie = profil.determiner_categorie_imc()
        assert categorie in ['underweight', 'normal', 'overweight', 'obese'], f"Catégorie invalide: {categorie}"
        
        # Nettoyer
        profil.delete()
        client.delete()
        user.delete()
        
        print(f"  ✅ IMC calculation OK")
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_score_ranges():
    """Test que tous les scores respectent les plages [0, 100]."""
    print("\n✓ Test 6: Plages de Scores")
    
    try:
        # Créer des cas limites
        user = Utilisateur.objects.create_user(
            email=f'test_range_{id(object())}@test.com',
            password='test',
            nom='Test',
            prenom='Range'
        )
        
        client = Client.objects.create(utilisateur=user)
        
        # Cas 1: Profil très strict
        profil_strict = ProfilNutritionnel.objects.create(
            client=client,
            age=25,
            poids=50.0,
            taille=160.0,
            sexe='F',
            objectif='perte_poids',
            niveau_activite='sedentaire',
        )
        
        # Cas 2: Plat très calorique
        plat_calorique = Plat.objects.create(
            nom='Fast Food Burger',
            description='Burger gras',
            calorie=1200,  # Très calorique
            proteine=40,
            glucides=80,
            lipides=60,
            fibres=2,
            prix=8.00,
        )
        
        # Cas 3: Plat très sain
        plat_sain = Plat.objects.create(
            nom='Salade Complète',
            description='Très sain',
            calorie=300,
            proteine=20,
            glucides=30,
            lipides=8,
            fibres=15,
            prix=12.00,
        )
        
        # Tester les scores
        score_burger = Plat.calculer_score_professionnel(plat_calorique, profil_strict)
        score_salade = Plat.calculer_score_professionnel(plat_sain, profil_strict)
        
        print(f"  Score burger (mauvais): {score_burger:.1f}/100")
        print(f"  Score salade (bon): {score_salade:.1f}/100")
        
        assert 0 <= score_burger <= 100, f"Score burger hors plage: {score_burger}"
        assert 0 <= score_salade <= 100, f"Score salade hors plage: {score_salade}"
        assert score_salade > score_burger, "La salade devrait avoir un meilleur score"
        
        # Nettoyer
        plat_sain.delete()
        plat_calorique.delete()
        profil_strict.delete()
        client.delete()
        user.delete()
        
        print(f"  ✅ Score ranges OK (burger < salade)")
        return True
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("  VÉRIFICATION COMPLÈTE DU SYSTÈME DE SCORING")
    print("=" * 70)
    
    results = [
        test_profil_nutritionnel_score(),
        test_plat_recommendation_score(),
        test_plat_professional_score(),
        test_monitoring_integration(),
        test_imc_calculation(),
        test_score_ranges(),
    ]
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print(f"  RÉSULTAT: {passed}/{total} tests passés")
    print("=" * 70)
    
    if all(results):
        print("\n✅ TOUS LES TESTS DE SCORING PASSENT ✅")
        return True
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
