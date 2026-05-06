#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic script for POST /commande/api/ligne-commandes/ 404 error
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.conf import settings
from django.urls import get_resolver
from rest_framework.routers import DefaultRouter

print("\n" + "="*70)
print("DIAGNOSTIC: POST /commande/api/ligne-commandes/ 404 Error")
print("="*70)

print("\n1️⃣  SERVER CONFIGURATION:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

print("\n2️⃣  INSTALLED APPS (REST Framework):")
for app in settings.INSTALLED_APPS:
    if 'rest' in app.lower():
        print(f"   ✓ {app}")

print("\n3️⃣  URL PATTERNS ANALYSIS:")
resolver = get_resolver()
print(f"   Total URL patterns: {len(resolver.url_patterns)}")
print("\n   Looking for 'api' and 'ligne-commande' patterns:")
for pattern in resolver.url_patterns:
    pattern_str = str(pattern.pattern)
    if 'api' in pattern_str or 'ligne' in pattern_str:
        print(f"   ✓ {pattern_str}")

print("\n4️⃣  REST FRAMEWORK ROUTER:")
from myapp import views
router = DefaultRouter()
router.register(r'clients', views.ClientViewSet)
router.register(r'plats', views.PlatViewSet)
router.register(r'menus', views.MenuViewSet)
router.register(r'commandes', views.CommandeViewSet)
router.register(r'ligne-commande', views.LigneCommandeViewSet)
router.register(r'ia', views.SystemeIAViewSet)

print("   Registered routes:")
for url_pattern in router.urls:
    print(f"   ✓ {url_pattern.pattern}")

print("\n5️⃣  CORRECT REQUEST FORMAT:")
print("   URL: http://localhost:8000/commande/api/ligne-commandes/")
print("   Method: POST")
print("   Header: Content-Type: application/json")
print("   Authentication: Required (IsAuthenticated by default)")
print("   Body example:")
print("   {")
print('       "menu_id": 1,')
print('       "quantite": 2')
print("   }")

print("\n6️⃣  TROUBLESHOOTING STEPS:")
print("   ❌ Getting 404? Check:")
print("      1. Is the URL exactly 'http://localhost:8000/commande/api/ligne-commandes/'?")
print("      2. Is the HTTP method POST?")
print("      3. Is localhost:8000 in ALLOWED_HOSTS?")
print("      4. Are you authenticated (have a valid session/token)?")
print("      5. Is the Django server running?")

print("\n" + "="*70 + "\n")
