#!/usr/bin/env python
"""
Suite de tests complète pour tous les cas de calcul de scores nutritionnels
Test 6: Intégration avec Menus et Profils Nutritionnels
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from django.contrib.auth import get_user_model
from myapp.models import Plat, Menu, Client, ProfilNutritionnel
from myapp.score_constants import clear_score_cache

User = get_user_model()

print("=" * 80)
print("🧪 TEST 6: INTÉGRATION MENUS ET PROFILS NUTRITIONNELS")
print("=" * 80)

# Créer des utilisateurs et clients
print("\n📋 Créer les utilisateurs et profils...")

users_profiles = [
    ('user_normal@test.com', 'normal', 'perte_poids', 'femme'),
    ('user_surpoids@test.com', 'surpoids', 'perte_poids', 'homme'),
    ('user_athlete@test.com', 'normal', 'prise_muscle', 'homme'),
]

clients = {}
for email, imc_cat, objectif, sexe in users_profiles:
    try:
        user = User.objects.create_user(
            email=email,
            password='test123',
            nom='Test',
            prenom=email.split('@')[0]
        )
        client, created = Client.objects.get_or_create(utilisateur=user)
        
        profil, _ = ProfilNutritionnel.objects.get_or_create(
            client=client,
            defaults={
                'categorie_imc': imc_cat,
                'objectif': objectif,
                'sexe': sexe,
                'age': 35,
                'taille': 170,
                'poids': 75
            }
        )
        
        clients[email] = {
            'user': user,
            'client': client,
            'profil': profil,
            'imc': imc_cat,
            'objectif': objectif,
            'sexe': sexe
        }
        
        status = "✅ Créé" if created else "📌 Existe"
        print(f"{status}: {email} ({imc_cat}, {objectif})")
    except Exception as e:
        print(f"⚠️  {email}: {e}")

# Créer des plats
print("\n📋 Créer les plats...")
plats_data = [
    ('Poulet Grillé', 'Poulet grillé avec légumes', 350, 40, 30, 10, 5, 8.0),
    ('Burger Riche', 'Burger avec frites', 900, 25, 80, 35, 2, 12.0),
    ('Salade Protéinée', 'Salade avec poulet et noix', 400, 30, 35, 15, 8, 9.0),
    ('Riz Blanc', 'Riz blanc nature', 200, 4, 45, 0.5, 1, 2.5),
    ('Steak Épais', 'Steak de boeuf 300g', 600, 55, 0, 35, 0, 15.0),
    ('Soupe Légère', 'Soupe de légumes', 150, 8, 20, 2, 8, 4.0),
]

plats = {}
for nom, desc, cal, prot, carb, lip, fib, prix in plats_data:
    plat, created = Plat.objects.get_or_create(
        nom=nom,
        defaults={
            'description': desc,
            'calorie': cal,
            'proteine': prot,
            'glucides': carb,
            'lipides': lip,
            'fibres': fib,
            'prix': prix
        }
    )
    plats[nom] = plat
    status = "✅ Créé" if created else "📌 Existe"
    print(f"{status}: {plat.nom}")

# Créer des menus
print("\n📋 Créer les menus...")
menus_data = [
    ('Menu Léger', [plats['Soupe Légère'], plats['Salade Protéinée']]),
    ('Menu Équilibré', [plats['Poulet Grillé'], plats['Riz Blanc']]),
    ('Menu Riche', [plats['Steak Épais'], plats['Burger Riche']]),
    ('Menu Muscle', [plats['Poulet Grillé'], plats['Steak Épais']]),
]

menus = {}
for nom, plat_list in menus_data:
    today = date.today()
    menu, created = Menu.objects.get_or_create(
        nom=nom,
        defaults={
            'description': f'Menu: {nom}',
            'date_debut': today,
            'date_fin': today + timedelta(days=7),
            'est_actif': True
        }
    )
    menu.plats.set(plat_list)
    menus[nom] = menu
    status = "✅ Créé" if created else "📌 Existe"
    print(f"{status}: {menu.nom} avec {len(plat_list)} plats")

# TEST: Calculer les scores de recommandation pour chaque combinaison
print("\n" + "=" * 80)
print("🧮 TESTER LES SCORES DE RECOMMANDATION")
print("=" * 80)

clear_score_cache()

# Pour chaque client et son profil
for email, client_info in clients.items():
    print(f"\n{'='*50}")
    print(f"👤 Client: {email}")
    print(f"   Profil: IMC={client_info['imc']}, Objectif={client_info['objectif']}")
    print(f"   Sexe={client_info['sexe']}, Âge=35")
    print(f"{'='*50}")
    
    # Tester chaque plat
    print(f"\n   📍 SCORES PAR PLAT:")
    plat_scores = []
    for plat_name, plat in plats.items():
        score = Plat.calculer_score_recommendation(
            plat=plat,
            categorie_imc=client_info['imc'],
            allergies='',
            restrictions='',
            age=35,
            sexe=client_info['sexe']
        )
        plat_scores.append((plat_name, score))
        print(f"      {plat_name:20} | Score: {score:3}/100")
    
    # Trier par score
    plat_scores.sort(key=lambda x: x[1], reverse=True)
    print(f"\n   📊 CLASSEMENT:")
    for i, (plat_name, score) in enumerate(plat_scores[:3], 1):
        print(f"      {i}. {plat_name:20} | {score:3}/100 ⭐")

# TEST: Calculer les valeurs nutritionnelles des menus
print("\n" + "=" * 80)
print("🧮 ANALYSER LES VALEURS NUTRITIONNELLES DES MENUS")
print("=" * 80)

for menu_name, menu in menus.items():
    print(f"\n📋 Menu: {menu_name}")
    print(f"   Plats: {', '.join(p.nom for p in menu.plats.all())}")
    
    # Calculer les totaux
    total_cal = 0
    total_prot = 0
    total_carb = 0
    total_lip = 0
    total_fib = 0
    
    for plat in menu.plats.all():
        total_cal += plat.calorie
        total_prot += plat.proteine
        total_carb += plat.glucides
        total_lip += plat.lipides
        total_fib += plat.fibres
    
    print(f"   Totaux:")
    print(f"      Calories: {total_cal} kcal")
    print(f"      Protéines: {total_prot}g ({(total_prot*4)/(total_cal*0.01):.0f}%)")
    print(f"      Glucides: {total_carb}g ({(total_carb*4)/(total_cal*0.01):.0f}%)")
    print(f"      Lipides: {total_lip}g ({(total_lip*9)/(total_cal*0.01):.0f}%)")
    print(f"      Fibres: {total_fib}g")
    
    # Évaluer l'équilibre
    protein_ratio = (total_prot * 4) / total_cal
    carb_ratio = (total_carb * 4) / total_cal
    fat_ratio = (total_lip * 9) / total_cal
    
    distance = abs(protein_ratio - 0.3) + abs(carb_ratio - 0.4) + abs(fat_ratio - 0.3)
    
    print(f"   Équilibre: ", end="")
    if distance < 0.1:
        print("✅ Excellent")
    elif distance < 0.2:
        print("✅ Bon")
    elif distance < 0.3:
        print("⚠️  Modéré")
    else:
        print("❌ Mauvais")

# TEST: Recommandations par profil
print("\n" + "=" * 80)
print("💡 RECOMMANDATIONS PAR PROFIL")
print("=" * 80)

recommendations = {
    'perte_poids': "Favoriser les plats légers avec protéines élevées",
    'prise_muscle': "Favoriser les plats riches en protéines et calories",
    'performance': "Équilibre entre calories, protéines et glucides",
}

for email, client_info in clients.items():
    objectif = client_info['objectif']
    print(f"\n👤 {email} ({objectif}):")
    print(f"   Recommandation: {recommendations.get(objectif, 'Équilibre standard')}")

print("\n" + "=" * 80)
print("✅ TEST D'INTÉGRATION TERMINÉ!")
print("=" * 80)
