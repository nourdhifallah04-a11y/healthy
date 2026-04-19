#!/usr/bin/env python
"""
Suite de tests complète pour tous les cas de calcul de scores nutritionnels
Test 3: Allergies et Restrictions Alimentaires
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat
from myapp.score_constants import clear_score_cache, _score_cache

print("=" * 80)
print("🧪 TEST 3: ALLERGIES ET RESTRICTIONS ALIMENTAIRES")
print("=" * 80)

# Créer des plats de test
plats_data = {
    'poulet': {
        'nom': 'Poulet Rôti',
        'description': 'Poulet rôti avec riz',
        'calorie': 450,
        'proteine': 40,
        'glucides': 35,
        'lipides': 15,
        'fibres': 2,
        'prix': 9.0
    },
    'vegan': {
        'nom': 'Tofu Sauté',
        'description': 'Tofu sauté avec légumes',
        'calorie': 350,
        'proteine': 20,
        'glucides': 30,
        'lipides': 15,
        'fibres': 8,
        'prix': 8.0
    },
    'poisson': {
        'nom': 'Saumon',
        'description': 'Saumon grillé avec beurre',
        'calorie': 500,
        'proteine': 45,
        'glucides': 0,
        'lipides': 30,
        'fibres': 0,
        'prix': 15.0
    },
    'pizza': {
        'nom': 'Pizza Fromage',
        'description': 'Pizza riche en fromage et lait',
        'calorie': 800,
        'proteine': 30,
        'glucides': 80,
        'lipides': 35,
        'fibres': 2,
        'prix': 12.0
    },
    'pates': {
        'nom': 'Pâtes Blé',
        'description': 'Pâtes de blé avec sauce tomate',
        'calorie': 600,
        'proteine': 20,
        'glucides': 90,
        'lipides': 10,
        'fibres': 5,
        'prix': 7.0
    },
    'salad': {
        'nom': 'Salade Nature',
        'description': 'Salade avec légumes frais',
        'calorie': 150,
        'proteine': 8,
        'glucides': 20,
        'lipides': 5,
        'fibres': 10,
        'prix': 6.0
    }
}

print("\n📋 Créer/Récupérer les plats de test...")
plats = {}
for key, data in plats_data.items():
    plat, created = Plat.objects.get_or_create(
        nom=data['nom'],
        defaults={k: v for k, v in data.items() if k != 'nom'}
    )
    plats[key] = plat
    status = "✅ Créé" if created else "📌 Existe"
    print(f"{status}: {plat.nom}")

# Cas de test pour restrictions
test_cases = [
    {
        'restriction': 'vegetarien',
        'label': 'VÉGÉTARIEN',
        'description': 'Pas de viande ni poisson',
        'tests': [
            (plats['vegan'], True, 'Tofu - DOIT être accepté'),
            (plats['pizza'], True, 'Pizza - DOIT être acceptée'),
            (plats['poulet'], False, 'Poulet - DOIT être rejeté'),
            (plats['poisson'], False, 'Saumon - DOIT être rejeté'),
        ]
    },
    {
        'restriction': 'vegane',
        'label': 'VEGAN',
        'description': 'Pas de viande, poisson, oeufs, lait, fromage',
        'tests': [
            (plats['vegan'], True, 'Tofu - DOIT être accepté'),
            (plats['salad'], True, 'Salade - DOIT être acceptée'),
            (plats['poulet'], False, 'Poulet - DOIT être rejeté (viande)'),
            (plats['pizza'], False, 'Pizza - DOIT être rejeté (fromage/lait)'),
            (plats['poisson'], False, 'Saumon - DOIT être rejeté (poisson)'),
        ]
    },
    {
        'restriction': 'sans gluten',
        'label': 'SANS GLUTEN',
        'description': 'Pas de blé, gluten, pain',
        'tests': [
            (plats['vegan'], True, 'Tofu - DOIT être accepté'),
            (plats['poulet'], True, 'Poulet - DOIT être accepté'),
            (plats['pates'], False, 'Pâtes - DOIT être rejeté (blé)'),
        ]
    },
    {
        'restriction': 'sans lactose',
        'label': 'SANS LACTOSE',
        'description': 'Pas de lait, fromage, beurre',
        'tests': [
            (plats['poulet'], True, 'Poulet - DOIT être accepté'),
            (plats['vegan'], True, 'Tofu - DOIT être accepté'),
            (plats['pizza'], False, 'Pizza - DOIT être rejeté (fromage)'),
            (plats['poisson'], False, 'Saumon - DOIT être rejeté (beurre)'),
        ]
    }
]

print("\n" + "=" * 80)
print("🧮 Tester les restrictions alimentaires...")
print("=" * 80)

all_results = []
for case in test_cases:
    print(f"\n{'='*50}")
    print(f"🚫 {case['label']}: {case['description']}")
    print(f"{'='*50}")
    
    for plat, should_pass, description in case['tests']:
        clear_score_cache()
        
        # Calcul avec restriction
        score = Plat.calculer_score_recommendation(
            plat=plat,
            categorie_imc='normal',
            allergies='',
            restrictions=case['restriction'],
            age=35,
            sexe='femme'
        )
        
        # Score 0 = rejeté, Score > 0 = accepté
        is_accepted = score > 0
        success = (is_accepted == should_pass)
        
        print(f"\n   📍 {description}")
        print(f"      Plat: {plat.nom}")
        print(f"      Restriction: {case['restriction']}")
        print(f"      Score: {score}/100")
        
        if is_accepted:
            print(f"      État: ✅ ACCEPTÉ")
        else:
            print(f"      État: 🚫 REJETÉ")
        
        if should_pass:
            if success:
                print(f"      Résultat: ✅ CORRECT (accepté comme attendu)")
            else:
                print(f"      Résultat: ❌ ERREUR (devrait être accepté)")
        else:
            if success:
                print(f"      Résultat: ✅ CORRECT (rejeté comme attendu)")
            else:
                print(f"      Résultat: ❌ ERREUR (devrait être rejeté)")
        
        all_results.append({
            'restriction': case['label'],
            'plat': plat.nom,
            'description': description,
            'score': score,
            'accepted': is_accepted,
            'should_pass': should_pass,
            'success': success
        })

print("\n" + "=" * 80)
print("📈 RÉSUMÉ PAR RESTRICTION")
print("=" * 80)

for restriction_label in [c['label'] for c in test_cases]:
    results_rest = [r for r in all_results if r['restriction'] == restriction_label]
    success_count = sum(1 for r in results_rest if r['success'])
    print(f"\n{restriction_label}:")
    print(f"  Réussis: {success_count}/{len(results_rest)}")
    for r in results_rest:
        state = "✅" if r['accepted'] else "🚫"
        expected = "✅" if r['should_pass'] else "🚫"
        result = "✅" if r['success'] else "❌"
        print(f"    {result} {r['plat']:20} | {state} (Attendu: {expected}) | Score: {r['score']:3}/100")

print("\n" + "=" * 80)
print(f"GLOBAL: {sum(1 for r in all_results if r['success'])}/{len(all_results)} tests réussis")
print("=" * 80)
