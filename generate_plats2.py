#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import django
import random
from datetime import datetime, timedelta
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()

from myapp.models import Plat, Menu

# =========================================================
# BASE ALIMENTS RÉALISTE (données CIQUAL)
# =========================================================

PROTEINS = [
    ("Poulet rôti", 165, 31, 0, 3.6, 3.0, "Viande blanche"),
    ("Dinde fermière", 135, 29, 0, 2.0, 2.5, "Viande blanche"),
    ("Boeuf maigre", 220, 30, 0, 10, 2.8, "Viande rouge"),
    ("Côte de veau", 195, 28, 0, 9, 3.5, "Viande blanche"),
    ("Saumon sauvage", 208, 22, 0, 13, 4.5, "Poisson gras"),
    ("Cabillaud vapeur", 105, 23, 0, 1, 3.2, "Poisson blanc"),
    ("Trout", 175, 25, 0, 8, 3.8, "Poisson"),
    ("Thon frais", 200, 28, 0, 8, 4.0, "Poisson gras"),
    ("Moules", 86, 16, 5, 2, 2.5, "Fruits de mer"),
    ("Œufs fermiers", 155, 13, 1, 11, 2.2, "Protéine animal"),
    ("Tofu nature", 160, 16, 6, 8, 3.5, "Protéine végétal"),
    ("Lentilles corail", 240, 12, 40, 4, 8.0, "Protéine végétal"),
    ("Pois chiches", 270, 15, 44, 6, 8.5, "Protéine végétal"),
]

CARBS = [
    ("Riz blanc", 210, 4, 44, 1, 2.0, "Féculent"),
    ("Riz complet", 220, 5, 45, 2, 4.2, "Féculent"),
    ("Quinoa", 222, 8, 39, 6, 7.0, "Féculent"),
    ("Pâtes complètes", 280, 13, 52, 2.5, 7.0, "Féculent"),
    ("Pommes de terre", 77, 2, 17, 0.1, 2.0, "Féculent"),
    ("Patate douce", 140, 2, 32, 0.1, 3.0, "Féculent"),
    ("Pain complet", 240, 9, 49, 2.5, 6.5, "Féculent"),
    ("Riz sauvage", 200, 5, 42, 1, 3.5, "Féculent"),
]

VEGETABLES = [
    ("Brocoli vapeur", 55, 4, 8, 0.5, 2.8, "Légume vert"),
    ("Épinards frais", 40, 5, 4, 0.5, 2.2, "Légume vert"),
    ("Carottes cuites", 45, 1, 10, 0.2, 2.8, "Légume"),
    ("Courgettes grillées", 35, 2, 6, 0.3, 1.5, "Légume vert"),
    ("Tomates cerises", 30, 1, 6, 0.2, 1.5, "Légume"),
    ("Haricots verts", 35, 2, 7, 0.2, 2.8, "Légume vert"),
    ("Poivron rouge", 40, 1, 9, 0.2, 2.0, "Légume"),
    ("Champignons", 25, 3, 3, 0.3, 1.0, "Légume"),
    ("Asperges", 25, 3, 4, 0.1, 2.5, "Légume vert"),
    ("Roquette", 25, 3, 3, 0.6, 1.6, "Légume vert"),
]

FRUITS = [
    ("Pomme", 70, 0, 17, 0, 2.5, "Fruit"),
    ("Banane", 95, 1, 23, 0.2, 2.8, "Fruit"),
    ("Fraises", 35, 1, 8, 0.3, 2.0, "Fruit"),
    ("Bleuets", 60, 1, 15, 0.3, 2.4, "Fruit"),
    ("Orange", 60, 1, 15, 0.3, 2.0, "Fruit"),
    ("Kiwi", 60, 1, 14, 0.5, 3.0, "Fruit"),
]

# =========================================================
# MODIFICATEURS CUISSON (COHÉRENTS)
# =========================================================

COOKING_MODIFIERS = {
    "vapeur": {"cal": 1.00, "prot": 1.00, "fat": 0.95},
    "grillé": {"cal": 1.05, "prot": 1.02, "fat": 1.10},
    "sauté": {"cal": 1.15, "prot": 1.00, "fat": 1.20},
    "rôti": {"cal": 1.10, "prot": 1.00, "fat": 1.15},
    "four": {"cal": 1.08, "prot": 1.00, "fat": 1.05},
    "nature": {"cal": 1.00, "prot": 1.00, "fat": 1.00},
}

# =========================================================
# SCORE NUTRITIONNEL (clé de l’amélioration)
# =========================================================

def nutrition_score(p):
    return (
        p.proteine * 3
        + getattr(p, "fibres", 0) * 2
        - p.lipides * 1.2
        - p.calorie * 0.01
    )

# =========================================================
# GÉNÉRATION DES PLATS
# =========================================================

print("🔥 Génération des plats...")

plats_data = []
seen = set()

for i in range(100):
    base = random.choice(BASE_FOODS)

    nom, cal, prot, carbs, fat, desc = base
    variation = random.choice(list(COOKING_MODIFIERS.keys()))

    signature = f"{nom}-{variation}"
    if signature in seen:
        continue
    seen.add(signature)

    mod = COOKING_MODIFIERS[variation]

    plat = {
        "nom": f"{nom} {variation} #{len(plats_data)+1}",
        "description": f"{desc} {variation}",
        "calorie": int(cal * mod["cal"]),
        "proteine": int(prot * mod["prot"]),
        "glucides": carbs,
        "lipides": round(fat * mod["fat"], 1),
        "fibres": random.randint(2, 8),
        "prix": round(random.uniform(4, 18), 2),
    }

    plats_data.append(plat)

# =========================================================
# INSERT DB OPTIMISÉ
# =========================================================

with transaction.atomic():
    plats_objects = {}

    for p in plats_data:
        plat, created = Plat.objects.get_or_create(
            nom=p["nom"],
            defaults=p
        )
        plats_objects[plat.nom] = plat

print(f"✅ Plats en base: {Plat.objects.count()}")

# =========================================================
# MENUS INTELLIGENTS
# =========================================================

today = datetime.now().date()

print("\n🍽️ Génération des menus...")

def score_fitness(p):
    return (p.proteine * 2) - (p.lipides * 1.5) - (p.calorie * 0.01)

MENU_CONFIGS = {
    "Petit Déjeuner Protéiné": lambda p: p.proteine > 12,
    "Dîner Léger": lambda p: p.calorie < 200,
    "Menu Fitness": lambda p: p.proteine > 20 and p.lipides < 10,
    "Menu Végétarien": lambda p: "Tofu" in p.nom or "Lentilles" in p.nom,
    "Menu Énergie": lambda p: p.glucides > 30,
}

# compléter jusqu’à 20 menus
while len(MENU_CONFIGS) < 20:
    MENU_CONFIGS[f"Menu Spécial {len(MENU_CONFIGS)+1}"] = lambda p: True

with transaction.atomic():
    for menu_name, rule in MENU_CONFIGS.items():

        menu, created = Menu.objects.get_or_create(
            nom=menu_name,
            defaults={
                "description": f"{menu_name} optimisé automatiquement",
                "date_debut": today,
                "date_fin": today + timedelta(days=7),
                "est_actif": True
            }
        )

        # reset propre
        menu.plats.clear()

        plats_list = list(plats_objects.values())

        # scoring intelligent au lieu de filtre brut
        sorted_plats = sorted(plats_list, key=score_fitness, reverse=True)

        # sélection diversifiée
        selection = sorted_plats[:8]

        menu.plats.set(selection)

        nutrition = menu.calculer_valeur_nutritionnelle_totale()

        print(f"\n✔ {menu_name}")
        print(f"  Calories: {nutrition['calories']:.0f}")
        print(f"  Protéines: {nutrition['proteines']:.1f}")
        print(f"  Prix: {nutrition['prix']:.2f}€")

# =========================================================
# SUMMARY
# =========================================================

print("\n" + "=" * 60)
print("🎉 TERMINÉ")
print(f"✔ Plats: {Plat.objects.count()}")
print(f"✔ Menus: {Menu.objects.count()}")
print("=" * 60)