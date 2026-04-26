#!/usr/bin/env python
"""
Script de diagnostic pour vérifier les recommandations IA
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat, ProfilNutritionnel, Client
from django.contrib.auth.models import User

print("=" * 80)
print("DIAGNOSTIC RECOMMANDATIONS IA")
print("=" * 80)

# 1. Vérifier les plats disponibles
print("\n1. PLATS DISPONIBLES")
print("-" * 80)
plats = Plat.objects.filter(est_disponible=True)
print(f"Nombre de plats disponibles: {plats.count()}")
if plats.count() > 0:
    for plat in plats[:5]:
        print(f"  - {plat.nom}: {plat.calorie} cal, {plat.proteine}g protéine, {plat.glucides}g glucides")
else:
    print("  ⚠️  AUCUN PLAT DISPONIBLE!")

# 2. Vérifier les profils nutritionnels
print("\n2. PROFILS NUTRITIONNELS")
print("-" * 80)
profils = ProfilNutritionnel.objects.all()
print(f"Nombre de profils: {profils.count()}")
if profils.count() > 0:
    for profil in profils[:3]:
        print(f"  Profil {profil.client.utilisateur.prenom} {profil.client.utilisateur.nom}:")
        print(f"    - Age: {profil.age}, IMC: {profil.calculer_imc()}, Objectif: {profil.objectif}")
        
        # Essayer les recommandations
        print(f"    - Recommandations:")
        reco_plats = profil.recommander_plats(limite=5)
        if reco_plats:
            for plat in reco_plats:
                print(f"      * {plat.nom}")
        else:
            print(f"      ⚠️  AUCUNE RECOMMANDATION!")

# 3. Vérifier les BMI_STRATEGIES et DIETARY_RESTRICTIONS
print("\n3. CONFIGURATION SCORE")
print("-" * 80)
try:
    from myapp.score_constants import BMI_STRATEGIES, DIETARY_RESTRICTIONS
    print("BMI_STRATEGIES chargées:")
    for categorie, strategy in BMI_STRATEGIES.items():
        print(f"  - {categorie}: {strategy}")
    
    print("\nDIETARY_RESTRICTIONS chargées:")
    for restriction, data in DIETARY_RESTRICTIONS.items():
        print(f"  - {restriction}: {data}")
except Exception as e:
    print(f"  ⚠️  Erreur lors du chargement des constantes: {e}")

# 4. Tester le calcul du score manuellement
print("\n4. TEST CALCUL DU SCORE")
print("-" * 80)
if profils.count() > 0 and plats.count() > 0:
    profil = profils.first()
    plat = plats.first()
    
    score = Plat.calculer_score_recommendation(
        plat,
        profil.determiner_categorie_imc(),
        allergies=profil.allergies,
        restrictions=profil.restrictions_alimentaires,
        age=profil.age,
        sexe=profil.sexe,
        debug=True
    )
    print(f"Plat: {plat.nom}")
    print(f"Score de recommandation: {score}")

print("\n" + "=" * 80)
