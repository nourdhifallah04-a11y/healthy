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




# ===== API ViewSets =====

class SystemeIAViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour le système IA de recommandation de menus.
    Permet de consulter les recommandations et analyser les préférences.
    """
    queryset = SystemeIA.objects.filter(est_actif=True)
    serializer_class = SystemeIASerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recommandations(self, request):
        """Récupère les recommandations de menus personnalisées pour un client"""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response(
                {'error': 'client_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(id=client_id)
            ia_system = SystemeIA.objects.filter(est_actif=True).first()
            
            if not ia_system:
                return Response(
                    {'error': 'Système IA non disponible'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            recommandations = ia_system.recommander_menus(client)
            serializer = MenuSerializer(recommandations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def analyser_preferences(self, request):
        """Analyse les préférences alimentaires d'un client"""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response(
                {'error': 'client_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(id=client_id)
            ia_system = SystemeIA.objects.filter(est_actif=True).first()
            
            if not ia_system:
                return Response(
                    {'error': 'Système IA non disponible'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            preferences = ia_system.analyser_preferences(client)
            return Response(preferences, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )



# ============================================
# UNIFIED MENUS AND PLATS VIEWSET
# ============================================

class UnifiedMenuItemViewSet(viewsets.ViewSet):
    """
    ViewSet unifié pour combiner Menus et Plats avec catégorisation par régime.
    Permet de récupérer tous les articles (Menus + Plats) avec filtrage par catégorie de régime.
    """
    permission_classes = [AllowAny]
    
    def list(self, request):
        """
        Liste tous les Menus et Plats avec filtrage optionnel par catégorie de régime.
        Paramètres de requête:
        - diet_category: 'high-protein', 'low-carb', 'vegan', 'gluten-free', ou 'autre'
        - item_type: 'menu' ou 'plat' pour filtrer par type
        """
        diet_category = request.query_params.get('diet_category', None)
        item_type = request.query_params.get('item_type', None)
        
        items = []
        
        # Récupérer les menus actifs
        if item_type is None or item_type == 'menu':
            menus = Menu.objects.filter(est_actif=True)
            
            if diet_category:
                menus = menus.filter(diet_category=diet_category)
            
            for menu in menus:
                serializer = UnifiedMenuItemSerializer(menu)
                items.append(serializer.data)
        
        # Récupérer les plats disponibles
        if item_type is None or item_type == 'plat':
            plats = Plat.objects.filter(est_disponible=True)
            
            # Filtrer par catégorie de régime basée sur les propriétés du plat
            if diet_category:
                filtered_plats = []
                for plat in plats:
                    if diet_category in plat.get_diet_categories():
                        filtered_plats.append(plat)
                plats = filtered_plats
            
            for plat in plats:
                serializer = UnifiedMenuItemSerializer(plat)
                items.append(serializer.data)
        
        return Response(items, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def diet_categories(self, request):
        """Retourne les catégories de régime disponibles"""
        categories = [
            {'id': 'high-protein', 'name': 'High Protein'},
            {'id': 'low-carb', 'name': 'Low Carb'},
            {'id': 'vegan', 'name': 'Vegan'},
            {'id': 'gluten-free', 'name': 'Sans Gluten'},
            {'id': 'autre', 'name': 'Autre'},
        ]
        return Response(categories, status=status.HTTP_200_OK)



# ============================================
# COMMANDE API VIEWSET ENHANCEMENTS
# ============================================

# Ajouter la méthode calculer_nutrition_totale au modèle Commande
# Dans models.py:
# def calculer_nutrition_totale(self):
#     """Calcule les valeurs nutritionnelles totales de la commande"""
#     total_calories = 0
#     total_proteines = 0
#     total_glucides = 0
#     total_lipides = 0
#
#     for ligne in self.lignecommande_set.all():
#         valeurs = ligne.menu.calculer_valeur_nutritionnelle_totale()
#         total_calories += valeurs.get('calories', 0) * ligne.quantite
#         total_proteines += valeurs.get('proteines', 0) * ligne.quantite
#         total_glucides += valeurs.get('glucides', 0) * ligne.quantite
#         total_lipides += valeurs.get('lipides', 0) * ligne.quantite
#
#     return {
#         'calories': total_calories,
#         'proteines': total_proteines,
#         'glucides': total_glucides,
#         'lipides': total_lipides
#     }