from myapp.commande.models import Commande, LigneCommande
from myapp.profilNutritionnel.models import ProfilNutritionnel
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.html import mark_safe
from django.conf import settings
import json
import requests
import logging
import threading
import uuid
from datetime import datetime
from myapp.users.models import Client
from myapp.plat.models import Plat
from myapp.menu.models import Menu
from myapp.systemeIA.models import SystemeIA


logger = logging.getLogger(__name__)

# ===== Configuration Timeout N8N =====
N8N_WEBHOOK_TIMEOUT = getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 600)  # Default: 120 secondes
N8N_WEBHOOK_URL = getattr(settings, 'N8N_WEBHOOK_URL', 'http://192.168.1.184:5678/webhook/reco-nutrition')

# ===== Async Jobs Cache =====
# Dictionnaire pour stocker les résultats des jobs async
# Clé: job_id, Valeur: {'status': 'pending|completed|failed', 'result': {...}, 'error': {...}, 'timestamp': datetime}
async_jobs_cache = {}

from myapp.users.serializers import ClientSerializer
from myapp.profilNutritionnel.serializers import ProfilNutritionnelSerializer
from myapp.plat.serializers import PlatSerializer, UnifiedMenuItemSerializer
from myapp.menu.serializers import MenuSerializer
from myapp.commande.serializers import CommandeSerializer, LigneCommandeSerializer
from myapp.systemeIA.serializers import SystemeIASerializer


# ===== Template Views =====





def unified_browse(request):
    """Affiche la page de navigation unifiée pour menus et plats"""
    return render(request, 'menu/unified-browse.html', {})





def contact(request):
    """Affiche la page de contact"""
    return render(request, 'contact/contact.html', {})







def administrateur(request):
    """Affiche la page du profil administrateur"""
    return render(request, 'administrateur/administrateur.html', {})


