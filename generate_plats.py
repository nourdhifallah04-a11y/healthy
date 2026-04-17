#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat, Menu
from django.db import transaction

# Données pour générer les plats
plats_data = [
    {
        'nom': 'Salade Méditerranéenne',
        'description': 'Salade fraîche avec tomates, concombre, olives noires et fromage feta',
        'calorie': 280,
        'proteine': 10,
        'glucides': 12,
        'lipides': 20,
        'fibres': 4,
        'prix': 8.50
    },
    {
        'nom': 'Poulet Grillé aux Herbes',
        'description': 'Filet de poulet grillé avec herbes fraîches et légumes de saison',
        'calorie': 280,
        'proteine': 42,
        'glucides': 0,
        'lipides': 12,
        'fibres': 0,
        'prix': 12.00
    },
    {
        'nom': 'Riz Complet aux Légumes',
        'description': 'Riz complet cuit avec brocoli, carottes et pois chiches',
        'calorie': 330,
        'proteine': 12,
        'glucides': 58,
        'lipides': 6,
        'fibres': 5,
        'prix': 7.50
    },
    {
        'nom': 'Saumon Poêlé',
        'description': 'Filet de saumon frais poêlé avec citron et herbes aromatiques',
        'calorie': 360,
        'proteine': 38,
        'glucides': 0,
        'lipides': 22,
        'fibres': 0,
        'prix': 14.99
    },
    {
        'nom': 'Pâtes Complètes à la Tomate',
        'description': 'Pâtes complètes avec sauce tomate maison et basilic frais',
        'calorie': 360,
        'proteine': 14,
        'glucides': 62,
        'lipides': 5,
        'fibres': 8,
        'prix': 8.00
    },
    {
        'nom': 'Poitrine de Dinde Rôtie',
        'description': 'Poitrine de dinde rôtie avec moutarde de Dijon et légumes racines',
        'calorie': 280,
        'proteine': 45,
        'glucides': 2,
        'lipides': 8,
        'fibres': 1,
        'prix': 11.50
    },
    {
        'nom': 'Quinoa aux Brocoli',
        'description': 'Quinoa protéiné mélangé avec brocoli et graines de tournesol',
        'calorie': 360,
        'proteine': 14,
        'glucides': 52,
        'lipides': 14,
        'fibres': 7,
        'prix': 9.99
    },
    {
        'nom': 'Truite Arc-en-ciel',
        'description': 'Truite fraîche cuite en papillote avec fenouil et citron',
        'calorie': 280,
        'proteine': 35,
        'glucides': 0,
        'lipides': 15,
        'fibres': 0,
        'prix': 13.50
    },
    {
        'nom': 'Pois Chiches Rôtis',
        'description': 'Pois chiches croustillants rôtis avec épices méditerranéennes',
        'calorie': 320,
        'proteine': 16,
        'glucides': 32,
        'lipides': 14,
        'fibres': 8,
        'prix': 6.00
    },
    {
        'nom': 'Œufs à la Coque et Épinards',
        'description': 'Œufs mollets accompagnés d\'épinards frais et pain complet',
        'calorie': 260,
        'proteine': 16,
        'glucides': 20,
        'lipides': 14,
        'fibres': 6,
        'prix': 6.50
    },
    {
        'nom': 'Steak Maigre Poêlé',
        'description': 'Steak de bœuf maigre poêlé avec ail et persil',
        'calorie': 350,
        'proteine': 50,
        'glucides': 0,
        'lipides': 16,
        'fibres': 0,
        'prix': 15.99
    },
    {
        'nom': 'Soupe de Légumes Minestrone',
        'description': 'Soupe riche avec pâtes, haricots et variété de légumes',
        'calorie': 220,
        'proteine': 10,
        'glucides': 35,
        'lipides': 4,
        'fibres': 8,
        'prix': 6.00
    },
    {
        'nom': 'Tofu Mariné aux Épices',
        'description': 'Bloc de tofu nature mariné dans un mélange d\'épices asiatiques',
        'calorie': 180,
        'proteine': 20,
        'glucides': 8,
        'lipides': 10,
        'fibres': 2,
        'prix': 7.00
    },
    {
        'nom': 'Patate Douce Rôtie',
        'description': 'Patate douce rôtie au four avec une touche de cannelle',
        'calorie': 160,
        'proteine': 3,
        'glucides': 36,
        'lipides': 1,
        'fibres': 6,
        'prix': 4.50
    },
    {
        'nom': 'Cabillaud Vapeur',
        'description': 'Filet de cabillaud cuit à la vapeur avec citron et herbes',
        'calorie': 230,
        'proteine': 40,
        'glucides': 2,
        'lipides': 5,
        'fibres': 1,
        'prix': 12.00
    },
    {
        'nom': 'Lentilles Corail au Curcuma',
        'description': 'Lentilles corail cuites avec curcuma, oignon et épices',
        'calorie': 310,
        'proteine': 18,
        'glucides': 45,
        'lipides': 4,
        'fibres': 12,
        'prix': 5.99
    },
    {
        'nom': 'Œufs Brouillés aux Champignons',
        'description': 'Œufs brouillés avec champignons de Paris et fromage râpé léger',
        'calorie': 280,
        'proteine': 20,
        'glucides': 12,
        'lipides': 18,
        'fibres': 2,
        'prix': 7.50
    },
    {
        'nom': 'Morue à la Méditerranéenne',
        'description': 'Morue avec tomates, olives, câpres et herbes de Provence',
        'calorie': 320,
        'proteine': 42,
        'glucides': 8,
        'lipides': 12,
        'fibres': 3,
        'prix': 13.99
    },
    {
        'nom': 'Haricots Verts Sautés',
        'description': 'Haricots verts frais sautés à l\'ail avec un trait d\'huile d\'olive',
        'calorie': 90,
        'proteine': 6,
        'glucides': 15,
        'lipides': 2,
        'fibres': 8,
        'prix': 4.00
    },
    {
        'nom': 'Yaourt Grec Nature',
        'description': 'Yaourt grec riche en protéines sans sucre ajouté',
        'calorie': 150,
        'proteine': 20,
        'glucides': 8,
        'lipides': 4,
        'fibres': 0,
        'prix': 3.50
    },
    {
        'nom': 'Escalope de Veau Panée',
        'description': 'Escalope de veau fine panée à la chapelure complète',
        'calorie': 380,
        'proteine': 48,
        'glucides': 18,
        'lipides': 14,
        'fibres': 2,
        'prix': 14.50
    },
    {
        'nom': 'Courgettes Farcies',
        'description': 'Courgettes évidées farcies avec riz complet et légumes',
        'calorie': 280,
        'proteine': 14,
        'glucides': 38,
        'lipides': 8,
        'fibres': 6,
        'prix': 8.99
    },
    {
        'nom': 'Crevettes Sautées à l\'Ail',
        'description': 'Crevettes fraîches sautées à l\'ail avec persil et citron',
        'calorie': 240,
        'proteine': 38,
        'glucides': 4,
        'lipides': 8,
        'fibres': 2,
        'prix': 11.99
    },
    {
        'nom': 'Riz Basmati Blanc',
        'description': 'Riz basmati blanc cuit à la perfection avec un trait de bouillon',
        'calorie': 280,
        'proteine': 8,
        'glucides': 58,
        'lipides': 2,
        'fibres': 2,
        'prix': 3.99
    },
    {
        'nom': 'Chou-fleur Rôti',
        'description': 'Chou-fleur rôti au four avec curcuma et paprika',
        'calorie': 140,
        'proteine': 12,
        'glucides': 20,
        'lipides': 4,
        'fibres': 8,
        'prix': 4.99
    },
    {
        'nom': 'Jambon Blanc Fermier',
        'description': 'Jambon blanc fermier maigre tranchéleur qualité supérieure',
        'calorie': 200,
        'proteine': 38,
        'glucides': 1,
        'lipides': 4,
        'fibres': 0,
        'prix': 8.99
    },
    {
        'nom': 'Tartine Complète Avocat',
        'description': 'Pain complet grillé garni d\'avocat frais et tomate',
        'calorie': 320,
        'proteine': 14,
        'glucides': 38,
        'lipides': 14,
        'fibres': 10,
        'prix': 6.50
    },
    {
        'nom': 'Poisson Blanc aux Herbes',
        'description': 'Filet de poisson blanc délicat cuit aux herbes fraîches',
        'calorie': 260,
        'proteine': 42,
        'glucides': 2,
        'lipides': 8,
        'fibres': 1,
        'prix': 12.50
    },
    {
        'nom': 'Omelette aux Fromage',
        'description': 'Omelette baveuse garnie de fromage à pâte molle',
        'calorie': 340,
        'proteine': 28,
        'glucides': 4,
        'lipides': 26,
        'fibres': 0,
        'prix': 7.99
    },
    {
        'nom': 'Betteraves Rôties',
        'description': 'Betteraves rôties au four avec graines de courge',
        'calorie': 200,
        'proteine': 10,
        'glucides': 32,
        'lipides': 6,
        'fibres': 10,
        'prix': 5.50
    },
    {
        'nom': 'Filet de Porc Grillé',
        'description': 'Filet de porc maigre grillé avec moutarde ancienne',
        'calorie': 360,
        'proteine': 50,
        'glucides': 2,
        'lipides': 16,
        'fibres': 0,
        'prix': 13.50
    },
    {
        'nom': 'Carotte Râpée Vinaigrette',
        'description': 'Carottes crues râpées avec vinaigrette légère',
        'calorie': 100,
        'proteine': 2,
        'glucides': 18,
        'lipides': 2,
        'fibres': 6,
        'prix': 3.50
    },
    {
        'nom': 'Aubergine Grillée',
        'description': 'Tranches d\'aubergine grillées à la perfection avec herbes',
        'calorie': 120,
        'proteine': 4,
        'glucides': 18,
        'lipides': 3,
        'fibres': 6,
        'prix': 4.50
    },
    {
        'nom': 'Œufs Pochés Épinards',
        'description': 'Œufs pochés sur lit d\'épinards frais avec sauce béchamel légère',
        'calorie': 310,
        'proteine': 16,
        'glucides': 10,
        'lipides': 22,
        'fibres': 2,
        'prix': 8.50
    },
    {
        'nom': 'Lentilles Vertes Salée',
        'description': 'Lentilles vertes cuites nature avec condiments légers',
        'calorie': 320,
        'proteine': 18,
        'glucides': 46,
        'lipides': 2,
        'fibres': 10,
        'prix': 5.50
    },
    {
        'nom': 'Steak Tartare Frais',
        'description': 'Steak tartare préparé à la minute avec herbes et câpres',
        'calorie': 300,
        'proteine': 48,
        'glucides': 0,
        'lipides': 14,
        'fibres': 0,
        'prix': 16.99
    },
    {
        'nom': 'Pamplemousse Rose',
        'description': 'Demi pamplemousse rose sucré et juteux du matin',
        'calorie': 90,
        'proteine': 1,
        'glucides': 20,
        'lipides': 0,
        'fibres': 3,
        'prix': 2.50
    },
    {
        'nom': 'Pâtes Complètes Carbonara',
        'description': 'Pâtes complètes avec lardons, œuf et parmesan râpé',
        'calorie': 440,
        'proteine': 18,
        'glucides': 60,
        'lipides': 16,
        'fibres': 6,
        'prix': 9.99
    },
    {
        'nom': 'Thon en Conserve Nature',
        'description': 'Thon blanc en conserve dans l\'eau sans sel ajouté',
        'calorie': 200,
        'proteine': 38,
        'glucides': 0,
        'lipides': 5,
        'fibres': 0,
        'prix': 4.99
    },
    {
        'nom': 'Poitrine Poulet Rôtie',
        'description': 'Poitrine de poulet fermier rôtie aux herbes de Provence',
        'calorie': 320,
        'proteine': 42,
        'glucides': 0,
        'lipides': 16,
        'fibres': 0,
        'prix': 11.99
    },
    {
        'nom': 'Tomate Mozzarella',
        'description': 'Tomates frais accompagnées de mozzarella et basilic frais',
        'calorie': 260,
        'proteine': 14,
        'glucides': 6,
        'lipides': 18,
        'fibres': 1,
        'prix': 7.50
    },
    {
        'nom': 'Artichauts à la Vapeur',
        'description': 'Cœurs d\'artichauts cuits à la vapeur avec sauce citron',
        'calorie': 120,
        'proteine': 6,
        'glucides': 20,
        'lipides': 1,
        'fibres': 8,
        'prix': 6.50
    },
    {
        'nom': 'Andouille Grillée',
        'description': 'Andouille de Guémené grillée accompagnée de moutarde',
        'calorie': 360,
        'proteine': 20,
        'glucides': 0,
        'lipides': 30,
        'fibres': 0,
        'prix': 10.99
    },
    {
        'nom': 'Myrtilles Fraîches',
        'description': 'Myrtilles sauvages fraîches riches en antioxydants',
        'calorie': 100,
        'proteine': 1,
        'glucides': 20,
        'lipides': 0,
        'fibres': 3,
        'prix': 5.99
    },
    {
        'nom': 'Champignons de Paris Sautés',
        'description': 'Champignons frais sautés à l\'ail et persil',
        'calorie': 150,
        'proteine': 6,
        'glucides': 16,
        'lipides': 7,
        'fibres': 2,
        'prix': 4.99
    },
    {
        'nom': 'Crabe Frais',
        'description': 'Crabe frais décortiqué accompagné de citron et herbes',
        'calorie': 200,
        'proteine': 38,
        'glucides': 0,
        'lipides': 5,
        'fibres': 0,
        'prix': 18.99
    },
    {
        'nom': 'Épinards à la Crème',
        'description': 'Épinards frais préparés à la crème légère et muscade',
        'calorie': 220,
        'proteine': 10,
        'glucides': 10,
        'lipides': 14,
        'fibres': 4,
        'prix': 6.99
    },
    {
        'nom': 'Filet de Truite Fumée',
        'description': 'Filet de truite fumée à froid sur lit de citron',
        'calorie': 260,
        'proteine': 36,
        'glucides': 0,
        'lipides': 14,
        'fibres': 0,
        'prix': 14.99
    },
    {
        'nom': 'Muesli Complet Nature',
        'description': 'Muesli complet sans sucre avec noix et fruits secs',
        'calorie': 400,
        'proteine': 14,
        'glucides': 62,
        'lipides': 12,
        'fibres': 8,
        'prix': 5.99
    },
    {
        'nom': 'Navets Rôtis',
        'description': 'Navets rôtis au four avec thym frais',
        'calorie': 140,
        'proteine': 2,
        'glucides': 28,
        'lipides': 1,
        'fibres': 3,
        'prix': 3.99
    },
    {
        'nom': 'Blanc de Poulet Poêlé',
        'description': 'Blanc de poulet poêlé avec champignons et échalotes',
        'calorie': 300,
        'proteine': 42,
        'glucides': 4,
        'lipides': 12,
        'fibres': 1,
        'prix': 10.99
    },
    {
        'nom': 'Mangue Fraîche',
        'description': 'Mangue tropicale fraîche riche en vitamine C',
        'calorie': 120,
        'proteine': 1,
        'glucides': 28,
        'lipides': 0,
        'fibres': 2,
        'prix': 4.50
    },
    {
        'nom': 'Huître Nature',
        'description': 'Huîtres fraîches de Bretagne accompagnées de citron',
        'calorie': 90,
        'proteine': 12,
        'glucides': 4,
        'lipides': 2,
        'fibres': 0,
        'prix': 12.50
    },
    {
        'nom': 'Foie Gras Poêlé',
        'description': 'Foie gras poêlé avec réduction de raisin',
        'calorie': 480,
        'proteine': 20,
        'glucides': 6,
        'lipides': 40,
        'fibres': 0,
        'prix': 24.99
    },
    {
        'nom': 'Pois Cassés Écrasés',
        'description': 'Pois cassés cuits et écrasés avec échalotes',
        'calorie': 300,
        'proteine': 16,
        'glucides': 42,
        'lipides': 2,
        'fibres': 8,
        'prix': 4.99
    },
    {
        'nom': 'Ananas Frais Découpé',
        'description': 'Ananas frais découpé en morceaux succulents',
        'calorie': 120,
        'proteine': 1,
        'glucides': 26,
        'lipides': 0,
        'fibres': 2,
        'prix': 4.99
    },
    {
        'nom': 'Côte de Veau Rôtie',
        'description': 'Côte de veau fermier rôtie avec légumes de saison',
        'calorie': 400,
        'proteine': 46,
        'glucides': 2,
        'lipides': 22,
        'fibres': 0,
        'prix': 18.99
    },
    {
        'nom': 'Riz Noir Complet',
        'description': 'Riz noir sauvage cuit avec un bouillon de légumes',
        'calorie': 320,
        'proteine': 8,
        'glucides': 66,
        'lipides': 2,
        'fibres': 3,
        'prix': 7.99
    },
    {
        'nom': 'Fraise Fraîche',
        'description': 'Fraises fraîches de saison riches en vitamine C',
        'calorie': 100,
        'proteine': 1,
        'glucides': 20,
        'lipides': 0,
        'fibres': 2,
        'prix': 4.50
    },
    {
        'nom': 'Moelle Osseuse Rôtie',
        'description': 'Moelle osseuse de bœuf rôtie avec fleur de sel',
        'calorie': 420,
        'proteine': 24,
        'glucides': 0,
        'lipides': 36,
        'fibres': 0,
        'prix': 12.99
    },
    {
        'nom': 'Orge Perlé Cuit',
        'description': 'Orge perlé cuit accompagné de légumes racines',
        'calorie': 320,
        'proteine': 10,
        'glucides': 68,
        'lipides': 1,
        'fibres': 6,
        'prix': 5.50
    },
    {
        'nom': 'Noix Cerneaux',
        'description': 'Noix cerneaux crues riches en oméga-3',
        'calorie': 440,
        'proteine': 12,
        'glucides': 10,
        'lipides': 40,
        'fibres': 3,
        'prix': 8.99
    },
    {
        'nom': 'Pomme Granny Smith',
        'description': 'Pomme verte acidulée Granny Smith issue d\'agriculture locale',
        'calorie': 120,
        'proteine': 0,
        'glucides': 30,
        'lipides': 0,
        'fibres': 3,
        'prix': 2.50
    },
    {
        'nom': 'Osserine de Veau',
        'description': 'Osserine de veau braissée avec légumes racines',
        'calorie': 360,
        'proteine': 40,
        'glucides': 6,
        'lipides': 18,
        'fibres': 1,
        'prix': 16.50
    },
    {
        'nom': 'Sarrasin Nature',
        'description': 'Grains de sarrasin cuits sans gluten',
        'calorie': 340,
        'proteine': 14,
        'glucides': 60,
        'lipides': 3,
        'fibres': 5,
        'prix': 5.99
    },
    {
        'nom': 'Pêche Blanche Juteuse',
        'description': 'Pêche blanche fraîche très juteuse de saison',
        'calorie': 110,
        'proteine': 1,
        'glucides': 26,
        'lipides': 0,
        'fibres': 2,
        'prix': 3.50
    },
    {
        'nom': 'Ris de Veau Poêlé',
        'description': 'Ris de veau tendre poêlé avec sauce aux champignons',
        'calorie': 400,
        'proteine': 44,
        'glucides': 4,
        'lipides': 22,
        'fibres': 0,
        'prix': 22.99
    },
    {
        'nom': 'Riz Risotto Crémeux',
        'description': 'Risotto cuit avec bouillon de légumes et fromage râpé',
        'calorie': 380,
        'proteine': 12,
        'glucides': 56,
        'lipides': 12,
        'fibres': 1,
        'prix': 11.99
    },
    {
        'nom': 'Clémentine Douce',
        'description': 'Clémentine douce sans pépins d\'hiver',
        'calorie': 90,
        'proteine': 1,
        'glucides': 20,
        'lipides': 0,
        'fibres': 2,
        'prix': 2.00
    },
    {
        'nom': 'Bavette d\'Aloyau',
        'description': 'Bavette d\'aloyau poêlée avec échalotes caramélisées',
        'calorie': 360,
        'proteine': 44,
        'glucides': 2,
        'lipides': 20,
        'fibres': 0,
        'prix': 16.99
    },
    {
        'nom': 'Couscous Complet',
        'description': 'Couscous complet cuit avec légumes et pois chiches',
        'calorie': 360,
        'proteine': 14,
        'glucides': 60,
        'lipides': 6,
        'fibres': 8,
        'prix': 7.99
    },
    {
        'nom': 'Kiwi Vert Sucré',
        'description': 'Kiwis verts savoureux riches en vitamine C',
        'calorie': 110,
        'proteine': 1,
        'glucides': 26,
        'lipides': 0,
        'fibres': 2,
        'prix': 3.50
    },
    {
        'nom': 'Côtelette Agneau',
        'description': 'Côtelette d\'agneau fermier rôtie avec herbes',
        'calorie': 400,
        'proteine': 46,
        'glucides': 0,
        'lipides': 22,
        'fibres': 0,
        'prix': 19.99
    },
    {
        'nom': 'Porridge de Sarrasin',
        'description': 'Porridge de sarrasin avec lait et miel',
        'calorie': 320,
        'proteine': 10,
        'glucides': 50,
        'lipides': 8,
        'fibres': 5,
        'prix': 6.99
    },
    {
        'nom': 'Raisin Blanc Frais',
        'description': 'Raisins blancs frais et succulents',
        'calorie': 130,
        'proteine': 1,
        'glucides': 30,
        'lipides': 0,
        'fibres': 2,
        'prix': 4.50
    },
    {
        'nom': 'Gigot Agneau Rôti',
        'description': 'Gigot d\'agneau fermier rôti avec romarin',
        'calorie': 380,
        'proteine': 48,
        'glucides': 0,
        'lipides': 20,
        'fibres': 0,
        'prix': 22.99
    },
    {
        'nom': 'Millet Cuit Nature',
        'description': 'Millet cuit simplement nature sans additif',
        'calorie': 340,
        'proteine': 12,
        'glucides': 68,
        'lipides': 2,
        'fibres': 2,
        'prix': 5.99
    },
    {
        'nom': 'Prune Noire Fraîche',
        'description': 'Prunes noires fraîches de saison',
        'calorie': 110,
        'proteine': 1,
        'glucides': 26,
        'lipides': 0,
        'fibres': 2,
        'prix': 3.99
    },
    {
        'nom': 'Tête de Veau Vinaigrette',
        'description': 'Tête de veau cuite à la vinaigrette traditionnelle',
        'calorie': 260,
        'proteine': 40,
        'glucides': 0,
        'lipides': 12,
        'fibres': 0,
        'prix': 13.99
    },
    {
        'nom': 'Fonio Cuit',
        'description': 'Fonio céréale ancienne cuite simplement',
        'calorie': 320,
        'proteine': 10,
        'glucides': 64,
        'lipides': 2,
        'fibres': 3,
        'prix': 7.50
    },
    {
        'nom': 'Papaye Fraîche',
        'description': 'Papaye tropicale fraîche et douce',
        'calorie': 120,
        'proteine': 2,
        'glucides': 28,
        'lipides': 0,
        'fibres': 2,
        'prix': 5.50
    },
    {
        'nom': 'Rognons Agneau Grillés',
        'description': 'Rognons d\'agneau grillés avec moutarde',
        'calorie': 300,
        'proteine': 42,
        'glucides': 0,
        'lipides': 14,
        'fibres': 0,
        'prix': 14.99
    },
    {
        'nom': 'Couscous aux Sept Légumes',
        'description': 'Couscous traditionnel avec carottes, navets, courgettes, champignons',
        'calorie': 340,
        'proteine': 14,
        'glucides': 60,
        'lipides': 6,
        'fibres': 7,
        'prix': 9.50
    },
    {
        'nom': 'Brochettes de Crevettes',
        'description': 'Crevettes grillées à la broche avec poivrons et oignons rouges',
        'calorie': 240,
        'proteine': 30,
        'glucides': 6,
        'lipides': 10,
        'fibres': 1,
        'prix': 13.00
    },
    {
        'nom': 'Lentilles Corail au Curry',
        'description': 'Lentilles corail cuites avec épices curry et oignons caramélisés',
        'calorie': 300,
        'proteine': 20,
        'glucides': 40,
        'lipides': 4,
        'fibres': 8,
        'prix': 6.50
    },
    {
        'nom': 'Steak Frites Maison',
        'description': 'Steak grillé saignant avec frites croustillantes et roquette',
        'calorie': 460,
        'proteine': 36,
        'glucides': 38,
        'lipides': 22,
        'fibres': 2,
        'prix': 16.99
    },
    {
        'nom': 'Morue à la Provençale',
        'description': 'Morue cuite avec tomates, olives, ail et herbes provençales',
        'calorie': 280,
        'proteine': 36,
        'glucides': 6,
        'lipides': 10,
        'fibres': 2,
        'prix': 12.99
    },
    {
        'nom': 'Courgettes Farcies',
        'description': 'Courgettes évidées farcies avec riz, tomate et viande hachée',
        'calorie': 300,
        'proteine': 20,
        'glucides': 32,
        'lipides': 14,
        'fibres': 4,
        'prix': 9.99
    },
    {
        'nom': 'Poulet Tandoori',
        'description': 'Filet de poulet mariné aux épices tandoori et yaourt',
        'calorie': 320,
        'proteine': 42,
        'glucides': 4,
        'lipides': 14,
        'fibres': 0,
        'prix': 13.50
    },
    {
        'nom': 'Minestrone Végétal',
        'description': 'Soupe italienne généreuse avec pâtes, légumes et haricots',
        'calorie': 260,
        'proteine': 12,
        'glucides': 35,
        'lipides': 5,
        'fibres': 5,
        'prix': 6.99
    },
    {
        'nom': 'Filet Mignon Sauce Poivre',
        'description': 'Filet mignon tendre sauce au poivre frais et crème fraîche',
        'calorie': 420,
        'proteine': 42,
        'glucides': 4,
        'lipides': 28,
        'fibres': 0,
        'prix': 18.99
    },
    {
        'nom': 'Riz Jasmin aux Champignons',
        'description': 'Riz jasmin parfumé avec champignons de Paris et petits pois',
        'calorie': 290,
        'proteine': 10,
        'glucides': 54,
        'lipides': 4,
        'fibres': 3,
        'prix': 7.99
    },
    {
        'nom': 'Boulettes de Viande Sauce Tomate',
        'description': 'Boulettes maison à la viande hachée avec sauce tomate et herbes',
        'calorie': 350,
        'proteine': 28,
        'glucides': 18,
        'lipides': 20,
        'fibres': 2,
        'prix': 9.99
    },
    {
        'nom': 'Aubergine Parmigiana',
        'description': 'Aubergines fondantes en couches avec sauce tomate et mozzarella',
        'calorie': 310,
        'proteine': 18,
        'glucides': 22,
        'lipides': 20,
        'fibres': 5,
        'prix': 10.50
    },
    {
        'nom': 'Homard Thermidor',
        'description': 'Homard cuit à la vapeur avec sauce béchamel et fromage gratinée',
        'calorie': 380,
        'proteine': 44,
        'glucides': 8,
        'lipides': 20,
        'fibres': 1,
        'prix': 24.99
    },
    {
        'nom': 'Tofu Sauté Aigre-Sucré',
        'description': 'Tofu frit sauté avec sauce aigre-sucre, ananas et légumes',
        'calorie': 280,
        'proteine': 20,
        'glucides': 28,
        'lipides': 12,
        'fibres': 4,
        'prix': 8.50
    },
    {
        'nom': 'Risotto aux Champignons',
        'description': 'Risotto crémeux aux champignons de Paris, parmesan et blanc de poireau',
        'calorie': 360,
        'proteine': 14,
        'glucides': 52,
        'lipides': 14,
        'fibres': 2,
        'prix': 11.99
    },
    {
        'nom': 'Lapin à la Moutarde',
        'description': 'Lapin fermier à la moutarde de Dijon avec crème fraîche',
        'calorie': 340,
        'proteine': 42,
        'glucides': 3,
        'lipides': 18,
        'fibres': 0,
        'prix': 15.99
    },
    {
        'nom': 'Soupe à l\'Oignon Gratinée',
        'description': 'Soupe onctueuse d\'oignons caramélisés avec pain et fromage gratinée',
        'calorie': 240,
        'proteine': 12,
        'glucides': 25,
        'lipides': 12,
        'fibres': 3,
        'prix': 8.00
    },
    {
        'nom': 'Ratatouille Niçoise',
        'description': 'Ratatouille traditionnelle avec tomate, aubergine, courgette et poivron',
        'calorie': 220,
        'proteine': 8,
        'glucides': 24,
        'lipides': 12,
        'fibres': 6,
        'prix': 7.50
    },
    {
        'nom': 'Côte de Veau Panée',
        'description': 'Côte de veau épaisse panée à la chapelure et frite à l\'huile d\'olive',
        'calorie': 420,
        'proteine': 44,
        'glucides': 12,
        'lipides': 22,
        'fibres': 1,
        'prix': 17.50
    },
    {
        'nom': 'Ravioles aux Épinards',
        'description': 'Ravioles fraîches farcies d\'épinards et ricotta, sauce béchamel',
        'calorie': 350,
        'proteine': 16,
        'glucides': 48,
        'lipides': 14,
        'fibres': 4,
        'prix': 10.99
    },
    {
        'nom': 'Bouillabaisse Provençale',
        'description': 'Soupe de poisson méditerranéenne avec rouille et croûtons',
        'calorie': 280,
        'proteine': 32,
        'glucides': 12,
        'lipides': 12,
        'fibres': 3,
        'prix': 14.99
    },
    {
        'nom': 'Chou Farci Alsacien',
        'description': 'Chou blanchi farci de viande hachée et riz, cuit à la braise',
        'calorie': 300,
        'proteine': 24,
        'glucides': 24,
        'lipides': 14,
        'fibres': 4,
        'prix': 8.99
    },
    {
        'nom': 'Daurade Royale en Croûte de Sel',
        'description': 'Daurade entière cuite en croûte de sel, citron et herbes',
        'calorie': 320,
        'proteine': 40,
        'glucides': 0,
        'lipides': 18,
        'fibres': 0,
        'prix': 18.50
    },
    {
        'nom': 'Cassoulet Français',
        'description': 'Cassoulet traditionnel avec haricots, viande et saucisse fumée',
        'calorie': 480,
        'proteine': 32,
        'glucides': 42,
        'lipides': 24,
        'fibres': 8,
        'prix': 12.99
    },
]

print(f"Génération de {len(plats_data)} plats...")
print("=" * 80)

with transaction.atomic():
    created_count = 0
    plat_objects = {}  # Stocker les objets Plat créés pour les menus
    
    for plat_info in plats_data:
        try:
            plat, created = Plat.objects.get_or_create(
                nom=plat_info['nom'],
                defaults={
                    'description': plat_info['description'],
                    'calorie': plat_info['calorie'],
                    'proteine': plat_info['proteine'],
                    'glucides': plat_info['glucides'],
                    'lipides': plat_info['lipides'],
                    'fibres': plat_info['fibres'],
                    'prix': plat_info['prix'],
                    'est_disponible': True
                }
            )
            if created:
                created_count += 1
                print(f"✓ Créé: {plat.nom} ({plat.calorie:.0f} kcal, {plat.proteine:.1f}g prot, {plat.prix}€)")
            plat_objects[plat.nom] = plat
        except Exception as e:
            print(f"✗ Erreur pour {plat_info['nom']}: {str(e)}")

print("=" * 80)
print(f"✅ Génération plats terminée! {created_count} nouveaux plats créés.")
print(f"Total de plats dans la base de données: {Plat.objects.count()}")

# =============================================================================
# GÉNÉRER LES MENUS THÉMATIQUES
# =============================================================================
print("\n" + "=" * 80)
print("GÉNÉRATION DES MENUS THÉMATIQUES")
print("=" * 80 + "\n")

# Définir les dates (semaine courante)
aujourd_hui = datetime.now().date()
date_debut = aujourd_hui
date_fin = aujourd_hui + timedelta(days=6)

menus_config = {
    "Petit Déjeuner Protéiné": {
        "description": "Petit déjeuner riche en protéines pour bien démarrer la journée",
        "plats": [
            "Œufs à la Coque et Épinards",
            "Œufs Brouillés aux Champignons",
            "Yaourt Grec Nature",
        ]
    },
    "Déjeuner Équilibré": {
        "description": "Déjeuner équilibré avec protéines, glucides et légumes",
        "plats": [
            "Poulet Grillé aux Herbes",
            "Riz Complet aux Légumes",
            "Salade Méditerranéenne",
            "Haricots Verts Sautés",
        ]
    },
    "Dîner Léger": {
        "description": "Dîner faible en calories pour une meilleure digestion",
        "plats": [
            "Cabillaud Vapeur",
            "Betteraves Rôties",
            "Carotte Râpée Vinaigrette",
        ]
    },
    "Menu Fitness": {
        "description": "Menu haute performance: protéines élevées, faibles lipides",
        "plats": [
            "Steak Maigre Poêlé",
            "Poitrine de Dinde Rôtie",
            "Blanc de Poulet Poêlé",
            "Riz Basmati Blanc",
            "Lentilles Vertes Salée",
        ]
    },
    "Menu Végétarien": {
        "description": "Menu complet sans viande ni poisson",
        "plats": [
            "Tofu Mariné aux Épices",
            "Lentilles Corail au Curcuma",
            "Quinoa aux Brocoli",
            "Tomate Mozzarella",
            "Chou-fleur Rôti",
        ]
    },
    "Menu Gastronomique": {
        "description": "Menu raffiné avec saveurs méditerranéennes",
        "plats": [
            "Saumon Poêlé",
            "Morue à la Méditerranéenne",
            "Truite Arc-en-ciel",
            "Crevettes Sautées à l'Ail",
            "Riz Risotto Crémeux",
        ]
    },
}

menu_created_count = 0
with transaction.atomic():
    for menu_nom, config in menus_config.items():
        try:
            # Créer ou récupérer le menu
            menu, created = Menu.objects.get_or_create(
                nom=menu_nom,
                defaults={
                    'description': config['description'],
                    'date_debut': date_debut,
                    'date_fin': date_fin,
                    'est_actif': True
                }
            )
            
            if created:
                menu_created_count += 1
                print(f"\n✓ Menu créé: {menu_nom}")
            else:
                print(f"\n⚠ Menu existant: {menu_nom} (maj des plats)")
                # Supprimer les anciens plats du menu
                menu.plats.clear()
            
            # Ajouter les plats au menu
            plats_ajoutes = 0
            for plat_nom in config['plats']:
                if plat_nom in plat_objects:
                    menu.ajouter_plat(plat_objects[plat_nom])
                    plats_ajoutes += 1
                    print(f"  └─ ✓ Ajouté: {plat_nom}")
                else:
                    print(f"  └─ ⚠ Non trouvé: {plat_nom}")
            
            # Afficher les nutritions totales
            nutrition = menu.calculer_valeur_nutritionnelle_totale()
            print(f"  📊 Nutritions totales:")
            print(f"     • Calories: {nutrition['calories']:.0f} kcal")
            print(f"     • Protéines: {nutrition['proteines']:.1f}g")
            print(f"     • Glucides: {nutrition['glucides']:.1f}g")
            print(f"     • Lipides: {nutrition['lipides']:.1f}g")
            print(f"     • Fibres: {nutrition['fibres']:.1f}g")
            print(f"     • Prix total: {nutrition['prix']:.2f}€")
            
        except Exception as e:
            print(f"\n✗ Erreur création menu {menu_nom}: {str(e)}")

print("\n" + "=" * 80)
print(f"✅ Génération menus terminée! {menu_created_count} nouveaux menus créés.")
print(f"Total de menus dans la base de données: {Menu.objects.count()}")
print("=" * 80 + "\n")
print("🎉 GÉNÉRATION COMPLÈTE!")
print(f"   • Plats: {Plat.objects.count()}")
print(f"   • Menus: {Menu.objects.count()}")
print("=" * 80)
