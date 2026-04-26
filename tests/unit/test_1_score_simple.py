#!/usr/bin/env python
"""
Suite de tests complète pour tous les cas de calcul de scores nutritionnels
Test: Score Simple (Plat)
"""

import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat
from myapp.score_constants import clear_score_cache, _score_cache

print("=" * 80)
print("🧪 TEST 1: SCORE SIMPLE (PLAT)")
print("=" * 80)

# Données de test
test_plats = [
    {
        'nom': 'Poulet Grillé - Sain',
        'description': 'Poulet grillé avec légumes',
        'calorie': 300,
        'proteine': 35,
        'glucides': 20,
        'lipides': 8,
        'fibres': 8,
        'prix': 8.5,
        'expected_min': 70,  # Score attendu > 70
        'case': 'Haute protéine, basses calories'
    },
    {
        'nom': 'Burger Gras',
        'description': 'Burger avec frites',
        'calorie': 1200,
        'proteine': 25,
        'glucides': 80,
        'lipides': 45,
        'fibres': 2,
        'prix': 12.0,
        'expected_max': 40,  # Score attendu < 40
        'case': 'Hautes calories, bas score'
    },
    {
        'nom': 'Salade Équilibrée',
        'description': 'Salade avec protéines et fibres',
        'calorie': 350,
        'proteine': 28,
        'glucides': 35,
        'lipides': 12,
        'fibres': 12,
        'prix': 7.0,
        'expected_min': 65,
        'case': 'Équilibre optimal'
    },
    {
        'nom': 'Riz Nature',
        'description': 'Riz blanc cuit',
        'calorie': 200,
        'proteine': 4,
        'glucides': 45,
        'lipides': 0.5,
        'fibres': 1,
        'prix': 2.5,
        'expected_max': 40,
        'case': 'Basses protéines'
    },
    {
        'nom': 'Cabillaud vapeur',
        'description': 'Cabillaud vapeur - brocoli citron',
        'calorie': 900,
        'proteine': 80,
        'glucides': 50,
        'lipides': 12,
        'fibres': 12,
        'prix': 9.0,
        'expected_min': 75,
        'case': 'Très haute protéine'
    }
]

print("\n📋 Créer les plats de test...")
plats = []
for data in test_plats:
    try:
        # Vérifier si plat existe déjà
        plat, created = Plat.objects.get_or_create(
            nom=data['nom'],
            defaults={
                'description': data['description'],
                'calorie': data['calorie'],
                'proteine': data['proteine'],
                'glucides': data['glucides'],
                'lipides': data['lipides'],
                'fibres': data['fibres'],
                'prix': data['prix']
            }
        )
        plats.append((plat, data))
        status = "✅ Créé" if created else "📌 Existe"
        print(f"{status}: {plat.nom}")
    except Exception as e:
        print(f"❌ Erreur avec {data['nom']}: {e}")

print("\n🧮 Tester les scores...")
clear_score_cache()

results = []
for plat, test_data in plats:
    print(f"\n📊 Plat: {plat.nom}")
    print(f"   Cas: {test_data['case']}")
    print(f"   Valeurs: {plat.calorie} cal, {plat.proteine}g prot, {plat.lipides}g lip, {plat.fibres}g fib")
    
    # Calcul 1: Sans cache
    clear_score_cache()
    start = time.time()
    score1 = plat.calculer_score_nutritionnel()
    t1 = (time.time() - start) * 1000
    
    # Calcul 2: Avec cache
    start = time.time()
    score2 = plat.calculer_score_nutritionnel()
    t2 = (time.time() - start) * 1000
    
    print(f"   Score: {score1}/100")
    print(f"   ⏱️  Temps sans cache: {t1:.4f}ms")
    print(f"   ⏱️  Temps avec cache: {t2:.4f}ms")
    print(f"   Speedup: {t1/max(t2, 0.001):.1f}x")
    
    # Vérifier les seuils attendus
    success = True
    if 'expected_min' in test_data:
        if score1 >= test_data['expected_min']:
            print(f"   ✅ Score >= {test_data['expected_min']} ✓")
        else:
            print(f"   ⚠️  Score < {test_data['expected_min']} (obtenu: {score1})")
            success = False
    
    if 'expected_max' in test_data:
        if score1 <= test_data['expected_max']:
            print(f"   ✅ Score <= {test_data['expected_max']} ✓")
        else:
            print(f"   ⚠️  Score > {test_data['expected_max']} (obtenu: {score1})")
            success = False
    
    results.append({
        'nom': plat.nom,
        'score': score1,
        'success': success,
        'speedup': t1/max(t2, 0.001)
    })

print("\n" + "=" * 80)
print("📈 RÉSUMÉ DES RÉSULTATS")
print("=" * 80)
print(f"\nTests réussis: {sum(1 for r in results if r['success'])}/{len(results)}")
print(f"Cache size: {len(_score_cache)} items\n")

for result in results:
    status = "✅" if result['success'] else "⚠️"
    print(f"{status} {result['nom']:30} | Score: {result['score']:3}/100 | Speedup: {result['speedup']:6.1f}x")

print("\n" + "=" * 80)
