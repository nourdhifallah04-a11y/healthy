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

print("=" * 70)
print("🍽️  GÉNÉRATION DE PLATS ET MENUS RÉALISTES")
print("=" * 70)

# =========================================================
# RECETTES RÉALISTES ET VARIÉES
# =========================================================

RECIPES = [
    # PETITS DÉJEUNERS
    {"nom": "Oeufs brouillés aux épinards", "type": "Petit-déjeuner", "prot": 20, "cal": 250, "glucides": 10, "lipides": 12, "fibres": 4, "prix": 3.50},
    {"nom": "Yaourt grec muesli fruits rouges", "type": "Petit-déjeuner", "prot": 18, "cal": 280, "glucides": 35, "lipides": 8, "fibres": 5, "prix": 4.00},
    {"nom": "Pancakes protéinés banane miel", "type": "Petit-déjeuner", "prot": 22, "cal": 310, "glucides": 42, "lipides": 10, "fibres": 4, "prix": 5.00},
    {"nom": "Porridge avoine baies", "type": "Petit-déjeuner", "prot": 15, "cal": 290, "glucides": 45, "lipides": 8, "fibres": 6, "prix": 3.80},
    {"nom": "Smoothie protéiné framboise", "type": "Petit-déjeuner", "prot": 20, "cal": 250, "glucides": 35, "lipides": 4, "fibres": 5, "prix": 4.50},
    
    # PLATS PRINCIPAUX - VIANDES BLANCHES
    {"nom": "Poulet rôti sauce curry - riz complet", "type": "Plat Principal", "prot": 35, "cal": 450, "glucides": 48, "lipides": 8, "fibres": 5, "prix": 10.50},
    {"nom": "Dinde fermière poêlée - légumes", "type": "Plat Principal", "prot": 38, "cal": 420, "glucides": 35, "lipides": 10, "fibres": 6, "prix": 11.00},
    {"nom": "Escalope de veau - pâtes complètes", "type": "Plat Principal", "prot": 40, "cal": 510, "glucides": 50, "lipides": 12, "fibres": 7, "prix": 13.00},
    
    # PLATS PRINCIPAUX - VIANDES ROUGES
    {"nom": "Steak de boeuf maigre - légumes rôtis", "type": "Plat Principal", "prot": 42, "cal": 480, "glucides": 42, "lipides": 14, "fibres": 6, "prix": 12.00},
    {"nom": "Côte de boeuf grillée - pommes vapeur", "type": "Plat Principal", "prot": 45, "cal": 520, "glucides": 35, "lipides": 18, "fibres": 4, "prix": 14.50},
    
    # PLATS PRINCIPAUX - POISSONS GRAS
    {"nom": "Saumon sauvage grillé - patates douces", "type": "Plat Principal", "prot": 38, "cal": 520, "glucides": 45, "lipides": 18, "fibres": 6, "prix": 14.00},
    {"nom": "Trout vapeur - riz sauvage", "type": "Plat Principal", "prot": 36, "cal": 450, "glucides": 46, "lipides": 12, "fibres": 5, "prix": 11.00},
    {"nom": "Thon frais poêlé - couscous", "type": "Plat Principal", "prot": 40, "cal": 480, "glucides": 48, "lipides": 14, "fibres": 4, "prix": 12.00},
    
    # PLATS PRINCIPAUX - POISSONS BLANCS
    {"nom": "Cabillaud vapeur - brocoli citron", "type": "Plat Principal", "prot": 40, "cal": 350, "glucides": 28, "lipides": 6, "fibres": 6, "prix": 9.00},
    {"nom": "Morue rôtie - légumes du jour", "type": "Plat Principal", "prot": 38, "cal": 380, "glucides": 32, "lipides": 8, "fibres": 5, "prix": 8.50},
    {"nom": "Sole meunière - riz blanc", "type": "Plat Principal", "prot": 35, "cal": 420, "glucides": 44, "lipides": 10, "fibres": 3, "prix": 10.00},
    
    # FRUITS DE MER
    {"nom": "Moules marinières - frites maison", "type": "Plat Principal", "prot": 32, "cal": 420, "glucides": 48, "lipides": 10, "fibres": 4, "prix": 10.00},
    {"nom": "Crevettes sautées - riz jasmin", "type": "Plat Principal", "prot": 34, "cal": 380, "glucides": 42, "lipides": 8, "fibres": 3, "prix": 11.00},
    
    # PROTÉINES VÉGÉTALES
    {"nom": "Buddha Bowl Tofu mariné - quinoa", "type": "Plat Principal", "prot": 28, "cal": 420, "glucides": 52, "lipides": 14, "fibres": 8, "prix": 8.50},
    {"nom": "Lentilles corail épicées - riz blanc", "type": "Plat Principal", "prot": 24, "cal": 380, "glucides": 58, "lipides": 6, "fibres": 9, "prix": 6.50},
    {"nom": "Pois chiches rôtis - pain complet", "type": "Plat Principal", "prot": 22, "cal": 400, "glucides": 55, "lipides": 8, "fibres": 10, "prix": 5.50},
    {"nom": "Chili végétal haricots noirs", "type": "Plat Principal", "prot": 20, "cal": 380, "glucides": 52, "lipides": 8, "fibres": 12, "prix": 6.00},
    
    # DÉJEUNERS COMPOSÉS
    {"nom": "Salade Niçoise complète oeuf", "type": "Déjeuner", "prot": 28, "cal": 340, "glucides": 25, "lipides": 14, "fibres": 6, "prix": 8.00},
    {"nom": "Sandwich complet poulet crudités", "type": "Déjeuner", "prot": 26, "cal": 380, "glucides": 45, "lipides": 10, "fibres": 7, "prix": 7.50},
    {"nom": "Wrap saumon roquette fromage", "type": "Déjeuner", "prot": 30, "cal": 420, "glucides": 38, "lipides": 16, "fibres": 5, "prix": 8.50},
    {"nom": "Soupe minestrone riche", "type": "Déjeuner", "prot": 18, "cal": 280, "glucides": 42, "lipides": 6, "fibres": 8, "prix": 5.50},
    
    # COLLATIONS / SNACKS
    {"nom": "Tiramisu léger fruits", "type": "Dessert", "prot": 12, "cal": 200, "glucides": 22, "lipides": 8, "fibres": 2, "prix": 3.50},
    {"nom": "Assiette fruits frais du jour", "type": "Dessert", "prot": 2, "cal": 120, "glucides": 28, "lipides": 0, "fibres": 4, "prix": 2.00},
    {"nom": "Barre protéinée amande", "type": "Snack", "prot": 15, "cal": 180, "glucides": 18, "lipides": 8, "fibres": 3, "prix": 2.50},
    {"nom": "Fromage blanc miel granola", "type": "Dessert", "prot": 18, "cal": 220, "glucides": 25, "lipides": 6, "fibres": 2, "prix": 3.00},
    
    # PETITS DÉJEUNERS - SUPPLÉMENTAIRES
    {"nom": "Oeufs à la coque pain complet beurre", "type": "Petit-déjeuner", "prot": 16, "cal": 240, "glucides": 28, "lipides": 10, "fibres": 4, "prix": 3.00},
    {"nom": "Tartine avocat oeuf poché", "type": "Petit-déjeuner", "prot": 18, "cal": 320, "glucides": 32, "lipides": 14, "fibres": 5, "prix": 4.50},
    {"nom": "Chia pudding lait amande miel", "type": "Petit-déjeuner", "prot": 12, "cal": 280, "glucides": 38, "lipides": 10, "fibres": 8, "prix": 4.00},
    {"nom": "Crêpes farine complète fruits frais", "type": "Petit-déjeuner", "prot": 14, "cal": 300, "glucides": 42, "lipides": 8, "fibres": 5, "prix": 4.80},
    {"nom": "Porridge miel noix amandes", "type": "Petit-déjeuner", "prot": 16, "cal": 310, "glucides": 46, "lipides": 10, "fibres": 7, "prix": 4.20},
    
    # PLATS PRINCIPAUX - SUPPLÉMENTAIRES
    {"nom": "Blanquette de veau - riz blanc", "type": "Plat Principal", "prot": 42, "cal": 520, "glucides": 48, "lipides": 14, "fibres": 4, "prix": 13.50},
    {"nom": "Navarin d'agneau - pommes vapeur", "type": "Plat Principal", "prot": 40, "cal": 480, "glucides": 42, "lipides": 16, "fibres": 5, "prix": 12.50},
    {"nom": "Coq au vin - pâtes complètes", "type": "Plat Principal", "prot": 38, "cal": 490, "glucides": 50, "lipides": 12, "fibres": 6, "prix": 11.50},
    {"nom": "Ratatouille niçoise - pain grillé", "type": "Plat Principal", "prot": 18, "cal": 320, "glucides": 48, "lipides": 8, "fibres": 10, "prix": 7.50},
    {"nom": "Risotto champignons parmesan", "type": "Plat Principal", "prot": 24, "cal": 420, "glucides": 52, "lipides": 14, "fibres": 3, "prix": 9.00},
    {"nom": "Crevettes ail persil - riz blanc", "type": "Plat Principal", "prot": 36, "cal": 380, "glucides": 44, "lipides": 8, "fibres": 2, "prix": 11.00},
    {"nom": "Filet mignon sauce moutarde - haricots", "type": "Plat Principal", "prot": 44, "cal": 520, "glucides": 38, "lipides": 18, "fibres": 6, "prix": 14.50},
    {"nom": "Escalope poulet milanaise - frites", "type": "Plat Principal", "prot": 36, "cal": 480, "glucides": 46, "lipides": 14, "fibres": 3, "prix": 9.50},
    {"nom": "Homard thermidor - riz blanc", "type": "Plat Principal", "prot": 38, "cal": 450, "glucides": 42, "lipides": 12, "fibres": 2, "prix": 15.00},
    {"nom": "Filet de lieu amande - légumes vapeur", "type": "Plat Principal", "prot": 40, "cal": 400, "glucides": 30, "lipides": 10, "fibres": 5, "prix": 10.00},
    {"nom": "Paella espagnole mixte", "type": "Plat Principal", "prot": 40, "cal": 510, "glucides": 54, "lipides": 14, "fibres": 4, "prix": 12.00},
    {"nom": "Oeufs bénédictine - bacon crispy", "type": "Plat Principal", "prot": 24, "cal": 380, "glucides": 28, "lipides": 16, "fibres": 2, "prix": 8.50},
    {"nom": "Côte de porc sauce cidre - chou-fleur", "type": "Plat Principal", "prot": 42, "cal": 500, "glucides": 32, "lipides": 16, "fibres": 5, "prix": 11.00},
    {"nom": "Canard confit - pommes sautées", "type": "Plat Principal", "prot": 40, "cal": 560, "glucides": 38, "lipides": 20, "fibres": 4, "prix": 13.00},
    {"nom": "Tourte courgette ricotta - salade verte", "type": "Plat Principal", "prot": 26, "cal": 400, "glucides": 38, "lipides": 14, "fibres": 7, "prix": 8.00},
    
    # DÉJEUNERS COMPOSÉS - SUPPLÉMENTAIRES
    {"nom": "Soupe à l'oignon gratinée - pain complet", "type": "Déjeuner", "prot": 16, "cal": 300, "glucides": 40, "lipides": 8, "fibres": 6, "prix": 6.50},
    {"nom": "Salade Caprese tomate mozzarella", "type": "Déjeuner", "prot": 22, "cal": 320, "glucides": 20, "lipides": 18, "fibres": 4, "prix": 8.50},
    {"nom": "Quiche Lorraine - salade assortie", "type": "Déjeuner", "prot": 28, "cal": 420, "glucides": 35, "lipides": 16, "fibres": 5, "prix": 9.00},
    
    # DESSERTS - SUPPLÉMENTAIRES
    {"nom": "Mousse au chocolat noir 70%", "type": "Dessert", "prot": 10, "cal": 220, "glucides": 18, "lipides": 14, "fibres": 3, "prix": 4.00},
    {"nom": "Tarte Tatin pommes caramélisées", "type": "Dessert", "prot": 8, "cal": 280, "glucides": 38, "lipides": 12, "fibres": 3, "prix": 5.50},
    {"nom": "Crème caramel léger", "type": "Dessert", "prot": 10, "cal": 200, "glucides": 25, "lipides": 6, "fibres": 0, "prix": 3.50},
    {"nom": "Salade fruits rouges coulis", "type": "Dessert", "prot": 3, "cal": 140, "glucides": 32, "lipides": 1, "fibres": 5, "prix": 3.00},
    
    # SNACKS - SUPPLÉMENTAIRES
    {"nom": "Barre granola maison fruits secs", "type": "Snack", "prot": 12, "cal": 210, "glucides": 28, "lipides": 8, "fibres": 4, "prix": 2.50},
    {"nom": "Yaourt nature pur sucre coco", "type": "Snack", "prot": 16, "cal": 180, "glucides": 20, "lipides": 4, "fibres": 2, "prix": 2.00},
    
    # PLATS TRADITIONNELS FRANÇAIS - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Cassoulet traditionnel", "type": "Plat Principal", "prot": 38, "cal": 540, "glucides": 52, "lipides": 18, "fibres": 7, "prix": 12.00},
    {"nom": "Tarte bowl fromage frais crudités", "type": "Plat Principal", "prot": 20, "cal": 360, "glucides": 38, "lipides": 14, "fibres": 6, "prix": 9.00},
    {"nom": "Blanquette de poulet sauce crème", "type": "Plat Principal", "prot": 36, "cal": 480, "glucides": 45, "lipides": 14, "fibres": 4, "prix": 10.50},
    {"nom": "Bœuf Bourguignon aux légumes", "type": "Plat Principal", "prot": 42, "cal": 520, "glucides": 42, "lipides": 18, "fibres": 5, "prix": 13.50},
    {"nom": "Gratin de ravioles comté dauphiné", "type": "Plat Principal", "prot": 26, "cal": 440, "glucides": 48, "lipides": 16, "fibres": 3, "prix": 10.00},
    {"nom": "Rougail saucisse réunionnais", "type": "Plat Principal", "prot": 32, "cal": 480, "glucides": 50, "lipides": 16, "fibres": 5, "prix": 9.50},
    
    # PÂTES - RÉCUPÉRÉES DEPUIS INTERNET
    {"nom": "Spaghetti alle vongole palourdes", "type": "Plat Principal", "prot": 28, "cal": 420, "glucides": 52, "lipides": 12, "fibres": 3, "prix": 11.50},
    {"nom": "Gnocchis au chorizo croustillants", "type": "Plat Principal", "prot": 24, "cal": 480, "glucides": 54, "lipides": 16, "fibres": 2, "prix": 10.00},
    {"nom": "Spaghetti au thon à l'italienne", "type": "Plat Principal", "prot": 32, "cal": 450, "glucides": 50, "lipides": 12, "fibres": 3, "prix": 9.00},
    {"nom": "Tagliatelles saumon fumé italienne", "type": "Plat Principal", "prot": 30, "cal": 480, "glucides": 50, "lipides": 14, "fibres": 2, "prix": 11.00},
    {"nom": "Pâtes aux quatre fromages", "type": "Plat Principal", "prot": 22, "cal": 460, "glucides": 52, "lipides": 18, "fibres": 1, "prix": 9.00},
    {"nom": "Cannelloni au boeuf sauce tomate", "type": "Plat Principal", "prot": 28, "cal": 480, "glucides": 48, "lipides": 16, "fibres": 3, "prix": 10.50},
    {"nom": "Pâtes linguine crevettes sauce crémeuse", "type": "Plat Principal", "prot": 30, "cal": 450, "glucides": 48, "lipides": 14, "fibres": 2, "prix": 11.00},
    {"nom": "Cannellonis ricotta épinards", "type": "Plat Principal", "prot": 26, "cal": 420, "glucides": 46, "lipides": 14, "fibres": 5, "prix": 9.50},
    
    # PLATS À BASE DE RIZ - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Riz pilaf traditionnel", "type": "Plat Principal", "prot": 14, "cal": 380, "glucides": 64, "lipides": 8, "fibres": 3, "prix": 6.00},
    {"nom": "Risotto asperges vertes parmesan", "type": "Plat Principal", "prot": 24, "cal": 420, "glucides": 52, "lipides": 14, "fibres": 4, "prix": 10.00},
    {"nom": "Risotto au chorizo épicé", "type": "Plat Principal", "prot": 26, "cal": 480, "glucides": 54, "lipides": 16, "fibres": 2, "prix": 9.50},
    {"nom": "Bobun au boeuf sauce nuoc mam", "type": "Plat Principal", "prot": 30, "cal": 420, "glucides": 50, "lipides": 12, "fibres": 4, "prix": 9.00},
    {"nom": "Risotto aux champignons facile", "type": "Plat Principal", "prot": 20, "cal": 400, "glucides": 54, "lipides": 12, "fibres": 3, "prix": 8.50},
    
    # VIANDES - RÉCUPÉRÉES DEPUIS INTERNET
    {"nom": "Filet mignon de porc au four", "type": "Plat Principal", "prot": 40, "cal": 480, "glucides": 32, "lipides": 16, "fibres": 3, "prix": 12.00},
    {"nom": "Poulet maison façon KFC", "type": "Plat Principal", "prot": 38, "cal": 520, "glucides": 42, "lipides": 18, "fibres": 2, "prix": 10.50},
    {"nom": "Filet mignon au Air Fryer", "type": "Plat Principal", "prot": 42, "cal": 500, "glucides": 35, "lipides": 16, "fibres": 2, "prix": 11.50},
    {"nom": "Cuisse de dinde rôtie au four", "type": "Plat Principal", "prot": 40, "cal": 420, "glucides": 28, "lipides": 12, "fibres": 2, "prix": 10.00},
    {"nom": "Blanc de poulet au Air Fryer", "type": "Plat Principal", "prot": 38, "cal": 380, "glucides": 30, "lipides": 10, "fibres": 2, "prix": 9.50},
    {"nom": "Paupiettes de porc mijotées", "type": "Plat Principal", "prot": 36, "cal": 460, "glucides": 40, "lipides": 14, "fibres": 3, "prix": 10.50},
    {"nom": "Dakgangjeong poulet frit coréen", "type": "Plat Principal", "prot": 36, "cal": 540, "glucides": 48, "lipides": 18, "fibres": 2, "prix": 11.00},
    {"nom": "Cuisses de poulet pommes de terre", "type": "Plat Principal", "prot": 38, "cal": 500, "glucides": 45, "lipides": 14, "fibres": 4, "prix": 10.00},
    {"nom": "Rôti de boeuf rosbeef au four", "type": "Plat Principal", "prot": 44, "cal": 520, "glucides": 35, "lipides": 18, "fibres": 2, "prix": 13.00},
    
    # POISSONS - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Pavés saumon Air Fryer citron", "type": "Plat Principal", "prot": 38, "cal": 480, "glucides": 28, "lipides": 16, "fibres": 2, "prix": 12.00},
    {"nom": "Encornets sautés ail persil", "type": "Plat Principal", "prot": 30, "cal": 360, "glucides": 25, "lipides": 12, "fibres": 2, "prix": 10.50},
    {"nom": "Morue au four à la portugaise", "type": "Plat Principal", "prot": 36, "cal": 400, "glucides": 32, "lipides": 10, "fibres": 3, "prix": 10.00},
    {"nom": "Sardines au barbecue grillées", "type": "Plat Principal", "prot": 32, "cal": 420, "glucides": 28, "lipides": 14, "fibres": 2, "prix": 9.50},
    {"nom": "Crevettes ail lait coco curry", "type": "Plat Principal", "prot": 34, "cal": 420, "glucides": 35, "lipides": 14, "fibres": 2, "prix": 11.00},
    {"nom": "Filets sardine grillés au four", "type": "Plat Principal", "prot": 30, "cal": 400, "glucides": 30, "lipides": 12, "fibres": 2, "prix": 9.00},
    {"nom": "Poulpe au barbecue tendre", "type": "Plat Principal", "prot": 32, "cal": 380, "glucides": 28, "lipides": 12, "fibres": 2, "prix": 10.50},
    
    # LÉGUMES - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Courgettes au Air Fryer croustillantes", "type": "Plat Principal", "prot": 6, "cal": 180, "glucides": 18, "lipides": 8, "fibres": 4, "prix": 4.50},
    {"nom": "Dahl de lentilles corail épices", "type": "Plat Principal", "prot": 22, "cal": 340, "glucides": 48, "lipides": 8, "fibres": 10, "prix": 6.50},
    {"nom": "Aubergines farcies boeuf haché", "type": "Plat Principal", "prot": 28, "cal": 420, "glucides": 42, "lipides": 14, "fibres": 6, "prix": 9.00},
    {"nom": "Chou-fleur au Air Fryer dorés", "type": "Plat Principal", "prot": 8, "cal": 200, "glucides": 20, "lipides": 8, "fibres": 5, "prix": 4.50},
    {"nom": "Poivrons au Air Fryer farcis", "type": "Plat Principal", "prot": 14, "cal": 280, "glucides": 32, "lipides": 10, "fibres": 5, "prix": 5.50},
    
    # CÉRÉALES - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Polenta au four croustillante", "type": "Plat Principal", "prot": 8, "cal": 280, "glucides": 42, "lipides": 10, "fibres": 3, "prix": 5.00},
    {"nom": "Panisses au four dorées", "type": "Plat Principal", "prot": 6, "cal": 220, "glucides": 38, "lipides": 6, "fibres": 4, "prix": 4.50},
    {"nom": "Ebly au curry et coco", "type": "Plat Principal", "prot": 12, "cal": 360, "glucides": 54, "lipides": 10, "fibres": 4, "prix": 6.50},
    {"nom": "Quinoa poulet légumes du soleil", "type": "Plat Principal", "prot": 28, "cal": 420, "glucides": 50, "lipides": 12, "fibres": 7, "prix": 9.50},
    
    # FROMAGE - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Croziflette traditionnelle savoyarde", "type": "Plat Principal", "prot": 22, "cal": 480, "glucides": 48, "lipides": 18, "fibres": 2, "prix": 10.00},
    {"nom": "Tartiflette au reblochon rapide", "type": "Plat Principal", "prot": 24, "cal": 500, "glucides": 50, "lipides": 18, "fibres": 2, "prix": 10.50},
    {"nom": "Camembert rôti au four miel", "type": "Plat Principal", "prot": 18, "cal": 380, "glucides": 32, "lipides": 18, "fibres": 1, "prix": 7.50},
    {"nom": "Camembert rôti au barbecue", "type": "Plat Principal", "prot": 18, "cal": 380, "glucides": 32, "lipides": 18, "fibres": 1, "prix": 7.50},
    {"nom": "Mont d'or au four classique", "type": "Plat Principal", "prot": 20, "cal": 400, "glucides": 35, "lipides": 18, "fibres": 1, "prix": 8.50},
    {"nom": "Tofu façon porc au caramel", "type": "Plat Principal", "prot": 20, "cal": 320, "glucides": 40, "lipides": 10, "fibres": 4, "prix": 7.00},
    {"nom": "Chèvre chaud au Air Fryer miel", "type": "Plat Principal", "prot": 16, "cal": 340, "glucides": 35, "lipides": 14, "fibres": 2, "prix": 6.50},
    
    # FAST FOOD - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Croque-monsieur classique jambon", "type": "Déjeuner", "prot": 24, "cal": 420, "glucides": 38, "lipides": 16, "fibres": 2, "prix": 7.50},
    {"nom": "Pizza maison personnalisée", "type": "Plat Principal", "prot": 20, "cal": 460, "glucides": 52, "lipides": 16, "fibres": 2, "prix": 8.00},
    {"nom": "Wrap grillé poulet fromage", "type": "Déjeuner", "prot": 28, "cal": 420, "glucides": 42, "lipides": 14, "fibres": 3, "prix": 7.50},
    {"nom": "Pizza margherita tomate frais", "type": "Plat Principal", "prot": 18, "cal": 400, "glucides": 48, "lipides": 14, "fibres": 2, "prix": 7.50},
    {"nom": "Wraps fromage saumon concombre", "type": "Déjeuner", "prot": 26, "cal": 380, "glucides": 40, "lipides": 12, "fibres": 2, "prix": 8.00},
    {"nom": "Quesadillas viande hachée tex-mex", "type": "Plat Principal", "prot": 22, "cal": 440, "glucides": 46, "lipides": 16, "fibres": 2, "prix": 7.50},
    {"nom": "Kebab maison poulet légumes", "type": "Plat Principal", "prot": 28, "cal": 420, "glucides": 45, "lipides": 12, "fibres": 4, "prix": 8.00},
    {"nom": "Sandwich au poulet complet", "type": "Déjeuner", "prot": 26, "cal": 400, "glucides": 42, "lipides": 12, "fibres": 3, "prix": 7.00},
    {"nom": "Pizza Air Fryer rapide", "type": "Plat Principal", "prot": 18, "cal": 420, "glucides": 48, "lipides": 14, "fibres": 2, "prix": 6.50},
    {"nom": "Gaufres patate douce salée", "type": "Plat Principal", "prot": 8, "cal": 320, "glucides": 45, "lipides": 10, "fibres": 5, "prix": 6.00},
]

# =========================================================
# GÉNÉRER LES PLATS
# =========================================================

print("\n🔥 Génération des plats réalistes...")

with transaction.atomic():
    # Supprimer les anciens plats
    Plat.objects.all().delete()
    
    plats_objects = {}
    
    for recipe in RECIPES:
        plat = Plat.objects.create(
            nom=recipe["nom"],
            description=f"{recipe['type']} - {recipe['nom']}",
            calorie=recipe["cal"],
            proteine=recipe["prot"],
            glucides=recipe["glucides"],
            lipides=recipe["lipides"],
            fibres=recipe["fibres"],
            prix=recipe["prix"]
        )
        plats_objects[recipe["nom"]] = plat
        print(f"  ✅ {plat.nom}")

print(f"✅ Total plats générés: {Plat.objects.count()}")

# =========================================================
# GÉNÉRER LES MENUS
# =========================================================

print("\n🍽️  Génération des menus équilibrés...")

MENUS = [
    # Menus petit-déjeuner complets
    {"nom": "Menu Matin Énergique", "plats": ["Oeufs brouillés aux épinards", "Pancakes protéinés banane miel"], "description": "Petit-déjeuner riche en protéines"},
    {"nom": "Menu Petit Déjeuner Léger", "plats": ["Yaourt grec muesli fruits rouges", "Assiette fruits frais du jour"], "description": "Petit-déjeuner équilibré et léger"},
    {"nom": "Menu Brunch Gourmand", "plats": ["Tartine avocat oeuf poché", "Smoothie protéiné framboise"], "description": "Brunch complet et savoureux"},
    
    # Menus déjeuner 
    {"nom": "Menu Équilibré Classique", "plats": ["Poulet rôti sauce curry - riz complet", "Salade Niçoise complète oeuf", "Assiette fruits frais du jour"], "description": "Déjeuner équilibré traditionnel"},
    {"nom": "Menu Méditerranéen", "plats": ["Saumon sauvage grillé - patates douces", "Salade Caprese tomate mozzarella", "Tiramisu léger fruits"], "description": "Cuisine méditerranéenne saine"},
    {"nom": "Menu Végétarien Gourmand", "plats": ["Ratatouille niçoise - pain grillé", "Lentilles corail épicées - riz blanc", "Mousse au chocolat noir 70%"], "description": "Déjeuner végétarien savoureux"},
    {"nom": "Menu Fruits de Mer Léger", "plats": ["Crevettes ail persil - riz blanc", "Soupe minestrone riche", "Salade fruits rouges coulis"], "description": "Déjeuner léger et protéiné"},
    
    # Menus dîner
    {"nom": "Menu Dîner Français Raffiné", "plats": ["Blanquette de veau - riz blanc", "Salade Niçoise complète oeuf", "Crème caramel léger"], "description": "Dîner classique français élégant"},
    {"nom": "Menu Dîner Viande Rouge", "plats": ["Filet mignon sauce moutarde - haricots", "Steak de boeuf maigre - légumes rôtis", "Tarte Tatin pommes caramélisées"], "description": "Dîner copieux et gourmand"},
    {"nom": "Menu Dîner Léger Santé", "plats": ["Filet de lieu amande - légumes vapeur", "Wrap saumon roquette fromage", "Yaourt nature pur sucre coco"], "description": "Dîner diététique et sain"},
    {"nom": "Menu Dîner Poisson Blanc", "plats": ["Cabillaud vapeur - brocoli citron", "Morue rôtie - légumes du jour", "Assiette fruits frais du jour"], "description": "Dîner protéiné light"},
    
    # MENUS DÉJEUNER INNOVANTS
    {"nom": "Menu Pasta Italienne", "plats": ["Spaghetti alle vongole palourdes", "Pâtes aux quatre fromages", "Assiette fruits frais du jour"], "description": "Pâtes fraîches à l'italienne"},
    {"nom": "Menu Riz Exotique", "plats": ["Risotto aux asperges vertes parmesan", "Bobun au boeuf sauce nuoc mam", "Tiramisu léger fruits"], "description": "Plats à base de riz savoureux"},
    {"nom": "Menu Français Gourmand", "plats": ["Cassoulet traditionnel", "Blanquette de poulet sauce crème", "Crème caramel léger"], "description": "Cuisine française authentique"},
    {"nom": "Menu Barbecue Estival", "plats": ["Sardines au barbecue grillées", "Cuisses de poulet pommes de terre", "Salade fruits rouges coulis"], "description": "Grillades estivales"},
    {"nom": "Menu Air Fryer Santé", "plats": ["Blanc de poulet au Air Fryer", "Courgettes au Air Fryer croustillantes", "Yaourt nature pur sucre coco"], "description": "Cuisson saine à l'Air Fryer"},
    {"nom": "Menu Fromage Alpin", "plats": ["Croziflette traditionnelle savoyarde", "Camembert rôti au four miel", "Barre protéinée amande"], "description": "Spécialités alpines généreuses"},
    {"nom": "Menu Fruits de Mer Festif", "plats": ["Encornets sautés ail persil", "Crevettes ail lait coco curry", "Mousse au chocolat noir 70%"], "description": "Fruits de mer délicats"},
    {"nom": "Menu Vegetarien Savoyard", "plats": ["Dahl de lentilles corail épices", "Aubergines farcies boeuf haché", "Tarte Tatin pommes caramélisées"], "description": "Menu végétarien riche"},
    {"nom": "Menu Street Food", "plats": ["Kebab maison poulet légumes", "Wrap grillé poulet fromage", "Fromage blanc miel granola"], "description": "Cuisine de rue revisitée"},
    {"nom": "Menu Thon et Pâtes", "plats": ["Spaghetti au thon à l'italienne", "Tagliatelles saumon fumé italienne", "Assiette fruits frais du jour"], "description": "Pâtes et poisson"},
    
    # MENUS DÎNER SOPHISTIQUÉS
    {"nom": "Menu Dîner Provence", "plats": ["Ratatouille niçoise - pain grillé", "Pavés saumon Air Fryer citron", "Mousse au chocolat noir 70%"], "description": "Saveurs méditerranéennes"},
    {"nom": "Menu Dîner Viande Raffinée", "plats": ["Filet mignon de porc au four", "Filet mignon au Air Fryer", "Crème caramel léger"], "description": "Viandes nobles délicieuses"},
    {"nom": "Menu Dîner Bourguignon", "plats": ["Bœuf Bourguignon aux légumes", "Rôti de boeuf rosbeef au four", "Mousse au chocolat noir 70%"], "description": "Cuisine bourgeoise classique"},
    {"nom": "Menu Dîner Végétal", "plats": ["Polenta au four croustillante", "Chou-fleur au Air Fryer dorés", "Salade fruits rouges coulis"], "description": "Dîner 100% végétal équilibré"},
    
    # MENUS SPÉCIALISÉS - RÉCUPÉRÉS DEPUIS INTERNET
    {"nom": "Menu Régime Cétogène", "plats": ["Filet mignon au Air Fryer", "Poulpe au barbecue tendre", "Barre granola maison fruits secs"], "description": "Faible en glucides"},
    {"nom": "Menu Tropical Exotique", "plats": ["Crevettes ail lait coco curry", "Riz pilaf traditionnel", "Yaourt nature pur sucre coco"], "description": "Saveurs tropicales"},
    {"nom": "Menu Coréen Épicé", "plats": ["Dakgangjeong poulet frit coréen", "Bobun au boeuf sauce nuoc mam", "Assiette fruits frais du jour"], "description": "Cuisine coréenne authentique"},
    {"nom": "Menu Pizza & Pastas", "plats": ["Pizza maison personnalisée", "Cannelloni au boeuf sauce tomate", "Fromage blanc miel granola"], "description": "Classiques italiens"},
    {"nom": "Menu Poulet Rôti", "plats": ["Poulet maison façon KFC", "Cuisse de dinde rôtie au four", "Barre protéinée amande"], "description": "Volailles rôties gourmandes"},
    {"nom": "Menu Gratin Gourmand", "plats": ["Gratin de ravioles comté dauphiné", "Tartiflette au reblochon rapide", "Assiette fruits frais du jour"], "description": "Gratins réconfortants"},
]

with transaction.atomic():
    # Supprimer les anciens menus
    Menu.objects.all().delete()
    
    today = datetime.now().date()
    
    for menu_info in MENUS:
        plats_list = []
        for nom_plat in menu_info["plats"]:
            if nom_plat in plats_objects:
                plat = plats_objects[nom_plat]
                plats_list.append(plat)
            else:
                print(f"  ⚠️  Plat '{nom_plat}' non trouvé")
        
        if plats_list:
            menu = Menu.objects.create(
                nom=menu_info["nom"],
                description=menu_info["description"],
                date_debut=today,
                date_fin=today + timedelta(days=7),
                est_actif=True
            )
            menu.plats.set(plats_list)
            print(f"  ✅ {menu.nom} ({len(plats_list)} plats)")

print(f"✅ Total menus générés: {Menu.objects.count()}")

print("\n" + "=" * 70)
print("✅ GÉNÉRATION COMPLÈTE AVEC SUCCÈS!")
print("=" * 70)

# =========================================================
# MENUS THÉMATIQUES RÉALISTES
# =========================================================

print("\n🍽️  Génération des menus thématiques...")

MENU_TEMPLATES = [
    {
        "nom": "Menu Fitness Protéiné",
        "description": "Riche en protéines pour la musculation",
        "filters": lambda p: p.proteine >= 35 and p.calorie <= 550
    },
    {
        "nom": "Menu Minceur Équilibré",
        "description": "Faible en calories, riche en fibres",
        "filters": lambda p: p.calorie <= 400 and p.fibres >= 5
    },
    {
        "nom": "Menu Gourmand Sain",
        "description": "Savoureux et nutritif",
        "filters": lambda p: p.prix >= 8.00 and p.proteine >= 25
    },
    {
        "nom": "Menu Végétarien Complet",
        "description": "100% plantes, protéiné et équilibré",
        "filters": lambda p: "Buddha" in p.nom or "Lentilles" in p.nom or "Pois chiches" in p.nom or "Chili" in p.nom
    },
    {
        "nom": "Menu Gourmet Poisson",
        "description": "Poissons frais et fruits de mer",
        "filters": lambda p: ("Saumon" in p.nom or "Trout" in p.nom or "Cabillaud" in p.nom or "Moules" in p.nom or "Crevettes" in p.nom)
    },
    {
        "nom": "Menu Gourmet Volaille",
        "description": "Viandes blanches délicieuses",
        "filters": lambda p: ("Poulet" in p.nom or "Dinde" in p.nom or "Veau" in p.nom)
    },
    {
        "nom": "Menu Premium Viande",
        "description": "Steaks et viandes nobles",
        "filters": lambda p: ("Steak" in p.nom or "Côte" in p.nom or "Boeuf" in p.nom)
    },
    {
        "nom": "Menu Petit-Déjeuner Complet",
        "description": "Petit-déj énergétique pour bien commencer",
        "filters": lambda p: "Petit-déjeuner" in p.description
    },
    {
        "nom": "Menu Midi Rapide",
        "description": "Déjeuner équilibré et rapide",
        "filters": lambda p: ("Salade" in p.nom or "Sandwich" in p.nom or "Wrap" in p.nom or "Soupe" in p.nom)
    },
    {
        "nom": "Menu Détox Léger",
        "description": "Léger et purifiant",
        "filters": lambda p: p.calorie <= 350 and p.lipides <= 8
    },
]

today = datetime.now().date()

with transaction.atomic():
    # Supprimer les anciens menus
    Menu.objects.all().delete()
    
    for template in MENU_TEMPLATES:
        menu = Menu.objects.create(
            nom=template["nom"],
            description=template["description"],
            date_debut=today,
            date_fin=today + timedelta(days=7),
            est_actif=True
        )
        
        # Récupérer tous les plats
        all_plats = Plat.objects.all()
        
        # Filtrer selon le template
        filtered_plats = [p for p in all_plats if template["filters"](p)]
        
        # Ajouter jusqu'à 6 plats au menu
        if filtered_plats:
            selected = random.sample(filtered_plats, min(6, len(filtered_plats)))
            menu.plats.set(selected)
        
        print(f"  ✅ {template['nom']} ({menu.plats.count()} plats)")

print(f"\n✅ Total menus générés: {Menu.objects.count()}")

print("\n" + "=" * 70)
print("🎉 GÉNÉRATION TERMINÉE!")
print("=" * 70)
print(f"📊 Statistiques finales:")
print(f"   • Plats: {Plat.objects.count()}")
print(f"   • Menus: {Menu.objects.count()}")
print("=" * 70)
