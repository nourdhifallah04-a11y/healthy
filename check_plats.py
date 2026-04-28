#!/usr/bin/env python
import os
import sys
import django

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.plat.models import Plat

plats = Plat.objects.all()[:5]
for plat in plats:
    print(f"Plat: {plat.nom}")
    print(f"  Calories: {plat.calorie}")
    print(f"  Protéines: {plat.proteine}")
    print(f"  Glucides: {plat.glucides}")
    print(f"  Lipides: {plat.lipides}")
    print(f"  Fibres: {plat.fibres}")
    print()
