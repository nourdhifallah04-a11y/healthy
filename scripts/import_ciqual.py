#!/usr/bin/env python
"""
Import CIQUAL 2025 :
- Télécharge XLS
- Convertit XLS → CSV (sans pandas)
- Importe 500 plats
- Génère 100 menus
"""

import os
import sys
import django
import requests
import xlrd
import csv
import random
from datetime import date, timedelta
import logging

# Désactiver le logging Django (fix Windows)
logging.disable(logging.CRITICAL)

# -----------------------------
# PROJECT ROOT
# -----------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

# -----------------------------
# CONFIG DJANGO
# -----------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'myapp.settings'))
django.setup()

from myapp.plat.models import Plat
from myapp.menu.models import Menu

# -----------------------------
# URL CIQUAL 2025
# -----------------------------
CIQUAL_URL = "https://ciqual.anses.fr/cms/sites/default/files/inline-files/Table%20Ciqual%202025_FR_2025_11_03.xls"

XLS_FILE = "ciqual_2025.xls"
CSV_FILE = "ciqual_2025.csv"


# -----------------------------
# 1. Télécharger CIQUAL
# -----------------------------
def download_ciqual():
    print("📥 Téléchargement CIQUAL 2025…")

    response = requests.get(CIQUAL_URL, allow_redirects=True, timeout=30)
    if response.status_code != 200:
        raise Exception(f"❌ Erreur téléchargement ({response.status_code})")

    with open(XLS_FILE, "wb") as f:
        f.write(response.content)

    print(f"✅ Fichier téléchargé : {XLS_FILE}")


# -----------------------------
# 2. Convertir XLS → CSV
# -----------------------------
def convert_to_csv():
    print("🔄 Conversion XLS → CSV…")

    workbook = xlrd.open_workbook(XLS_FILE)
    sheet = workbook.sheet_by_index(0)

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")

        for row_idx in range(sheet.nrows):
            writer.writerow(sheet.row_values(row_idx))

    print(f"✅ Conversion terminée : {CSV_FILE}")


# -----------------------------
# 3. Importer 500 plats
# -----------------------------
def import_plats(limit=500):
    print("🍽️ Importation des plats CIQUAL 2025…")

    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")

        plats_created = 0
        
        # Créer un mapping des colonnes avec les retours à la ligne supprimés
        def clean_key(key):
            return key.replace('\n', ' ').replace('\r', ' ').strip() if key else key

        for row in reader:
            if plats_created >= limit:
                break

            # Créer un dictionnaire avec les clés nettoyées
            clean_row = {clean_key(k): v for k, v in row.items()}
            
            nom = clean_row.get("alim_nom_fr")
            if not nom:
                continue

            # Champs CIQUAL 2025 - Chercher les colonnes de manière robuste
            calorie = 0.0
            proteine = 0.0
            glucides = 0.0
            lipides = 0.0
            fibres = 0.0
            
            # Trouver et récupérer les valeurs en cherchant les colonnes contenant les mots-clés
            for key, value in clean_row.items():
                if value:  # Ignorer les valeurs vides
                    if "kcal" in key and "100 g" in key and "Jones" not in key:
                        try:
                            calorie = float(value.replace(',', '.'))
                        except (ValueError, AttributeError):
                            pass
                    elif "Protéines" in key and "Jones" in key and "g" in key:
                        try:
                            proteine = float(value.replace(',', '.'))
                        except (ValueError, AttributeError):
                            pass
                    elif "Glucides" in key and "g" in key:
                        try:
                            glucides = float(value.replace(',', '.'))
                        except (ValueError, AttributeError):
                            pass
                    elif "Lipides" in key and "g" in key:
                        try:
                            lipides = float(value.replace(',', '.'))
                        except (ValueError, AttributeError):
                            pass
                    elif "Fibres" in key and "g" in key:
                        try:
                            fibres = float(value.replace(',', '.'))
                        except (ValueError, AttributeError):
                            pass

            prix = round(random.uniform(3, 20), 2)

            plat, created = Plat.objects.get_or_create(
                nom=nom,
                defaults={
                    "description": f"Aliment issu de la base CIQUAL 2025 : {nom}",
                    "calorie": calorie,
                    "proteine": proteine,
                    "glucides": glucides,
                    "lipides": lipides,
                    "fibres": fibres,
                    "prix": prix,
                    "est_disponible": True,
                    "isNew": False,
                    "image": "",
                },
            )

            if created:
                plats_created += 1
                print(f"   ➕ {nom}")

    print(f"➡️ Total plats créés : {plats_created}")
    return plats_created


# -----------------------------
# 4. Générer 100 menus
# -----------------------------
def generate_menus(nb=100):
    print("📦 Génération des menus…")

    plats = list(Plat.objects.all())
    if len(plats) < 10:
        print("❌ Pas assez de plats.")
        return

    for i in range(nb):
        menu = Menu.objects.create(
            nom=f"Menu automatique {i+1}",
            description="Menu généré automatiquement à partir des plats CIQUAL 2025.",
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=7),
            est_actif=True,
        )

        menu_plats = random.sample(plats, random.randint(3, 6))
        menu.plats.set(menu_plats)

        print(f"   🍽️ Menu {i+1} ({len(menu_plats)} plats)")

    print(f"➡️ Total menus créés : {nb}")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    download_ciqual()
    convert_to_csv()
    import_plats()
    generate_menus()
    print("\n🎉 Importation CIQUAL 2025 terminée !")
