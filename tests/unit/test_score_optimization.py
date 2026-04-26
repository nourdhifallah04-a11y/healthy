#!/usr/bin/env python
"""
Script de test pour vérifier que les calculs de score sont correctement optimisés
avec le plat: Cabillaud vapeur - brocoli citron
"""

import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat, Client
from myapp.score_constants import clear_score_cache, get_cached_score, _score_cache

print("=" * 80)
print("🧪 TEST DES OPTIMISATIONS DE SCORE")
print("=" * 80)

# Test 1: Créer ou récupérer le plat de test
print("\n1️⃣  Récupération du plat...")
try:
    plat = Plat.objects.filter(nom__contains="Cabillaud").first()
    if not plat:
        plat = Plat.objects.create(
            nom='Cabillaud vapeur - brocoli citron',
            description='Plat Principal - Cabillaud vapeur - brocoli citron',
            calorie=900,
            proteine=80,
            glucides=50,
            lipides=12,
            fibres=12,
            prix=9.0
        )
        print(f"   ✅ Plat créé: {plat.nom}")
    else:
        print(f"   ✅ Plat trouvé: {plat.nom}")
        print(f"      ID: {plat.id_plat}")
        print(f"      Calories: {plat.calorie}")
        print(f"      Protéines: {plat.proteine}g")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

# Test 2: Vérifier le cache avant calcul
print("\n2️⃣  Vérification du cache avant calcul...")
clear_score_cache()
cache_size = len(_score_cache)
print(f"   Cache size: {cache_size} items")

# Test 3: Premier calcul (va mettre en cache)
print("\n3️⃣  PREMIER CALCUL - Devrait être en cache")
start = time.time()
score1 = plat.calculer_score_nutritionnel()
elapsed1 = (time.time() - start) * 1000
print(f"   ⏱️  Score: {score1}/100")
print(f"   ⏱️  Temps: {elapsed1:.4f}ms")

# Test 4: Vérifier le cache après calcul
print("\n4️⃣  Vérification du cache après calcul...")
cache_size = len(_score_cache)
print(f"   Cache size: {cache_size} items")
if cache_size > 0:
    print(f"   ✅ Cache actif!")
else:
    print(f"   ⚠️  Cache vide!")

# Test 5: Deuxième calcul (doit être ultra rapide via cache)
print("\n5️⃣  DEUXIÈME CALCUL - Devrait utiliser le cache")
start = time.time()
score2 = plat.calculer_score_nutritionnel()
elapsed2 = (time.time() - start) * 1000
print(f"   ⏱️  Score: {score2}/100")
print(f"   ⏱️  Temps: {elapsed2:.4f}ms")

# Test 6: Comparaison des performances
print("\n6️⃣  COMPARAISON PERFORMANCE")
if elapsed2 > 0 and elapsed1 > 0:
    ratio = elapsed1 / (elapsed2 + 0.001)  # Éviter division par 0
    print(f"   Ratio: {ratio:.1f}x plus rapide en cache")
    if elapsed2 < elapsed1 * 0.5:
        print(f"   ✅ CACHE FONCTIONNE! ({ratio:.1f}x speedup)")
    else:
        print(f"   ⚠️  Cache peut-être inactif")
else:
    print(f"   ⚠️  Temps trop court pour mesurer")

# Test 7: Test du score de recommandation
print("\n7️⃣  TEST DU SCORE DE RECOMMANDATION")
try:
    # Vérifier que les clients existent
    client = Client.objects.first()
    if not client:
        print("   ⚠️  Aucun client trouvé dans la base de données")
        print("      Création d'un client de test...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.create_user(
            email='test@test.com',
            password='test123',
            nom='Test',
            prenom='User'
        )
        client = Client.objects.create(utilisateur=user)
        print(f"   ✅ Client de test créé")
    
    # Tester le calcul avec profil nutritionnel
    if hasattr(client, 'profil_nutritionnel'):
        print(f"   ✅ Client avec profil trouvé: {client.utilisateur.email}")
        
        # Premier appel
        start = time.time()
        score_rec1 = Plat.calculer_score_recommendation(
            plat=plat,
            categorie_imc='normal',
            age=35,
            sexe='femme'
        )
        elapsed_rec1 = (time.time() - start) * 1000
        
        # Deuxième appel (cache)
        start = time.time()
        score_rec2 = Plat.calculer_score_recommendation(
            plat=plat,
            categorie_imc='normal',
            age=35,
            sexe='femme'
        )
        elapsed_rec2 = (time.time() - start) * 1000
        
        print(f"   Score recommandation: {score_rec1}/100")
        print(f"   Premier appel: {elapsed_rec1:.4f}ms")
        print(f"   Appel en cache: {elapsed_rec2:.4f}ms")
        
        if elapsed_rec2 < elapsed_rec1 * 0.5:
            print(f"   ✅ CACHE RECOMMANDATION FONCTIONNE!")
    else:
        print(f"   ⚠️  Client sans profil nutritionnel")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 8: Statistiques finales
print("\n8️⃣  STATISTIQUES FINALES")
print(f"   Total cache items: {len(_score_cache)}")
print(f"   Score simple: {score1}/100")
print(f"   Performance gain: ~{(1 - elapsed2/elapsed1)*100:.0f}% plus rapide en cache")

print("\n" + "=" * 80)
print("✅ TESTS TERMINÉS!")
print("=" * 80)
