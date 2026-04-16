import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.models import Plat
from django.db import transaction

# Données pour générer les plats
plats_data = [
    {
        'nom': 'Salade Méditerranéenne',
        'description': 'Salade fraîche avec tomates, concombre, olives noires et fromage feta',
        'calorie': 250,
        'proteine': 12,
        'glucides': 15,
        'lipides': 18,
        'fibres': 8,
        'prix': 8.50
    },
    {
        'nom': 'Poulet Grillé aux Herbes',
        'description': 'Filet de poulet grillé avec herbes fraîches et légumes de saison',
        'calorie': 350,
        'proteine': 45,
        'glucides': 5,
        'lipides': 15,
        'fibres': 3,
        'prix': 12.00
    },
    {
        'nom': 'Riz Complet aux Légumes',
        'description': 'Riz complet cuit avec brocoli, carottes et pois chiches',
        'calorie': 320,
        'proteine': 14,
        'glucides': 52,
        'lipides': 8,
        'fibres': 12,
        'prix': 7.50
    },
    {
        'nom': 'Saumon Poêlé',
        'description': 'Filet de saumon frais poêlé avec citron et herbes aromatiques',
        'calorie': 380,
        'proteine': 42,
        'glucides': 2,
        'lipides': 22,
        'fibres': 2,
        'prix': 14.99
    },
    {
        'nom': 'Pâtes Complètes à la Tomate',
        'description': 'Pâtes complètes avec sauce tomate maison et basilic frais',
        'calorie': 380,
        'proteine': 16,
        'glucides': 65,
        'lipides': 6,
        'fibres': 10,
        'prix': 8.00
    },
    {
        'nom': 'Poitrine de Dinde Rôtie',
        'description': 'Poitrine de dinde rôtie avec moutarde de Dijon et légumes racines',
        'calorie': 310,
        'proteine': 48,
        'glucides': 10,
        'lipides': 8,
        'fibres': 4,
        'prix': 11.50
    },
    {
        'nom': 'Quinoa aux Brocoli',
        'description': 'Quinoa protéiné mélangé avec brocoli et graines de tournesol',
        'calorie': 340,
        'proteine': 15,
        'glucides': 48,
        'lipides': 12,
        'fibres': 11,
        'prix': 9.99
    },
    {
        'nom': 'Truite Arc-en-ciel',
        'description': 'Truite fraîche cuite en papillote avec fenouil et citron',
        'calorie': 300,
        'proteine': 38,
        'glucides': 1,
        'lipides': 16,
        'fibres': 1,
        'prix': 13.50
    },
    {
        'nom': 'Pois Chiches Rôtis',
        'description': 'Pois chiches croustillants rôtis avec épices méditerranéennes',
        'calorie': 280,
        'proteine': 14,
        'glucides': 35,
        'lipides': 8,
        'fibres': 10,
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
        'calorie': 290,
        'proteine': 18,
        'glucides': 12,
        'lipides': 20,
        'fibres': 4,
        'prix': 8.50
    },
    {
        'nom': 'Lentilles Vertes Salée',
        'description': 'Lentilles vertes cuites nature avec condiments légers',
        'calorie': 300,
        'proteine': 16,
        'glucides': 48,
        'lipides': 3,
        'fibres': 14,
        'prix': 5.50
    },
    {
        'nom': 'Steak Tartare Frais',
        'description': 'Steak tartare préparé à la minute avec herbes et câpres',
        'calorie': 320,
        'proteine': 52,
        'glucides': 2,
        'lipides': 12,
        'fibres': 0,
        'prix': 16.99
    },
    {
        'nom': 'Pamplemousse Rose',
        'description': 'Demi pamplemousse rose sucré et juteux du matin',
        'calorie': 85,
        'proteine': 1,
        'glucides': 21,
        'lipides': 0,
        'fibres': 5,
        'prix': 2.50
    },
    {
        'nom': 'Pâtes Complètes Carbonara',
        'description': 'Pâtes complètes avec lardons, œuf et parmesan râpé',
        'calorie': 420,
        'proteine': 20,
        'glucides': 62,
        'lipides': 14,
        'fibres': 8,
        'prix': 9.99
    },
    {
        'nom': 'Thon en Conserve Nature',
        'description': 'Thon blanc en conserve dans l\'eau sans sel ajouté',
        'calorie': 210,
        'proteine': 42,
        'glucides': 0,
        'lipides': 4,
        'fibres': 0,
        'prix': 4.99
    },
    {
        'nom': 'Poitrine Poulet Rôtie',
        'description': 'Poitrine de poulet fermier rôtie aux herbes de Provence',
        'calorie': 340,
        'proteine': 48,
        'glucides': 0,
        'lipides': 16,
        'fibres': 0,
        'prix': 11.99
    },
    {
        'nom': 'Tomate Mozzarella',
        'description': 'Tomates frais accompagnées de mozzarella et basil frais',
        'calorie': 240,
        'proteine': 16,
        'glucides': 8,
        'lipides': 16,
        'fibres': 2,
        'prix': 7.50
    },
    {
        'nom': 'Artichauts à la Vapeur',
        'description': 'Cœurs d\'artichauts cuits à la vapeur avec sauce citron',
        'calorie': 110,
        'proteine': 8,
        'glucides': 18,
        'lipides': 1,
        'fibres': 12,
        'prix': 6.50
    },
    {
        'nom': 'Andouille Grillée',
        'description': 'Andouille de Guémené grillée accompagnée de moutarde',
        'calorie': 380,
        'proteine': 24,
        'glucides': 2,
        'lipides': 30,
        'fibres': 0,
        'prix': 10.99
    },
    {
        'nom': 'Myrtilles Fraîches',
        'description': 'Myrtilles sauvages fraîches riches en antioxydants',
        'calorie': 95,
        'proteine': 1,
        'glucides': 22,
        'lipides': 0,
        'fibres': 4,
        'prix': 5.99
    },
    {
        'nom': 'Champignons de Paris Sautés',
        'description': 'Champignons frais sautés à l\'ail et persil',
        'calorie': 140,
        'proteine': 8,
        'glucides': 14,
        'lipides': 6,
        'fibres': 4,
        'prix': 4.99
    },
    {
        'nom': 'Crabe Frais',
        'description': 'Crabe frais décortiqué accompagné de citron et herbes',
        'calorie': 220,
        'proteine': 42,
        'glucides': 0,
        'lipides': 4,
        'fibres': 0,
        'prix': 18.99
    },
    {
        'nom': 'Épinards à la Crème',
        'description': 'Épinards frais préparés à la crème légère et muscade',
        'calorie': 200,
        'proteine': 12,
        'glucides': 12,
        'lipides': 12,
        'fibres': 6,
        'prix': 6.99
    },
    {
        'nom': 'Filet de Truite Fumée',
        'description': 'Filet de truite fumée à froid sur lit de citron',
        'calorie': 280,
        'proteine': 40,
        'glucides': 1,
        'lipides': 14,
        'fibres': 0,
        'prix': 14.99
    },
    {
        'nom': 'Muesli Complet Nature',
        'description': 'Muesli complet sans sucre avec noix et fruits secs',
        'calorie': 380,
        'proteine': 12,
        'glucides': 65,
        'lipides': 8,
        'fibres': 10,
        'prix': 5.99
    },
    {
        'nom': 'Navets Rôtis',
        'description': 'Navets rôtis au four avec thym frais',
        'calorie': 120,
        'proteine': 4,
        'glucides': 22,
        'lipides': 1,
        'fibres': 4,
        'prix': 3.99
    },
    {
        'nom': 'Blanc de Poulet Poêlé',
        'description': 'Blanc de poulet poêlé avec champignons et échalotes',
        'calorie': 330,
        'proteine': 46,
        'glucides': 6,
        'lipides': 14,
        'fibres': 2,
        'prix': 10.99
    },
    {
        'nom': 'Mangue Fraîche',
        'description': 'Mangue tropicale fraîche riche en vitamine C',
        'calorie': 130,
        'proteine': 1,
        'glucides': 32,
        'lipides': 0,
        'fibres': 3,
        'prix': 4.50
    },
    {
        'nom': 'Huître Nature',
        'description': 'Huîtres fraîches de Bretagne accompagnées de citron',
        'calorie': 80,
        'proteine': 14,
        'glucides': 6,
        'lipides': 1,
        'fibres': 0,
        'prix': 12.50
    },
    {
        'nom': 'Foie Gras Poêlé',
        'description': 'Foie gras poêlé avec réduction de raisin',
        'calorie': 520,
        'proteine': 24,
        'glucides': 8,
        'lipides': 44,
        'fibres': 0,
        'prix': 24.99
    },
    {
        'nom': 'Pois Cassés Écrasés',
        'description': 'Pois cassés cuits et écrasés avec échalotes',
        'calorie': 280,
        'proteine': 14,
        'glucides': 45,
        'lipides': 2,
        'fibres': 10,
        'prix': 4.99
    },
    {
        'nom': 'Ananas Frais Découpé',
        'description': 'Ananas frais découpé en morceaux succulents',
        'calorie': 110,
        'proteine': 1,
        'glucides': 28,
        'lipides': 0,
        'fibres': 2,
        'prix': 4.99
    },
    {
        'nom': 'Côte de Veau Rôtie',
        'description': 'Côte de veau fermier rôtie avec légumes de saison',
        'calorie': 440,
        'proteine': 52,
        'glucides': 4,
        'lipides': 24,
        'fibres': 1,
        'prix': 18.99
    },
    {
        'nom': 'Riz Noir Complet',
        'description': 'Riz noir sauvage cuit avec un bouillon de légumes',
        'calorie': 310,
        'proteine': 10,
        'glucides': 60,
        'lipides': 3,
        'fibres': 4,
        'prix': 7.99
    },
    {
        'nom': 'Fraise Fraîche',
        'description': 'Fraises fraîches de saison riches en vitamine C',
        'calorie': 90,
        'proteine': 1,
        'glucides': 20,
        'lipides': 0,
        'fibres': 3,
        'prix': 4.50
    },
    {
        'nom': 'Moelle Osseuse Rôtie',
        'description': 'Moelle osseuse de bœuf rôtie avec fleur de sel',
        'calorie': 480,
        'proteine': 28,
        'glucides': 0,
        'lipides': 40,
        'fibres': 0,
        'prix': 12.99
    },
    {
        'nom': 'Orge Perlé Cuit',
        'description': 'Orge perlé cuit accompagné de légumes racines',
        'calorie': 300,
        'proteine': 12,
        'glucides': 62,
        'lipides': 2,
        'fibres': 8,
        'prix': 5.50
    },
    {
        'nom': 'Noix Cerneaux',
        'description': 'Noix cerneaux crues riches en oméga-3',
        'calorie': 420,
        'proteine': 10,
        'glucides': 12,
        'lipides': 38,
        'fibres': 4,
        'prix': 8.99
    },
    {
        'nom': 'Pomme Granny Smith',
        'description': 'Pomme verte acidulée Granny Smith issue d\'agriculture locale',
        'calorie': 110,
        'proteine': 0,
        'glucides': 28,
        'lipides': 0,
        'fibres': 5,
        'prix': 2.50
    },
    {
        'nom': 'Oestrine de Veau',
        'description': 'Oenoplie de veau braissée avec légumes racines',
        'calorie': 380,
        'proteine': 44,
        'glucides': 8,
        'lipides': 18,
        'fibres': 2,
        'prix': 16.50
    },
    {
        'nom': 'Sarrasin Nature',
        'description': 'Grains de sarrasin cuits sans gluten',
        'calorie': 320,
        'proteine': 12,
        'glucides': 62,
        'lipides': 3,
        'fibres': 6,
        'prix': 5.99
    },
    {
        'nom': 'Pêche Blanche Juteuse',
        'description': 'Pêche blanche fraîche très juteuse de saison',
        'calorie': 100,
        'proteine': 1,
        'glucides': 24,
        'lipides': 0,
        'fibres': 2,
        'prix': 3.50
    },
    {
        'nom': 'Ris de Veau Poêlé',
        'description': 'Ris de veau tendre poêlé avec sauce aux champignons',
        'calorie': 420,
        'proteine': 48,
        'glucides': 6,
        'lipides': 22,
        'fibres': 1,
        'prix': 22.99
    },
    {
        'nom': 'Riz Risotto Crémeux',
        'description': 'Risotto cuit avec bouillon de légumes et fromage râpé',
        'calorie': 380,
        'proteine': 14,
        'glucides': 58,
        'lipides': 10,
        'fibres': 2,
        'prix': 11.99
    },
    {
        'nom': 'Clémentine Douce',
        'description': 'Clémentine douce sans pépins d\'hiver',
        'calorie': 80,
        'proteine': 1,
        'glucides': 19,
        'lipides': 0,
        'fibres': 2,
        'prix': 2.00
    },
    {
        'nom': 'Bavette d\'Aloyau',
        'description': 'Bavette d\'aloyau poêlée avec échalotes caramélisées',
        'calorie': 380,
        'proteine': 48,
        'glucides': 4,
        'lipides': 20,
        'fibres': 0,
        'prix': 16.99
    },
    {
        'nom': 'Couscous Complet',
        'description': 'Couscous complet cuit avec légumes et pois chiches',
        'calorie': 340,
        'proteine': 16,
        'glucides': 58,
        'lipides': 6,
        'fibres': 10,
        'prix': 7.99
    },
    {
        'nom': 'Kiwi Vert Sucré',
        'description': 'Kiwis verts savoureux riches en vitamine C',
        'calorie': 100,
        'proteine': 1,
        'glucides': 24,
        'lipides': 0,
        'fibres': 3,
        'prix': 3.50
    },
    {
        'nom': 'Côtelette Agneau',
        'description': 'Côtelette d\'agneau fermier rôtie avec herbes',
        'calorie': 420,
        'proteine': 50,
        'glucides': 0,
        'lipides': 24,
        'fibres': 0,
        'prix': 19.99
    },
    {
        'nom': 'Buckwheat Porridge',
        'description': 'Porridge de sarrasin avec lait et miel',
        'calorie': 300,
        'proteine': 12,
        'glucides': 52,
        'lipides': 6,
        'fibres': 6,
        'prix': 6.99
    },
    {
        'nom': 'Raisin Blanc Frais',
        'description': 'Raisins blancs frais et succulents',
        'calorie': 120,
        'proteine': 1,
        'glucides': 28,
        'lipides': 0,
        'fibres': 2,
        'prix': 4.50
    },
    {
        'nom': 'Gigot Agneau Rôti',
        'description': 'Gigot d\'agneau fermier rôti avec romarin',
        'calorie': 400,
        'proteine': 52,
        'glucides': 0,
        'lipides': 20,
        'fibres': 0,
        'prix': 22.99
    },
    {
        'nom': 'Millet Cuit Nature',
        'description': 'Millet cuit simplement nature sans additif',
        'calorie': 320,
        'proteine': 10,
        'glucides': 65,
        'lipides': 3,
        'fibres': 2,
        'prix': 5.99
    },
    {
        'nom': 'Prune Noire Fraîche',
        'description': 'Prunes noires fraîches de saison',
        'calorie': 100,
        'proteine': 1,
        'glucides': 24,
        'lipides': 0,
        'fibres': 2,
        'prix': 3.99
    },
    {
        'nom': 'Tête de Veau Vinaigrette',
        'description': 'Tête de veau cuite à la vinaigrette traditionnelle',
        'calorie': 280,
        'proteine': 42,
        'glucides': 2,
        'lipides': 12,
        'fibres': 0,
        'prix': 13.99
    },
    {
        'nom': 'Fonio Cuit',
        'description': 'Fonio céréale ancienne cuite simplement',
        'calorie': 310,
        'proteine': 8,
        'glucides': 62,
        'lipides': 2,
        'fibres': 4,
        'prix': 7.50
    },
    {
        'nom': 'Papaye Fraîche',
        'description': 'Papaye tropicale fraîche et douce',
        'calorie': 110,
        'proteine': 2,
        'glucides': 26,
        'lipides': 0,
        'fibres': 2,
        'prix': 5.50
    },
    {
        'nom': 'Rognons Agneau Grillés',
        'description': 'Rognons d\'agneau grillés avec moutarde',
        'calorie': 320,
        'proteine': 48,
        'glucides': 0,
        'lipides': 14,
        'fibres': 0,
        'prix': 14.99
    },
]

# Générer des plats supplémentaires pour atteindre 100
additional_plats = [
    {
        'nom': f'Plat Savoureux #{i}',
        'description': f'Plat délicieux composé d\'ingrédients frais et de qualité supérieure',
        'calorie': 250 + (i * 5) % 300,
        'proteine': 15 + (i * 3) % 40,
        'glucides': 35 + (i * 4) % 40,
        'lipides': 8 + (i * 2) % 20,
        'fibres': 4 + (i % 12),
        'prix': 5.99 + (i * 0.1) % 10.0
    }
    for i in range(100 - len(plats_data))
]

plats_data.extend(additional_plats)

print(f"Génération de {len(plats_data)} plats...")
print("=" * 80)

with transaction.atomic():
    created_count = 0
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
        except Exception as e:
            print(f"✗ Erreur pour {plat_info['nom']}: {str(e)}")

print("=" * 80)
print(f"✅ Génération terminée! {created_count} nouveaux plats créés.")
print(f"Total de plats dans la base de données: {Plat.objects.count()}")
