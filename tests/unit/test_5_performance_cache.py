#!/usr/bin/env python
"""
Suite de tests complète pour tous les cas de calcul de scores nutritionnels
Test 5: Performance et Système de Cache
"""

import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat
from myapp.score_constants import clear_score_cache, _score_cache

print("=" * 80)
print("🧪 TEST 5: PERFORMANCE ET SYSTÈME DE CACHE")
print("=" * 80)

# Créer un ensemble de plats
print("\n📋 Créer les plats de test...")
plats_data = [
    ('Plat 1 - Léger', 200, 15, 25, 5, 6),
    ('Plat 2 - Équilibré', 450, 35, 40, 15, 6),
    ('Plat 3 - Riche', 750, 40, 60, 30, 3),
    ('Plat 4 - Protéiné', 350, 50, 20, 12, 2),
    ('Plat 5 - Végétal', 300, 15, 45, 8, 10),
]

plats = []
for nom, cal, prot, carb, lip, fib in plats_data:
    plat, _ = Plat.objects.get_or_create(
        nom=nom,
        defaults={
            'description': f'Plat de test: {nom}',
            'calorie': cal,
            'proteine': prot,
            'glucides': carb,
            'lipides': lip,
            'fibres': fib,
            'prix': 10.0
        }
    )
    plats.append(plat)
    print(f"  ✅ {plat.nom}")

# TEST 1: Cache pour Score Simple
print("\n" + "=" * 80)
print("TEST 1️⃣: CACHE POUR SCORE SIMPLE")
print("=" * 80)

print("\n🔍 Analyser le cache avant:")
print(f"   Cache size: {len(_score_cache)} items")

clear_score_cache()
print(f"   Cache après clear: {len(_score_cache)} items")

print("\n⚡ Tester la performance (100 calculs par plat):")

results = []
for plat in plats:
    times = []
    
    # Première série (pas de cache)
    for _ in range(100):
        start = time.time()
        plat.calculer_score_nutritionnel()
        times.append((time.time() - start) * 1000)
    
    avg_first = sum(times[:10]) / 10  # Moyenne des 10 premiers
    avg_last = sum(times[-10:]) / 10   # Moyenne des 10 derniers
    
    results.append({
        'plat': plat.nom,
        'first_10_avg': avg_first,
        'last_10_avg': avg_last,
        'speedup': avg_first / (avg_last + 0.001)
    })
    
    print(f"\n   {plat.nom}:")
    print(f"      Premiers 10 appels: {avg_first:.4f}ms (moyenne)")
    print(f"      Derniers 10 appels: {avg_last:.4f}ms (moyenne)")
    print(f"      Speedup: {avg_first / (avg_last + 0.001):.1f}x")

print(f"\n   Cache size après: {len(_score_cache)} items")

# TEST 2: Cache pour Score Recommandation
print("\n" + "=" * 80)
print("TEST 2️⃣: CACHE POUR SCORE RECOMMANDATION")
print("=" * 80)

clear_score_cache()
print(f"Cache cleared: {len(_score_cache)} items")

print("\n⚡ Tester la performance (50 calculs par profil x plat):")

profiles = [
    ('normal', '', '', 35, 'femme'),
    ('surpoids', '', '', 40, 'homme'),
    ('obesite', '', '', 55, 'femme'),
]

rec_results = []
for category, allerg, restr, age, sexe in profiles:
    times = []
    total_calls = 0
    
    for plat in plats:
        for _ in range(50):
            start = time.time()
            Plat.calculer_score_recommendation(
                plat=plat,
                categorie_imc=category,
                allergies=allerg,
                restrictions=restr,
                age=age,
                sexe=sexe
            )
            times.append((time.time() - start) * 1000)
            total_calls += 1
    
    avg_first = sum(times[:50]) / 50
    avg_last = sum(times[-50:]) / 50
    
    profile_str = f"{sexe}, {age} ans, IMC {category}"
    rec_results.append({
        'profile': profile_str,
        'total_calls': total_calls,
        'first_50_avg': avg_first,
        'last_50_avg': avg_last,
        'speedup': avg_first / (avg_last + 0.001)
    })
    
    print(f"\n   Profil: {profile_str}")
    print(f"      Total appels: {total_calls}")
    print(f"      Premiers 50: {avg_first:.4f}ms (moyenne)")
    print(f"      Derniers 50: {avg_last:.4f}ms (moyenne)")
    print(f"      Speedup: {avg_first / (avg_last + 0.001):.1f}x")

print(f"\n   Cache size: {len(_score_cache)} items")

# TEST 3: Comparaison Sans Cache vs Avec Cache
print("\n" + "=" * 80)
print("TEST 3️⃣: COMPARAISON SANS CACHE vs AVEC CACHE")
print("=" * 80)

comparison_results = []
for plat in plats[:3]:  # Test avec 3 plats
    # Sans cache
    clear_score_cache()
    start = time.time()
    for _ in range(100):
        plat.calculer_score_nutritionnel()
    time_with_clearing = (time.time() - start) * 1000
    
    # Avec cache
    clear_score_cache()
    score1 = plat.calculer_score_nutritionnel()  # Met en cache
    start = time.time()
    for _ in range(99):  # 99 autres (en cache)
        plat.calculer_score_nutritionnel()
    time_cached = (time.time() - start) * 1000
    
    comparison_results.append({
        'plat': plat.nom,
        'time_clearing': time_with_clearing,
        'time_cached': time_cached,
        'total_calls': 100
    })
    
    print(f"\n   {plat.nom}:")
    print(f"      100 appels sans cache: {time_with_clearing:.2f}ms")
    print(f"      100 appels avec cache: {time_cached:.2f}ms (1er + 99 en cache)")
    print(f"      Économie: {((time_with_clearing - time_cached) / time_with_clearing * 100):.1f}%")

# TEST 4: Efficacité du cache
print("\n" + "=" * 80)
print("TEST 4️⃣: EFFICACITÉ DU CACHE")
print("=" * 80)

clear_score_cache()

print(f"\n📊 Statistiques finales du cache:")
print(f"   Total items en cache: {len(_score_cache)}")

# Compter les entrées par type
score_entries = sum(1 for k in _score_cache.keys() if k.startswith('score_'))
rec_entries = sum(1 for k in _score_cache.keys() if k.startswith('rec_'))

print(f"   Scores simples en cache: {score_entries}")
print(f"   Scores recommandation en cache: {rec_entries}")

print("\n📈 Résumé des Gains:")
print(f"   Score simple: {sum(r['speedup'] for r in results) / len(results):.1f}x speedup moyen")
print(f"   Score recommandation: {sum(r['speedup'] for r in rec_results) / len(rec_results):.1f}x speedup moyen")

avg_saving = sum((r['time_clearing'] - r['time_cached']) / r['time_clearing'] * 100 
                  for r in comparison_results) / len(comparison_results)
print(f"   Économie temps moyenne: {avg_saving:.1f}%")

print("\n" + "=" * 80)
print("✅ TEST DE CACHE TERMINÉ!")
print("=" * 80)
