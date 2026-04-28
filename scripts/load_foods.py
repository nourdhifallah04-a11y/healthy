#!/usr/bin/env python
"""
Script pour charger des aliments de test
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from apps.nutrition.models import Food

def load_foods():
    """Charger les aliments de base"""
    foods_data = [
        {'name': 'Pomme', 'calories': 52, 'proteins': 0.3, 'carbs': 13.8, 'fats': 0.2},
        {'name': 'Banane', 'calories': 89, 'proteins': 1.1, 'carbs': 23, 'fats': 0.3},
        {'name': 'Chicken Breast', 'calories': 165, 'proteins': 31, 'carbs': 0, 'fats': 3.6},
        {'name': 'Riz blanc', 'calories': 130, 'proteins': 2.7, 'carbs': 28, 'fats': 0.3},
        {'name': 'Œuf', 'calories': 155, 'proteins': 13, 'carbs': 1.1, 'fats': 11},
    ]
    
    for food_data in foods_data:
        food, created = Food.objects.get_or_create(
            name=food_data['name'],
            defaults=food_data
        )
        if created:
            print(f"✅ Created: {food.name}")
        else:
            print(f"⏭️  Already exists: {food.name}")

if __name__ == '__main__':
    load_foods()
