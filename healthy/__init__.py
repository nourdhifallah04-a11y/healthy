"""
Script pour insérer les données initiales
Exécuter avec: python manage.py runscript migration.001_initial_data
"""
from django.core.management.base import BaseCommand

def run():
    print("Insertion des données initiales...")
    
    # Créer un système IA
    ia, created = SystemeIA.objects.get_or_create(
        nom="Nutrition AI",
        defaults={
            'version': "1.0.0",
            'est_actif': True
        }
    )
    
    if created:
        print("Système IA créé avec succès")
    
    # Créer des plats de base
    plats_data = [
        {
            'nom': 'Salade César',
            'description': 'Salade verte avec poulet grillé, parmesan et sauce césar',
            'calorie': 450,
            'proteine': 25,
            'glucides': 15,
            'lipides': 30,
            'fibres': 5,
            'prix': 12.99
        },
        {
            'nom': 'Bowl Protéiné',
            'description': 'Riz complet, poulet, avocat, légumes variés',
            'calorie': 650,
            'proteine': 40,
            'glucides': 60,
            'lipides': 25,
            'fibres': 8,
            'prix': 15.99
        },
        {
            'nom': 'Smoothie Énergie',
            'description': 'Banane, protéine de pois, lait d\'amande, beurre de cacahuète',
            'calorie': 350,
            'proteine': 20,
            'glucides': 40,
            'lipides': 12,
            'fibres': 6,
            'prix': 8.99
        },
        {
            'nom': 'Omelette Protéinée',
            'description': 'Omelette aux 3 œufs avec légumes et fromage léger',
            'calorie': 380,
            'proteine': 30,
            'glucides': 5,
            'lipides': 25,
            'fibres': 2,
            'prix': 10.99
        },
        {
            'nom': 'Poke Bowl Saumon',
            'description': 'Saumon frais, riz, avocat, concombre, graines de sésame',
            'calorie': 580,
            'proteine': 35,
            'glucides': 55,
            'lipides': 22,
            'fibres': 7,
            'prix': 18.99
        }
    ]
    
    for plat_data in plats_data:
        plat, created = Plat.objects.get_or_create(
            nom=plat_data['nom'],
            defaults=plat_data
        )
        if created:
            print(f"Plat créé: {plat.nom}")
    
    # Créer des menus
    menus_data = [
        {
            'nom': 'Menu Perte de Poids',
            'description': 'Repas équilibrés pour une perte de poids saine',
            'date_debut': '2024-01-01',
            'date_fin': '2024-12-31',
            'est_actif': True,
            'plats': ['Salade César', 'Smoothie Énergie']
        },
        {
            'nom': 'Menu Prise de Muscle',
            'description': 'Repas riches en protéines pour la construction musculaire',
            'date_debut': '2024-01-01',
            'date_fin': '2024-12-31',
            'est_actif': True,
            'plats': ['Bowl Protéiné', 'Omelette Protéinée', 'Smoothie Énergie']
        },
        {
            'nom': 'Menu Performance',
            'description': 'Repas énergétiques pour les sportifs',
            'date_debut': '2024-01-01',
            'date_fin': '2024-12-31',
            'est_actif': True,
            'plats': ['Poke Bowl Saumon', 'Smoothie Énergie']
        }
    ]
    
    for menu_data in menus_data:
        plats_noms = menu_data.pop('plats')
        menu, created = Menu.objects.get_or_create(
            nom=menu_data['nom'],
            defaults=menu_data
        )
        if created:
            for plat_nom in plats_noms:
                plat = Plat.objects.get(nom=plat_nom)
                menu.ajouter_plat(plat)
            print(f"Menu créé: {menu.nom}")
    
    print("Insertion des données terminée avec succès!")