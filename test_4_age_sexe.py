#!/usr/bin/env python
"""
Suite de tests complète pour tous les cas de calcul de scores nutritionnels
Test 4: Facteurs d'Âge et Sexe
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat

print("=" * 80)
print("🧪 TEST 4: FACTEURS D'ÂGE ET SEXE")
print("=" * 80)

# Créer des plats de test
plat_legere, _ = Plat.objects.get_or_create(
    nom='Salade Légère',
    defaults={
        'description': 'Salade avec crudités',
        'calorie': 250,
        'proteine': 12,
        'glucides': 25,
        'lipides': 8,
        'fibres': 8,
        'prix': 6.0
    }
)

plat_riche, _ = Plat.objects.get_or_create(
    nom='Steak Riche',
    defaults={
        'description': 'Steak avec sauce riche',
        'calorie': 700,
        'proteine': 50,
        'glucides': 0,
        'lipides': 40,
        'fibres': 0,
        'prix': 14.0
    }
)

plat_equilibre, _ = Plat.objects.get_or_create(
    nom='Poulet Équilibré',
    defaults={
        'description': 'Poulet avec légumes',
        'calorie': 450,
        'proteine': 35,
        'glucides': 40,
        'lipides': 15,
        'fibres': 6,
        'prix': 9.0
    }
)

print("\n📋 Plats de test:")
print(f"  ✅ {plat_legere.nom}")
print(f"  ✅ {plat_riche.nom}")
print(f"  ✅ {plat_equilibre.nom}")

# Test cases: (plat, sexe, age, imc_category, description, expected_min, expected_max)
test_cases = [
    {
        'label': 'FEMMES - JEUNES (< 20 ans)',
        'tests': [
            (plat_riche, 'femme', 18, 'normal', 'Steak riche - besoins énergétiques élevés', 60, 100),
            (plat_legere, 'femme', 18, 'normal', 'Salade légère - pas assez énergétique', 30, 60),
        ]
    },
    {
        'label': 'FEMMES - ADULTES (20-49 ans)',
        'tests': [
            (plat_legere, 'femme', 35, 'normal', 'Salade légère - bon score', 60, 80),
            (plat_equilibre, 'femme', 35, 'normal', 'Poulet équilibré - très bon', 70, 90),
            (plat_riche, 'femme', 35, 'normal', 'Steak - trop calorique pour femme', 30, 60),
        ]
    },
    {
        'label': 'FEMMES - SENIORS (>= 50 ans)',
        'tests': [
            (plat_legere, 'femme', 60, 'normal', 'Salade légère - parfait pour seniors', 70, 90),
            (plat_equilibre, 'femme', 60, 'normal', 'Poulet équilibré avec fibres', 70, 95),
            (plat_riche, 'femme', 60, 'normal', 'Steak riche - trop lourd', 25, 50),
        ]
    },
    {
        'label': 'HOMMES - JEUNES (< 20 ans)',
        'tests': [
            (plat_riche, 'homme', 18, 'normal', 'Steak - besoins énergétiques + protéines', 70, 100),
            (plat_legere, 'homme', 18, 'normal', 'Salade légère - pas assez', 25, 55),
        ]
    },
    {
        'label': 'HOMMES - ADULTES (20-49 ans)',
        'tests': [
            (plat_riche, 'homme', 35, 'normal', 'Steak riche + protéines élevées', 70, 90),
            (plat_equilibre, 'homme', 35, 'normal', 'Poulet équilibré - bon', 65, 85),
            (plat_legere, 'homme', 35, 'normal', 'Salade légère - insuffisant', 40, 65),
        ]
    },
    {
        'label': 'HOMMES - SENIORS (>= 50 ans)',
        'tests': [
            (plat_riche, 'homme', 60, 'normal', 'Steak - haute protéine pour seniors', 60, 80),
            (plat_equilibre, 'homme', 60, 'normal', 'Poulet équilibré avec fibres', 70, 90),
            (plat_legere, 'homme', 60, 'normal', 'Salade légère', 50, 70),
        ]
    }
]

print("\n" + "=" * 80)
print("🧮 Tester les facteurs d'âge et sexe...")
print("=" * 80)

all_results = []
for category in test_cases:
    print(f"\n{'='*50}")
    print(f"👤 {category['label']}")
    print(f"{'='*50}")
    
    for plat, sexe, age, imc_cat, description, expected_min, expected_max in category['tests']:
        # Calcul avec profil
        score = Plat.calculer_score_recommendation(
            plat=plat,
            categorie_imc=imc_cat,
            allergies='',
            restrictions='',
            age=age,
            sexe=sexe
        )
        
        success = expected_min <= score <= expected_max
        
        print(f"\n   📍 {description}")
        print(f"      Profil: {sexe}, {age} ans, IMC {imc_cat}")
        print(f"      Plat: {plat.nom} ({plat.calorie} cal, {plat.proteine}g prot)")
        print(f"      Score: {score}/100")
        print(f"      Attendu: {expected_min}-{expected_max}")
        
        if success:
            print(f"      ✅ CORRECT")
        else:
            print(f"      ❌ ERREUR")
        
        all_results.append({
            'category': category['label'],
            'sexe': sexe,
            'age': age,
            'plat': plat.nom,
            'score': score,
            'expected': f"{expected_min}-{expected_max}",
            'success': success
        })

print("\n" + "=" * 80)
print("📈 RÉSUMÉ PAR PROFIL")
print("=" * 80)

for category_label in [c['label'] for c in test_cases]:
    results_cat = [r for r in all_results if r['category'] == category_label]
    success_count = sum(1 for r in results_cat if r['success'])
    print(f"\n{category_label}:")
    print(f"  Réussis: {success_count}/{len(results_cat)}")
    for r in results_cat:
        status = "✅" if r['success'] else "❌"
        print(f"    {status} {r['plat']:20} | Score: {r['score']:3}/100 | Attendu: {r['expected']}")

print("\n" + "=" * 80)
print(f"GLOBAL: {sum(1 for r in all_results if r['success'])}/{len(all_results)} tests réussis")
print("=" * 80)
