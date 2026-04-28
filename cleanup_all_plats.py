#!/usr/bin/env python
import os
import sys
import django

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
django.setup()

from myapp.plat.models import Plat

# Supprimer tous les plats existants
deleted_count = Plat.objects.all().delete()[0]
print(f"✅ {deleted_count} plats supprimés")

# Vérifier qu'il n'y a plus de plats
count = Plat.objects.count()
print(f"Plats restants : {count}")
