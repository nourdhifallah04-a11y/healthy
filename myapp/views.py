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

class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les clients.
    Permet de lister, créer, récupérer, mettre à jour et supprimer les clients.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Les utilisateurs voient uniquement leurs données, sauf s'ils sont admin"""
        user = self.request.user
        if user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(utilisateur=user)
    
    @action(detail=True, methods=['get'])
    def profil_nutritionnel(self, request, pk=None):
        """Récupère le profil nutritionnel d'un client"""
        client = self.get_object()
        try:
            profil = ProfilNutritionnel.objects.get(client=client)
            serializer = ProfilNutritionnelSerializer(profil)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProfilNutritionnel.DoesNotExist:
            return Response(
                {'error': 'Profil nutritionnel non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def creer_profil(self, request, pk=None):
        """Crée ou met à jour le profil nutritionnel d'un client"""
        client = self.get_object()
        try:
            profil = ProfilNutritionnel.objects.get(client=client)
            serializer = ProfilNutritionnelSerializer(profil, data=request.data, partial=True)
            is_create = False
        except ProfilNutritionnel.DoesNotExist:
            serializer = ProfilNutritionnelSerializer(data=request.data)
            is_create = True
        
        if serializer.is_valid():
            serializer.save(client=client)
            status_code = status.HTTP_201_CREATED if is_create else status.HTTP_200_OK
            return Response(serializer.data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def historique_commandes(self, request, pk=None):
        """Récupère l'historique des commandes d'un client"""
        client = self.get_object()
        commandes = Commande.objects.filter(client=client).order_by('-date')
        serializer = CommandeSerializer(commandes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PlatViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les plats.
    Permet de rechercher, filtrer et consulter les plats.
    """
    queryset = Plat.objects.all()
    serializer_class = PlatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les plats selon les paramètres de requête"""
        queryset = Plat.objects.all()
        disponible = self.request.query_params.get('disponible')
        if disponible:
            queryset = queryset.filter(est_disponible=disponible.lower() == 'true')
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """
        Supprime un plat en vérifiant d'abord s'il est utilisé dans un menu ou une ligne de commande avec statut panier.
        Retourne une erreur 409 CONFLICT si le plat est utilisé.
        """
        plat = self.get_object()
        
        # Vérifier si le plat est utilisé dans une menu
        est_utilise_dans_menu = Menu.objects.filter(plats=plat).exists()
        
        # Vérifier si le plat est utilisé dans une ligne de commande avec statut panier
        est_utilise_dans_ligne_commande = LigneCommande.objects.filter(plat=plat, commande__statut='panier').exists()
        
        if est_utilise_dans_menu or est_utilise_dans_ligne_commande:
            messages_details = []
            if est_utilise_dans_menu:
                messages_details.append('ce plat est utilisé dans un ou plusieurs menus')
            if est_utilise_dans_ligne_commande:
                messages_details.append('ce plat est utilisé dans une ou plusieurs commandes')
            
            return Response(
                {
                    'error': 'Ce plat ne peut pas être supprimé',
                    'details': ' et '.join(messages_details),
                    'plat_id': plat.id_plat,
                    'nom_plat': plat.nom,
                    'est_utilise_dans_menu': est_utilise_dans_menu,
                    'est_utilise_dans_ligne_commande': est_utilise_dans_ligne_commande
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Si le plat n'est pas utilisé, procéder à la suppression
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche les plats par nom ou description"""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Le paramètre q est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        plats = Plat.objects.filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )
        serializer = self.get_serializer(plats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def score_nutritionnel(self, request, pk=None):
        """Récupère le score nutritionnel d'un plat"""
        plat = self.get_object()
        try:
            score = plat.calculer_score_nutritionnel()
            return Response({'score': score, 'plat': plat.nom}, status=status.HTTP_200_OK)
        except AttributeError:
            return Response(
                {'error': 'La méthode calculer_score_nutritionnel n\'est pas disponible'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommandeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commandes.
    Permet de créer, consulter, valider et gérer les articles des commandes.
    """
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Les utilisateurs voient uniquement leur dernière commande, sauf s'ils sont admin"""
        user = self.request.user
        if user.is_superuser:
            return Commande.objects.all().order_by('-id_commande')
        
        # Retourner uniquement la dernière commande de l'utilisateur
        commandes = Commande.objects.filter(client__utilisateur=user).order_by('-id_commande')
        return commandes[:1] if commandes.exists() else commandes
    
    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Valide une commande (passe du statut panier à confirmée)"""
        commande = self.get_object()
        try:
            if commande.valider_commande():
                return Response({'status': 'commande validée'}, status=status.HTTP_200_OK)
            return Response(
                {'error': 'La commande ne peut pas être validée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except AttributeError:
            return Response(
                {'error': 'La méthode valider_commande n\'est pas disponible'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def ajouter_menu(self, request, pk=None):
        """Ajoute un menu à une commande"""
        commande = self.get_object()
        menu_id = request.data.get('menu_id')
        quantite = request.data.get('quantite', 1)
        
        try:
            menu = Menu.objects.get(id=menu_id)
            # Calculer le prix total des plats du menu
            prix_total = menu.calculer_valeur_nutritionnelle_totale()['prix']
            
            LigneCommande.objects.create(
                commande=commande,
                menu=menu,
                quantite=quantite,
                prix_unitaire=prix_total
            )
            commande.calculer_total()
            serializer = self.get_serializer(commande)
            return Response(serializer.data)
        except Menu.DoesNotExist:
            return Response(
                {'error': 'Menu non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def calculer_total(self, request, pk=None):
        """Recalcule le total d'une commande"""
        commande = self.get_object()
        try:
            total = commande.calculer_total()
            return Response({'total': str(total)}, status=status.HTTP_200_OK)
        except AttributeError:
            return Response(
                {'error': 'La méthode calculer_total n\'est pas disponible'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LigneCommandeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les lignes de commande.
    Permet d'ajouter, modifier et supprimer des articles dans une commande.
    """
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Les utilisateurs voient uniquement les lignes de leurs commandes"""
        user = self.request.user
        if user.is_superuser:
            return LigneCommande.objects.all()
        return LigneCommande.objects.filter(commande__client__utilisateur=user)
    
    def create(self, request, *args, **kwargs):
        """Crée une nouvelle ligne de commande (ajoute un article au panier)
        Supporte à la fois menu_id et plat_id"""
        user = request.user
        menu_id = request.data.get('menu_id')
        plat_id = request.data.get('plat_id')
        quantite = request.data.get('quantite', 1)
        
        # Validation: au moins un ID doit être fourni
        if not menu_id and not plat_id:
            return Response(
                {'error': 'Soit menu_id soit plat_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validation de la quantité
        try:
            quantite = int(quantite)
            if quantite <= 0:
                return Response(
                    {'error': 'La quantité doit être positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'La quantité doit être un nombre entier'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Récupérer ou créer le client
            client = Client.objects.get(utilisateur=user)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Récupérer le menu ou plat
        menu = None
        plat = None
        prix_unitaire = 0
        
        if menu_id:
            try:
                menu = Menu.objects.get(id_menu=menu_id)
                menu_values = menu.calculer_valeur_nutritionnelle_totale()
                prix_unitaire = menu_values.get('prix', 0)
            except (Menu.DoesNotExist, ValueError):
                return Response(
                    {'error': 'Menu non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif plat_id:
            try:
                plat = Plat.objects.get(id_plat=plat_id)
                prix_unitaire = float(plat.prix)
            except (Plat.DoesNotExist, ValueError):
                return Response(
                    {'error': 'Plat non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            # Récupérer ou créer la commande (panier)
            commande, created = Commande.objects.get_or_create(
                client=client,
                statut='panier'
            )
            
            # Vérifier si l'article existe déjà dans le panier
            if menu:
                ligne_existante = LigneCommande.objects.filter(
                    commande=commande,
                    menu=menu,
                    plat=None
                ).first()
            else:  # plat
                ligne_existante = LigneCommande.objects.filter(
                    commande=commande,
                    plat=plat,
                    menu=None
                ).first()
            
            if ligne_existante:
                # Si l'article existe déjà, augmenter la quantité
                ligne_existante.quantite += quantite
                ligne_existante.save()
                ligne = ligne_existante
            else:
                # Sinon, créer une nouvelle ligne
                ligne = LigneCommande.objects.create(
                    commande=commande,
                    menu=menu,
                    plat=plat,
                    quantite=quantite,
                    prix_unitaire=prix_unitaire
                )
            
            serializer = self.get_serializer(ligne)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
# COMMANDE VIEWS (Panier, Checkout, Commandes)
# ============================================

@require_http_methods(["GET", "POST"])
def panier(request):
    """
    Affiche le panier (cart) de l'utilisateur
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        client = Client.objects.get(utilisateur=request.user)
        # Récupérer ou créer la commande panier de l'utilisateur
        commande, created = Commande.objects.get_or_create(
            client=client,
            statut='panier'
        )
    except Client.DoesNotExist:
        messages.error(request, "Veuillez d'abord créer un profil client")
        return redirect('accueil')
    
    # Recalculer le total
    commande.calculer_total()
    
    context = {
        'commande': commande,
    }
    return render(request, 'commande/panier.html', context)


@require_http_methods(["GET", "POST"])
def checkout(request):
    """
    Page de validation et finalisation de la commande
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        client = Client.objects.get(utilisateur=request.user)
        commande = Commande.objects.get(client=client, statut='panier')
    except (Client.DoesNotExist, Commande.DoesNotExist):
        messages.error(request, "Votre panier est vide")
        return redirect('panier')
    
    if request.method == 'POST':
        # Mettre à jour la commande avec les infos de livraison
        commande.adresse_livraison = request.POST.get('adresse_livraison', '')
        commande.notes = request.POST.get('notes', '')
        commande.statut = 'confirmee'
        commande.save()
        
        messages.success(request, "Commande confirmée avec succès!")
        return redirect('commande_confirmation', commande_id=commande.id_commande)
    
    context = {
        'commande': commande,
        'user': request.user,
    }
    return render(request, 'commande/checkout.html', context)


def commande_confirmation(request, commande_id):
    """
    Page de confirmation après la commande
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        commande = Commande.objects.get(id_commande=commande_id)
        
        # Vérifier que l'utilisateur est propriétaire de la commande
        if commande.client.utilisateur != request.user:
            messages.error(request, "Accès non autorisé")
            return redirect('accueil')
    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée")
        return redirect('accueil')
    
    context = {
        'commande': commande,
        'user': request.user,
    }
    return render(request, 'commande/commande_confirmation.html', context)


def mes_commandes(request):
    """
    Affiche l'historique des commandes de l'utilisateur
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        client = Client.objects.get(utilisateur=request.user)
        commandes = client.commandes.all().order_by('-date')
    except Client.DoesNotExist:
        messages.error(request, "Veuillez d'abord créer un profil client")
        return redirect('accueil')
    
    context = {
        'commandes': commandes,
    }
    return render(request, 'commande/mes_commandes.html', context)


def commande_detail(request, commande_id):
    """
    Affiche les détails d'une commande spécifique
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        commande = Commande.objects.get(id_commande=commande_id)
        
        # Vérifier que l'utilisateur est propriétaire de la commande
        if commande.client.utilisateur != request.user:
            messages.error(request, "Accès non autorisé")
            return redirect('accueil')
    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée")
        return redirect('mes_commandes')
    
    context = {
        'commande': commande,
        'user': request.user,
    }
    return render(request, 'commande/commande_detail.html', context)


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