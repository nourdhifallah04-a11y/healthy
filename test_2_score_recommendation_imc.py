#!/usr/bin/env python
"""
Suite de tests complète pour tous les cas de calcul de scores nutritionnels
Test 2: Score de Recommandation par catégorie IMC
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat
from myapp.score_constants import clear_score_cache, _score_cache

print("=" * 80)
print("🧪 TEST 2: SCORE DE RECOMMANDATION (PAR CATÉGORIE IMC)")
print("=" * 80)

# Créer des plats de test si nécessaire
plats_data = {
    'faible_cal': {
        'nom': 'Soupe Légère',
        'description': 'Soupe de légumes basse calorie',
        'calorie': 150,
        'proteine': 10,
        'glucides': 20,
        'lipides': 2,
        'fibres': 8,
        'prix': 4.0
    },
    'equilibre': {
        'nom': 'Poulet Équilibré',
        'description': 'Poulet rôti avec légumes',
        'calorie': 450,
        'proteine': 40,
        'glucides': 35,
        'lipides': 15,
        'fibres': 6,
        'prix': 9.0
    },
    'riche': {
        'nom': 'Pizza Fromage',
        'description': 'Pizza riche en fromage',
        'calorie': 800,
        'proteine': 30,
        'glucides': 80,
        'lipides': 35,
        'fibres': 2,
        'prix': 12.0
    },
    'haute_prot': {
        'nom': 'Steak Protéiné',
        'description': 'Steak de boeuf haute protéine',
        'calorie': 350,
        'proteine': 50,
        'glucides': 0,
        'lipides': 18,
        'fibres': 0,
        'prix': 14.0
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

# Cas de test par catégorie IMC
test_cases = [
    {
        'category': 'insuffisance_ponderale',
        'label': 'INSUFFISANCE PONDÉRALE',
        'description': 'Favoriser calories et protéines',
        'tests': [
            (plats['riche'], 'Pizza - Devrait marquer bien', 70, 100),
            (plats['equilibre'], 'Poulet - Modéré', 50, 80),
            (plats['faible_cal'], 'Soupe - Mauvais', 20, 50),
        ]
    },
    {
        'category': 'normal',
        'label': 'NORMAL (IMC 18.5-25)',
        'description': 'Équilibre optimal entre nutriments',
        'tests': [
            (plats['equilibre'], 'Poulet - Excellent', 70, 100),
            (plats['haute_prot'], 'Steak - Bon', 60, 85),
            (plats['riche'], 'Pizza - Mauvais', 20, 50),
        ]
    },
    {
        'category': 'surpoids',
        'label': 'SURPOIDS',
        'description': 'Faibles calories, protéines élevées',
        'tests': [
            (plats['faible_cal'], 'Soupe - Excellent', 80, 100),
            (plats['haute_prot'], 'Steak - Bon', 70, 90),
            (plats['riche'], 'Pizza - Mauvais', 5, 30),
        ]
    },
    {
        'category': 'obesite',
        'label': 'OBÉSITÉ',
        'description': 'Très faibles calories, protéines très élevées',
        'tests': [
            (plats['faible_cal'], 'Soupe - Excellent', 85, 100),
            (plats['equilibre'], 'Poulet - Bon', 60, 80),
            (plats['riche'], 'Pizza - Très mauvais', 1, 20),
        ]
    }
]

print("\n" + "=" * 80)
print("🧮 Tester les scores par catégorie IMC...")
print("=" * 80)

all_results = []
for case in test_cases:
    print(f"\n{'='*40}")
    print(f"📊 {case['label']}")
    print(f"   {case['description']}")
    print(f"{'='*40}")
    
    for plat, description, expected_min, expected_max in case['tests']:
        clear_score_cache()
        
        # Calcul avec profil
        score = Plat.calculer_score_recommendation(
            plat=plat,
            categorie_imc=case['category'],
            allergies='',
            restrictions='',
            age=35,
            sexe='femme'
        )
        
        print(f"\n   📍 {description}")
        print(f"      Plat: {plat.nom}")
        print(f"      Score obtenu: {score}/100")
        print(f"      Score attendu: {expected_min}-{expected_max}")
        
        if expected_min <= score <= expected_max:
            print(f"      ✅ DANS LA PLAGE ✓")
            success = True
        else:
            print(f"      ⚠️  HORS PLAGE")
            success = False
        
        all_results.append({
            'category': case['label'],
            'plat': plat.nom,
            'description': description,
            'score': score,
            'expected': f"{expected_min}-{expected_max}",
            'success': success
        })

print("\n" + "=" * 80)
print("📈 RÉSUMÉ PAR CATÉGORIE")
print("=" * 80)

for category_label in [c['label'] for c in test_cases]:
    results_cat = [r for r in all_results if r['category'] == category_label]
    success_count = sum(1 for r in results_cat if r['success'])
    print(f"\n{category_label}:")
    print(f"  Réussis: {success_count}/{len(results_cat)}")
    for r in results_cat:
        status = "✅" if r['success'] else "⚠️"
        print(f"    {status} {r['plat']:25} | {r['score']:3}/100 | Attendu: {r['expected']}")

print("\n" + "=" * 80)
print(f"GLOBAL: {sum(1 for r in all_results if r['success'])}/{len(all_results)} tests réussis")
print("=" * 80)
