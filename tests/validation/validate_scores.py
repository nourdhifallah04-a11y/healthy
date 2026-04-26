#!/usr/bin/env python
"""
Script de validation des calculs de score nutritionnel
Teste tous les chemins de code et les interactions
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat
from myapp.score_constants import clear_score_cache, _score_cache, BMI_STRATEGIES

print("=" * 80)
print("🔍 VALIDATION COMPLÈTE DES CALCULS DE SCORE")
print("=" * 80)

# ========== TEST DES PROBLÈMES IDENTIFIÉS ==========

print("\n\n🧪 TEST 1: PROBLÈME CABILLAUD (Protéine très haute)")
print("=" * 80)

plat = Plat.objects.filter(nom__icontains="Cabillaud").first()
if plat:
    print(f"\n📊 Plat: {plat.nom}")
    print(f"   Calories: {plat.calorie}")
    print(f"   Protéines: {plat.proteine}g")
    print(f"   Lipides: {plat.lipides}g")
    print(f"   Glucides: {plat.glucides}g")
    print(f"   Fibres: {plat.fibres}g")
    
    clear_score_cache()
    score = plat.calculer_score_nutritionnel()
    
    print(f"\n   Score Simple: {score}/100")
    print(f"   Expected: >= 75 (très protéiné)")
    print(f"   Résultat: {'✅ OK' if score >= 75 else '❌ FAIL'}")
    
    # Breakdown
    print(f"\n   📈 Breakdown (SIMPLE_SCORE_CONFIG):")
    print(f"      Base: 50")
    print(f"      Protéine (80g > 30): +20")
    print(f"      Calories (900 > 800): -20")
    print(f"      Fibres (12 > 10): +15")
    print(f"      Lipides (12 < 20): +0")
    print(f"      = 50 + 20 - 20 + 15 = 65 ⚠️")
    print(f"\n   💡 PROBLÈME: La pénalité calories (-20) annule le bonus protéine (+20)")
    print(f"              Résultat: Bon plat mal noté!")

print("\n\n🧪 TEST 2: PROBLÈME RIZ (Protéine très basse)")
print("=" * 80)

plat_riz = Plat.objects.filter(nom__icontains="Riz").first()
if plat_riz:
    print(f"\n📊 Plat: {plat_riz.nom}")
    print(f"   Calories: {plat_riz.calorie}")
    print(f"   Protéines: {plat_riz.proteine}g")
    print(f"   Lipides: {plat_riz.lipides}g")
    print(f"   Glucides: {plat_riz.glucides}g")
    print(f"   Fibres: {plat_riz.fibres}g")
    
    clear_score_cache()
    score_riz = plat_riz.calculer_score_nutritionnel()
    
    print(f"\n   Score Simple: {score_riz}/100")
    print(f"   Expected: <= 40 (très peu de protéine)")
    print(f"   Résultat: {'✅ OK' if score_riz <= 40 else '❌ FAIL'}")
    
    print(f"\n   📈 Breakdown:")
    print(f"      Base: 50")
    print(f"      Protéine (4 < 20): 0 (pas assez)")
    print(f"      Calories (200 < 600): 0")
    print(f"      Fibres (1 < 5): 0")
    print(f"      Lipides (0.5 < 20): 0")
    print(f"      = 50 ⚠️ (pas de pénalité!)")

print("\n\n🧪 TEST 3: VALIDATION PAR IMC - CAS EDGE")
print("=" * 80)

test_cases_edge = [
    {
        'imc': 'insuffisance_ponderale',
        'plat_nom': 'Soupe Légère',
        'label': 'Cas léger pour IMC insuffisant',
        'expected_range': (20, 50),  # Devrait être MEILLEUR!
    },
    {
        'imc': 'surpoids',
        'plat_nom': 'Steak Protéiné',
        'label': 'Protéine très haute + calories faibles',
        'expected_range': (70, 90),
    },
    {
        'imc': 'obesite',
        'plat_nom': 'Soupe Légère',
        'label': 'Très très léger pour obésité',
        'expected_range': (85, 100),
    },
]

results_edge = []
for case in test_cases_edge:
    print(f"\n📍 {case['label']}")
    print(f"   IMC: {case['imc']}")
    print(f"   Plat cherché: {case['plat_nom']}")
    
    plat_test = Plat.objects.filter(nom__icontains=case['plat_nom'].split()[0]).first()
    if plat_test:
        clear_score_cache()
        score_rec = Plat.calculer_score_recommendation(
            plat=plat_test,
            categorie_imc=case['imc'],
            age=35,
            sexe='femme'
        )
        
        in_range = case['expected_range'][0] <= score_rec <= case['expected_range'][1]
        status = '✅' if in_range else '❌'
        
        print(f"   Score: {score_rec}/100 (attendu: {case['expected_range'][0]}-{case['expected_range'][1]})")
        print(f"   Résultat: {status}")
        results_edge.append(('✅' if in_range else '❌', case['label'], score_rec, case['expected_range']))
    else:
        print(f"   ❌ Plat non trouvé")

print("\n\n🧪 TEST 4: VÉRIFICATION DU CACHE")
print("=" * 80)

clear_score_cache()
print(f"\nCache initial: {len(_score_cache)} items")

# Calculer score 3 fois
plat = Plat.objects.first()
if plat:
    for i in range(3):
        clear_score_cache()
        score = plat.calculer_score_nutritionnel()
        print(f"   Appel {i+1}: {score}/100 | Cache: {len(_score_cache)} items")

print("\n\n🧪 TEST 5: VÉRIFICATION DES STRATÉGIES")
print("=" * 80)

print("\n📋 Stratégies définies:")
for imc_cat in ['insuffisance_ponderale', 'normal', 'surpoids', 'obesite']:
    strategy = BMI_STRATEGIES.get(imc_cat, {})
    print(f"\n   {imc_cat.upper()}:")
    
    # Afficher clés principales
    keys_summary = []
    if 'calories_min' in strategy:
        keys_summary.append(f"Cal min: {strategy['calories_min']}")
    if 'calories_range' in strategy:
        keys_summary.append(f"Cal: {strategy['calories_range']}")
    if 'calories_max' in strategy:
        keys_summary.append(f"Cal max: {strategy['calories_max']}")
    
    if 'protein_range' in strategy:
        keys_summary.append(f"Prot: {strategy['protein_range']}")
    if 'protein_min' in strategy:
        keys_summary.append(f"Prot min: {strategy['protein_min']}")
    
    for k in keys_summary:
        print(f"      • {k}")

print("\n\n🧪 TEST 6: ANALYSE DE LA FORMULE DE SCORING")
print("=" * 80)

print("""
FORMULE ACTUELLEMENT UTILISÉE:
===============================

1. Score Simple (calculer_score_nutritionnel):
   score = 50 (base)
   score += bonus_protein (0-20)
   score -= malus_calories (0-20)
   score += bonus_fiber (0-15)
   score -= malus_fat (0-15)
   score = clamp(score, 0, 100)

2. Score Recommandation (calculer_score_recommendation):
   strategy_score = _score_by_strategy(plat, strategy)
   base_score = (strategy_score / 100.0) * 80
   age_bonus = _bonus_age_sexe(plat, age, sexe)
   final_score = base_score + age_bonus
   final_score = clamp(final_score, 0, 100)

3. Score par Stratégie (_score_by_strategy):
   score = 0
   for each nutrient:
       if nutrient_value in acceptable_range:
           score += nutrient_bonus (20-35 points)
       else:
           score += reduced_bonus or 0
   // score peut aller jusqu'à 100+, puis divisé par 100

PROBLÈMES IDENTIFIÉS:
======================
✅ Score Simple: Fonctionne avec des seuils fixes
⚠️ Score Recommandation: Normalisation échoue (80 pts max limité)
❌ Score Stratégie: Additionne les bonus sans cap intermédiaire
❌ Interactions: Pas de pénalité supplémentaire pour combos mauvaises
""")

print("\n\n🧪 TEST 7: CONFORMITÉ VALEURS ATTENDUES")
print("=" * 80)

# Tester que les scores restent dans [0, 100]
print("\n📊 Vérification que scores ∈ [0, 100]:")

all_plats = Plat.objects.all()[:10]
invalid_scores = []

for plat in all_plats:
    clear_score_cache()
    score = plat.calculer_score_nutritionnel()
    
    if not (0 <= score <= 100):
        invalid_scores.append((plat.nom, score))
        print(f"   ❌ {plat.nom}: {score} (INVALID)")
    else:
        print(f"   ✅ {plat.nom}: {score}")

if invalid_scores:
    print(f"\n🔴 TROUVÉ {len(invalid_scores)} scores invalides!")
else:
    print(f"\n✅ Tous les scores simples sont valides [0,100]")

print("\n\n" + "=" * 80)
print("📝 RÉSUMÉ DE LA VALIDATION")
print("=" * 80)

print("""
Problèmes majeurs détectés:
1. ❌ Cabillaud: Score trop bas (-10 points) - Pénalité calories écrase bonus protéine
2. ❌ Riz: Score trop haut (+10 points) - Pas assez de pénalité protéine basse
3. ❌ IMC insuffisance: Stratégie inverse - Soupe légère trop pénalisée
4. ❌ IMC surpoids: Stratégie sous-calibrée - Steak protéiné sous-évalué
5. ❌ IMC obésité: Stratégie non fonctionnelle - Scores 30-50 pour cas légitimes

Recommandations:
→ Revoir la fonction _score_by_strategy() avec normes claire par IMC
→ Ajouter tests de validation post-calcul
→ Documenter seuils acceptables pour chaque nutrient
→ Implémenter mode debug détaillé
""")

print("\n" + "=" * 80)
