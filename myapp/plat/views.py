from tkinter import N

from myapp.commande.models import LigneCommande
from myapp.profilNutritionnel.models import ProfilNutritionnel
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import render
from django.utils.html import mark_safe
from django.conf import settings
import base64
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
from myapp.plat.serializers import PlatSerializer, UnifiedMenuItemSerializer


logger = logging.getLogger(__name__)

# ===== Configuration Timeout N8N =====
N8N_WEBHOOK_TIMEOUT = getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 600)  # Default: 120 secondes
N8N_WEBHOOK_URL_RECO_NUTRITION = getattr(settings, 'N8N_WEBHOOK_URL_RECO_NUTRITION', 'http://192.168.1.184:5678/webhook/reco-nutrition')
N8N_PLAT_CREATION_WEBHOOK_URL = getattr(settings, 'N8N_PLAT_CREATION_WEBHOOK_URL', N8N_WEBHOOK_URL_RECO_NUTRITION)
N8N_PLAT_MODIFICATION_WEBHOOK_URL = getattr(settings, 'N8N_PLAT_MODIFICATION_WEBHOOK_URL', N8N_WEBHOOK_URL_RECO_NUTRITION)
N8N_PLAT_DELETE_WEBHOOK_URL = getattr(settings, 'N8N_PLAT_DELETE_WEBHOOK_URL', N8N_WEBHOOK_URL_RECO_NUTRITION)
# ===== Async Jobs Cache =====

# Dictionnaire pour stocker les résultats des jobs async
# Clé: job_id, Valeur: {'status': 'pending|completed|failed', 'result': {...}, 'error': {...}, 'timestamp': datetime}
async_jobs_cache = {}


def list_plats(request):
    """Affiche la page des plats"""
    return render(request, 'plats/list_plats.html', {})


def ajouter_plat(request):
    """Affiche la page pour ajouter un nouveau plat"""
    return render(request, 'plats/ajouter_plat.html', {})

def modifier_plat(request):
    """Affiche la page pour modifier un plat"""
    return render(request, 'plats/modifier_plat.html', {})


def _serialize_plat(plat, default_image_url):
    """Utilitaire pour sérialiser un plat avec ses données nutritionnelles"""
    return {
        'id': plat.id_plat,
        'name': plat.nom,
        'calories': plat.calorie,
        'protein': plat.proteine,
        'carbs': plat.glucides,
        'fat': plat.lipides,
        'fiber': plat.fibres,
        'image': plat.image.url if plat.image else default_image_url,
        'description': plat.description,
        'score': plat.calculer_score_nutritionnel()
    }

def specialdiet(request):
    """Affiche la page des régimes spéciaux avec les plats dynamiques"""
    # Configuration pour les images par défaut
    default_image_url = getattr(settings, 'DEFAULT_MEAL_IMAGE_URL', 
                                'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500')
    
    # Récupérer tous les plats disponibles
    plats = Plat.objects.filter(est_disponible=True)
    
    # Organiser les plats par catégorie de régime spécial
    diet_meals = {
        "high-protein": [],
        "low-carb": [],
        "vegan": [],
        "gluten-free": []
    }
    
    # Configuration des critères de régime
    vegan_keywords = {'vegan', 'végétal', 'légume', 'fruit', 'légumineuse', 'tofu', 'pois chiche', 'lentille'}
    gluten_free_keywords = {'sans gluten', 'riz', 'quinoa', 'patate', 'légume', 'viande', 'poisson'}
    gluten_containing = {'pâte', 'pain', 'blé'}
    
    for plat in plats:
        plat_data = _serialize_plat(plat, default_image_url)
        plat_nom_lower = plat.nom.lower()
        plat_desc_lower = plat.description.lower()
        
        # High Protein: protéines >= 30g
        if plat.proteine >= 30:
            diet_meals["high-protein"].append(plat_data)
        
        # Low Carb: glucides <= 20g
        if plat.glucides <= 20:
            diet_meals["low-carb"].append(plat_data)
        
        # Vegan: contient mots-clés vegan
        if any(keyword in plat_nom_lower or keyword in plat_desc_lower for keyword in vegan_keywords):
            diet_meals["vegan"].append(plat_data)
        
        # Gluten-free: contient mots-clés sans gluten et n'en contient pas
        if any(keyword in plat_nom_lower or keyword in plat_desc_lower for keyword in gluten_free_keywords):
            if not any(keyword in plat_nom_lower for keyword in gluten_containing):
                diet_meals["gluten-free"].append(plat_data)
    
    context = {
        'plats': plats,
        'diet_meals_json': mark_safe(json.dumps(diet_meals))
    }
    return render(request, 'specialdiet/specialdiet-improved.html', context)



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
        Notifie N8N en arrière-plan si la suppression est réussie.
        """
        plat = self.get_object()
        plat_id = plat.id_plat
        plat_nom = plat.nom
        
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
        
        # Si le plat n'est pas utilisé, procéder à la suppression et notifier N8N
        response = super().destroy(request, *args, **kwargs)
        
        try:
            plat_temp = type('obj', (object,), {
                'id_plat': plat_id,
                'nom': plat_nom
            })()
            headers = self._get_n8n_auth_headers(request)
            print(f"DEBUG: Démarrage thread N8N pour suppression plat {plat_id} avec headers: {headers}")
            thread = threading.Thread(
                target=self._notify_n8n_plat_delete,
                args=(plat_temp, headers),
                daemon=True
            )
            thread.start()
            logger.info(f"Thread N8N créé pour la suppression du plat {plat_id}")
        except Exception as e:
            logger.error(f"Impossible de notifier N8N après suppression du plat: {e}")
        
        return response
    
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

    def _build_n8n_creation_payload(self, plat):
        """Construit le payload envoyé à N8N lors de la création d'un plat."""
        image_url = None
        try:
            if plat.image:
                image_url = plat.image.url
        except Exception:
            image_url = None

        return {
            'event': 'creationPlat',
            'plat': {
                'id_plat': plat.id_plat,
                'nom': plat.nom,
                'description': plat.description,
                'calorie': float(plat.calorie) if plat.calorie is not None else None,
                'proteine': float(plat.proteine) if plat.proteine is not None else None,
                'glucides': float(plat.glucides) if plat.glucides is not None else None,
                'lipides': float(plat.lipides) if plat.lipides is not None else None,
                'fibres': float(plat.fibres) if plat.fibres is not None else None,
                'prix': float(plat.prix) if plat.prix is not None else None,
                'est_disponible': plat.est_disponible,
                'isNew': plat.isNew,
                'image_url': image_url,
                'created_at': plat.created_at.isoformat() if plat.created_at else None
            },
            'source': 'healthy-ia'
        }

    def _get_n8n_auth_headers(self, request):
        """Retourne les headers d'authentification Basic Auth pour N8N."""
        auth_header = request.headers.get('Authorization') if hasattr(request, 'headers') else None
        if not auth_header:
            auth_header = request.META.get('HTTP_AUTHORIZATION')

        if auth_header and auth_header.strip().lower().startswith('basic '):
            return {'Authorization': auth_header.strip()}

        username = None
        password = None
        user = getattr(request, 'user', None)
        print(f"DEBUG: Récupération auth headers - User: {user}, Auth Header: {auth_header}")
        if user is not None and getattr(user, 'is_authenticated', False):
            admin_profile = getattr(user, 'administrateur', None)
            if admin_profile is not None:
                username = getattr(user, 'email', None) or getattr(user, 'username', None)
                password = getattr(admin_profile, 'n8n_basic_auth_password', None)

        if not username:
            username = getattr(settings, 'N8N_PLAT_CREATION_BASIC_AUTH_USER', None)
        if not password:
            password = getattr(settings, 'N8N_PLAT_CREATION_BASIC_AUTH_PASSWORD', None)

        if username and password:
            token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            return {'Authorization': f'Basic {token}'}

        return {}

    def _notify_n8n_plat_creation(self, plat, headers=None):
        """Envoie en arrière-plan un événement de création de plat à N8N."""
        payload = self._build_n8n_creation_payload(plat)
        auth_headers = headers or {}
        logger.info(f"Appel N8N création plat: {N8N_PLAT_CREATION_WEBHOOK_URL}")
        logger.debug(f"Payload création plat: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        logger.debug(f"Headers N8N création plat: {auth_headers}")
        print(f"DEBUG: Appel N8N création plat - URL: {N8N_PLAT_CREATION_WEBHOOK_URL}, Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}, Headers: {auth_headers}")
        try:
            response = requests.post(
                N8N_PLAT_CREATION_WEBHOOK_URL,
                json=payload,
                headers=auth_headers,
                timeout=N8N_WEBHOOK_TIMEOUT
            )
            logger.info(f"Réponse N8N création plat (status {response.status_code}): {response.text[:500]}")
            if response.status_code != 200:
                logger.warning(
                    f"N8N création plat a répondu {response.status_code}: {response.text[:500]}"
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout N8N création plat: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erreur de connexion N8N création plat: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel N8N création plat: {str(e)}")

    def create(self, request, *args, **kwargs):
        """Crée un nouveau plat et notifie N8N en arrière-plan."""
        response = super().create(request, *args, **kwargs)
        try:
            plat_id = response.data.get('id_plat') or response.data.get('id')
            if plat_id:
                plat = Plat.objects.get(id_plat=plat_id)
                headers = self._get_n8n_auth_headers(request)
                print(f"DEBUG: Démarrage thread N8N pour plat {plat_id} avec headers: {headers}")
                thread = threading.Thread(
                    target=self._notify_n8n_plat_creation,
                    args=(plat, headers),
                    daemon=True
                )
                thread.start()
                logger.info(f"Thread N8N créé pour la création du plat {plat_id}")
            else:
                logger.warning("Impossible de récupérer l'id du plat créé pour notifier N8N")
        except Exception as e:
            logger.error(f"Impossible de notifier N8N après création du plat: {e}")
        return response

    def _build_n8n_modification_payload(self, plat):
        """Construit le payload envoyé à N8N lors de la modification d'un plat."""
        image_url = None
        try:
            if plat.image:
                image_url = plat.image.url
        except Exception:
            image_url = None

        return {
            'event': 'modificationPlat',
            'plat': {
                'id_plat': plat.id_plat,
                'nom': plat.nom,
                'description': plat.description,
                'calorie': float(plat.calorie) if plat.calorie is not None else None,
                'proteine': float(plat.proteine) if plat.proteine is not None else None,
                'glucides': float(plat.glucides) if plat.glucides is not None else None,
                'lipides': float(plat.lipides) if plat.lipides is not None else None,
                'fibres': float(plat.fibres) if plat.fibres is not None else None,
                'prix': float(plat.prix) if plat.prix is not None else None,
                'est_disponible': plat.est_disponible,
                'isNew': plat.isNew,
                'image_url': image_url,
                'updated_at': plat.updated_at.isoformat() if hasattr(plat, 'updated_at') and plat.updated_at else None
            },
            'source': 'healthy-ia'
        }

    def _notify_n8n_plat_modification(self, plat, headers=None):
        """Envoie en arrière-plan un événement de modification de plat à N8N."""
        payload = self._build_n8n_modification_payload(plat)
        auth_headers = headers or {}
        logger.info(f"Appel N8N modification plat: {N8N_PLAT_MODIFICATION_WEBHOOK_URL}")
        logger.debug(f"Payload modification plat: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        logger.debug(f"Headers N8N modification plat: {auth_headers}")
        print(f"DEBUG: Appel N8N modification plat - URL: {N8N_PLAT_MODIFICATION_WEBHOOK_URL}, Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}, Headers: {auth_headers}")
        try:
            response = requests.post(
                N8N_PLAT_MODIFICATION_WEBHOOK_URL,
                json=payload,
                headers=auth_headers,
                timeout=N8N_WEBHOOK_TIMEOUT
            )
            logger.info(f"Réponse N8N modification plat (status {response.status_code}): {response.text[:500]}")
            if response.status_code != 200:
                logger.warning(
                    f"N8N modification plat a répondu {response.status_code}: {response.text[:500]}"
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout N8N modification plat: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erreur de connexion N8N modification plat: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel N8N modification plat: {str(e)}")

    def update(self, request, *args, **kwargs):
        """Modifie un plat et notifie N8N en arrière-plan."""
        response = super().update(request, *args, **kwargs)
        try:
            plat_id = response.data.get('id_plat') or response.data.get('id')
            if plat_id:
                plat = Plat.objects.get(id_plat=plat_id)
                headers = self._get_n8n_auth_headers(request)
                print(f"DEBUG: Démarrage thread N8N pour modification plat {plat_id} avec headers: {headers}")
                thread = threading.Thread(
                    target=self._notify_n8n_plat_modification,
                    args=(plat, headers),
                    daemon=True
                )
                thread.start()
                logger.info(f"Thread N8N créé pour la modification du plat {plat_id}")
            else:
                logger.warning("Impossible de récupérer l'id du plat modifié pour notifier N8N")
        except Exception as e:
            logger.error(f"Impossible de notifier N8N après modification du plat: {e}")
        return response

    def _build_n8n_deletion_payload(self, plat):
        """Construit le payload envoyé à N8N lors de la suppression d'un plat."""
        return {
            'event': 'suppressionPlat',
            'plat': {
                'id_plat': plat.id_plat,
                'nom': plat.nom,
                'deleted_at': datetime.now().isoformat()
            },
            'source': 'healthy-ia'
        }

    def _notify_n8n_plat_delete(self, plat, headers=None):
        """Envoie en arrière-plan un événement de suppression de plat à N8N."""
        payload = self._build_n8n_deletion_payload(plat)
        auth_headers = headers or {}
        logger.info(f"Appel N8N suppression plat: {N8N_PLAT_DELETE_WEBHOOK_URL}")
        logger.debug(f"Payload suppression plat: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        logger.debug(f"Headers N8N suppression plat: {auth_headers}")
        print(f"DEBUG: Appel N8N suppression plat - URL: {N8N_PLAT_DELETE_WEBHOOK_URL}, Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}, Headers: {auth_headers}")
        try:
            response = requests.post(
                N8N_PLAT_DELETE_WEBHOOK_URL,
                json=payload,
                headers=auth_headers,
                timeout=N8N_WEBHOOK_TIMEOUT
            )
            logger.info(f"Réponse N8N suppression plat (status {response.status_code}): {response.text[:500]}")
            if response.status_code != 200:
                logger.warning(
                    f"N8N suppression plat a répondu {response.status_code}: {response.text[:500]}"
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout N8N suppression plat: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erreur de connexion N8N suppression plat: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel N8N suppression plat: {str(e)}")


class RecommenderPlatsView(generics.ListAPIView):
    """Vue pour obtenir les menus recommandés basés sur le profil nutritionnel de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    
    # Configuration des limites de recommandation
    MAX_RECOMMENDATIONS = 100
    
    def get_serializer_class(self):
        """Retourne le serializer approprié"""
        from .serializers import MenuRecommandationSerializer
        return MenuRecommandationSerializer
    
    def _calculer_score_menu(self, menu, client):
        """Calcule le score pour un menu basé sur le profil du client (optimisé avec cache)"""
        from .score_constants import get_cached_score, set_cached_score
        
        try:
            # Clé de cache
            cache_key = f"menu_score_{menu.id_menu}_{client.id if hasattr(client, 'id') else 'unknown'}"
            cached_score = get_cached_score(cache_key)
            if cached_score is not None:
                return cached_score
            
            profil = client.profil_nutritionnel
            valeurs = menu.calculer_valeur_nutritionnelle_totale()
            score = 0.0
            
            # Score basé sur l'objectif nutritionnel (max 30)
            if profil.objectif == 'perte_poids':
                score += 30 if valeurs['calories'] < 600 else (20 if valeurs['calories'] < 800 else 5)
            elif profil.objectif == 'prise_muscle':
                score += 30 if valeurs['proteines'] > 30 else (20 if valeurs['proteines'] > 20 else 5)
            elif profil.objectif == 'performance':
                score += 30 if valeurs['calories'] > 700 else (20 if valeurs['calories'] > 500 else 5)
            else:
                score += 15  # Score neutre pour objectif unknown
            
            # Score nutritionnel (max 20)
            if valeurs.get('proteines'):
                score_nutritionnel = (valeurs['proteines'] * 2 - valeurs['lipides']) / 100
                score += max(0, min(20, score_nutritionnel))
            
            # Score d'équilibre macro (max 20)
            total_cals = (valeurs.get('glucides', 0) * 4) + (valeurs.get('proteines', 0) * 4) + (valeurs.get('lipides', 0) * 9)
            if total_cals > 0:
                carbs_ratio = (valeurs.get('glucides', 0) * 4) / total_cals
                protein_ratio = (valeurs.get('proteines', 0) * 4) / total_cals
                fat_ratio = (valeurs.get('lipides', 0) * 9) / total_cals
                
                distance = abs(carbs_ratio - 0.4) + abs(protein_ratio - 0.3) + abs(fat_ratio - 0.3)
                balance_score = max(0, 20 - (distance * 25))
                score += balance_score
            
            final_score = round(min(100, max(0, score)), 2)
            set_cached_score(cache_key, final_score)
            
            return final_score
        except Exception as e:
            print(f"Erreur lors du calcul du score menu: {e}")
            return 0.0
    
    def get_queryset(self):
        """Retourne les menus recommandés basés sur le profil nutritionnel"""
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Récupérer les menus recommandés via le système IA
            ia_system = SystemeIA.objects.first() or SystemeIA.objects.create()
            menus_recommandes = ia_system.recommander_menus(client, limite=self.MAX_RECOMMENDATIONS)
            return menus_recommandes
        except Client.DoesNotExist:
            return Menu.objects.none()
        except Exception as e:
            # Si erreur, retourner les menus actifs
            return Menu.objects.filter(est_actif=True)[:self.MAX_RECOMMENDATIONS]
    
    def list(self, request, *args, **kwargs):
        """Retourne les menus recommandés personnalisés pour l'utilisateur avec scores"""
        try:
            utilisateur = request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Récupérer les menus recommandés via le système IA
            ia_system = SystemeIA.objects.first() or SystemeIA.objects.create()
            menus_recommandes = ia_system.recommander_menus(client, limite=self.MAX_RECOMMENDATIONS)
            
            # Sérialiser les menus avec la liste de plats
            serializer = self.get_serializer(menus_recommandes, many=True)
            data = serializer.data
            
            # Ajouter le score à chaque menu
            for menu_data in data:
                try:
                    menu = Menu.objects.get(id_menu=menu_data['id_menu'])
                    menu_data['score'] = self._calculer_score_menu(menu, client)
                except Menu.DoesNotExist:
                    menu_data['score'] = 0.0
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Client.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            # Si erreur, retourner les menus actifs disponibles
            menus = Menu.objects.filter(est_actif=True)[:self.MAX_RECOMMENDATIONS]
            serializer = self.get_serializer(menus, many=True)
            data = serializer.data
            
            # Ajouter un score par défaut
            for menu_data in data:
                menu_data['score'] = 0.0
            
            return Response(data, status=status.HTTP_200_OK)


class RecommenderPlatsDirectView(generics.ListAPIView):
    """Vue pour obtenir les plats recommandés basés sur le profil nutritionnel de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    
    # Configuration des limites de recommandation
    MAX_RECOMMENDATIONS = 100
    
    def get_serializer_class(self):
        """Retourne le serializer approprié"""
        from .serializers import PlatRecommandationSerializer
        return PlatRecommandationSerializer
    
    def get_queryset(self):
        """Retourne les plats recommandés basés sur le profil nutritionnel"""
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Récupérer tous les plats disponibles
            plats = Plat.objects.filter(est_disponible=True)[:self.MAX_RECOMMENDATIONS]
            return plats
        except Client.DoesNotExist:
            return Plat.objects.none()
        except Exception as e:
            # Si erreur, retourner les plats disponibles
            return Plat.objects.filter(est_disponible=True)[:self.MAX_RECOMMENDATIONS]
    
    def list(self, request, *args, **kwargs):
        """Retourne les plats recommandés personnalisés pour l'utilisateur avec scores professionnels"""
        try:
            utilisateur = request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = client.profil_nutritionnel
            
            # Utiliser la méthode recommander_plats() du profil nutritionnel
            # Cette méthode retourne déjà les plats triés par score
            plats_recommandes = profil.recommander_plats(limite=self.MAX_RECOMMENDATIONS)
            
            # Sérialiser les plats
            serializer = self.get_serializer(plats_recommandes, many=True)
            data = serializer.data
            
            # Calculer le score PROFESSIONNEL pour chaque plat
            for i, plat_data in enumerate(data):
                try:
                    plat = Plat.objects.get(id_plat=plat_data['id_plat'])
                    # Utiliser la nouvelle méthode professionnelle
                    score = Plat.calculer_score_professionnel(plat, profil)
                    plat_data['score'] = score
                except Plat.DoesNotExist:
                    logger.warning(f"Plat {plat_data.get('id_plat')} not found")
                    plat_data['score'] = 0.0
                except Exception as e:
                    logger.error(f"Erreur calcul score pour plat {plat_data.get('nom', 'unknown')}: {str(e)}", exc_info=True)
                    plat_data['score'] = 0.0
            
            # Trier par score décroissant
            data = sorted(data, key=lambda x: x['score'], reverse=True)
            
            return Response(data, status=status.HTTP_200_OK)
        
        except ProfilNutritionnel.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Erreur dans recommander_plats: {str(e)}")
            import traceback
            traceback.print_exc()
            # Si erreur, retourner les plats disponibles avec score par défaut
            plats = Plat.objects.filter(est_disponible=True)[:self.MAX_RECOMMENDATIONS]
            serializer = self.get_serializer(plats, many=True)
            data = serializer.data
            
            # Ajouter un score par défaut
            for plat_data in data:
                plat_data['score'] = 0.0
            
            return Response(data, status=status.HTTP_200_OK)


class RecommenderPlatsView(generics.ListAPIView):
    """Vue pour obtenir les menus recommandés basés sur le profil nutritionnel de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    
    # Configuration des limites de recommandation
    MAX_RECOMMENDATIONS = 100
    
    def get_serializer_class(self):
        """Retourne le serializer approprié"""
        from .serializers import MenuRecommandationSerializer
        return MenuRecommandationSerializer
    
    def _calculer_score_menu(self, menu, client):
        """Calcule le score pour un menu basé sur le profil du client (optimisé avec cache)"""
        from .score_constants import get_cached_score, set_cached_score
        
        try:
            # Clé de cache
            cache_key = f"menu_score_{menu.id_menu}_{client.id if hasattr(client, 'id') else 'unknown'}"
            cached_score = get_cached_score(cache_key)
            if cached_score is not None:
                return cached_score
            
            profil = client.profil_nutritionnel
            valeurs = menu.calculer_valeur_nutritionnelle_totale()
            score = 0.0
            
            # Score basé sur l'objectif nutritionnel (max 30)
            if profil.objectif == 'perte_poids':
                score += 30 if valeurs['calories'] < 600 else (20 if valeurs['calories'] < 800 else 5)
            elif profil.objectif == 'prise_muscle':
                score += 30 if valeurs['proteines'] > 30 else (20 if valeurs['proteines'] > 20 else 5)
            elif profil.objectif == 'performance':
                score += 30 if valeurs['calories'] > 700 else (20 if valeurs['calories'] > 500 else 5)
            else:
                score += 15  # Score neutre pour objectif unknown
            
            # Score nutritionnel (max 20)
            if valeurs.get('proteines'):
                score_nutritionnel = (valeurs['proteines'] * 2 - valeurs['lipides']) / 100
                score += max(0, min(20, score_nutritionnel))
            
            # Score d'équilibre macro (max 20)
            total_cals = (valeurs.get('glucides', 0) * 4) + (valeurs.get('proteines', 0) * 4) + (valeurs.get('lipides', 0) * 9)
            if total_cals > 0:
                carbs_ratio = (valeurs.get('glucides', 0) * 4) / total_cals
                protein_ratio = (valeurs.get('proteines', 0) * 4) / total_cals
                fat_ratio = (valeurs.get('lipides', 0) * 9) / total_cals
                
                distance = abs(carbs_ratio - 0.4) + abs(protein_ratio - 0.3) + abs(fat_ratio - 0.3)
                balance_score = max(0, 20 - (distance * 25))
                score += balance_score
            
            final_score = round(min(100, max(0, score)), 2)
            set_cached_score(cache_key, final_score)
            
            return final_score
        except Exception as e:
            print(f"Erreur lors du calcul du score menu: {e}")
            return 0.0
    
    def get_queryset(self):
        """Retourne les menus recommandés basés sur le profil nutritionnel"""
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Récupérer les menus recommandés via le système IA
            ia_system = SystemeIA.objects.first() or SystemeIA.objects.create()
            menus_recommandes = ia_system.recommander_menus(client, limite=self.MAX_RECOMMENDATIONS)
            return menus_recommandes
        except Client.DoesNotExist:
            return Menu.objects.none()
        except Exception as e:
            # Si erreur, retourner les menus actifs
            return Menu.objects.filter(est_actif=True)[:self.MAX_RECOMMENDATIONS]
    
    def list(self, request, *args, **kwargs):
        """Retourne les menus recommandés personnalisés pour l'utilisateur avec scores"""
        try:
            utilisateur = request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Récupérer les menus recommandés via le système IA
            ia_system = SystemeIA.objects.first() or SystemeIA.objects.create()
            menus_recommandes = ia_system.recommander_menus(client, limite=self.MAX_RECOMMENDATIONS)
            
            # Sérialiser les menus avec la liste de plats
            serializer = self.get_serializer(menus_recommandes, many=True)
            data = serializer.data
            
            # Ajouter le score à chaque menu
            for menu_data in data:
                try:
                    menu = Menu.objects.get(id_menu=menu_data['id_menu'])
                    menu_data['score'] = self._calculer_score_menu(menu, client)
                except Menu.DoesNotExist:
                    menu_data['score'] = 0.0
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Client.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            # Si erreur, retourner les menus actifs disponibles
            menus = Menu.objects.filter(est_actif=True)[:self.MAX_RECOMMENDATIONS]
            serializer = self.get_serializer(menus, many=True)
            data = serializer.data
            
            # Ajouter un score par défaut
            for menu_data in data:
                menu_data['score'] = 0.0
            
            return Response(data, status=status.HTTP_200_OK)


class JobStatusView(generics.GenericAPIView):
    """
    Vue pour récupérer le statut et les résultats d'un job async
    GET /profilNutritionnel/api/profil-nutritionnel/recommander-n8n/job-status/?job_id=<uuid>
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Récupère le statut et les résultats d'un job async
        """
        job_id = request.query_params.get('job_id')
        
        if not job_id:
            logger.warning("Requête job_status sans job_id")
            return Response({
                'success': False,
                'error': 'job_id est requis',
                'usage': '/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/job-status/?job_id=<uuid>'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"JobStatusView.get() - job_id: {job_id}")
        
        if job_id not in async_jobs_cache:
            logger.warning(f"Job {job_id} non trouvé ou expiré")
            return Response({
                'success': False,
                'error': 'Job non trouvé ou expiré'
            }, status=status.HTTP_404_NOT_FOUND)
        
        job = async_jobs_cache[job_id]
        
        # Nettoyer les anciens jobs (plus de 1 heure)
        if (datetime.now() - job['timestamp']).total_seconds() > 3600:
            logger.warning(f"Job {job_id} expiré (plus de 1 heure)")
            del async_jobs_cache[job_id]
            return Response({
                'success': False,
                'error': 'Job expiré (plus de 1 heure)'
            }, status=status.HTTP_404_NOT_FOUND)
        
        response_data = {
            'job_id': job_id,
            'status': job['status'],
            'timestamp': job['timestamp'].isoformat()
        }
        
        logger.info(f"Job {job_id} - Status: {job['status']}")
        
        if job['status'] == 'pending':
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        elif job['status'] == 'completed':
            response_data.update(job['result'])
            logger.info(f"Job {job_id} complété avec succès")
            return Response(response_data, status=status.HTTP_200_OK)
        else:  # failed
            response_data.update(job['error'])
            logger.error(f"Job {job_id} échoué")
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== N8N Webhook Integration =====

class RecommenderIAProfilNutritionnelWebhookView(generics.GenericAPIView):
    """
    Vue pour appeler le webhook n8n et obtenir les recommandations nutritionnelles IA.
    Analyse du profil nutritionnel et recommandations personnalisées.
    
    POST /profilNutritionnel/api/profil-nutritionnel/recommander-n8n/
    Body: {
        "profil_id": 1,           (optionnel, utilisera le profil de l'utilisateur courant sinon)
        "async": false             (optionnel, default: false. Si true, retourne immédiatement avec un job_id)
    }
    
    Webhook n8n: http://localhost:5678/webhook/reco-nutrition
    
    Réponse: Analyse du profil nutritionnel avec priorités et macronutriments cibles
    
    Options:
    - Mode Synchrone (async: false ou absent):
      - Attendra la réponse du webhook (timeout configurable)
      - Retournera la réponse complète avec profil_analyse
    
    - Mode Asynchrone (async: true):
      - Retournera immédiatement avec un job_id
      - Le traitement se fait en arrière-plan
      - Utiliser GET /profilNutritionnel/api/profil-nutritionnel/recommander-n8n/job-status/{job_id}/ pour vérifier l'état
    """
    permission_classes = [IsAuthenticated]
    
    def _call_n8n_webhook(self, job_id, payload, logger_info=None):
        """
        Fonction pour appeler le webhook n8n en arrière-plan (utilisée pour async)
        """
        try:
            logger.info(f"[Job {job_id}] Appel du webhook n8n en arrière-plan...")
            logger.info(f"[Job {job_id}] Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                N8N_WEBHOOK_URL_RECO_NUTRITION,
                json=payload,
                timeout=N8N_WEBHOOK_TIMEOUT
            )
            
            logger.info(f"[Job {job_id}] Réponse n8n (status {response.status_code}): {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    recommendations = response.json()
                except json.JSONDecodeError:
                    recommendations = {'raw_response': response.text}
                
                # Stocker le résultat dans le cache
                async_jobs_cache[job_id] = {
                    'status': 'completed',
                    'result': {
                        'success': True,
                        'message': 'Recommandations obtenues avec succès',
                        'profil': payload['profil'],
                        'recommendations': recommendations
                    },
                    'timestamp': datetime.now()
                }
                logger.info(f"[Job {job_id}] Résultat stocké avec succès")
            else:
                async_jobs_cache[job_id] = {
                    'status': 'failed',
                    'error': {
                        'success': False,
                        'error': f'Erreur du webhook n8n: {response.status_code}',
                        'details': response.text[:1000]
                    },
                    'timestamp': datetime.now()
                }
                logger.error(f"[Job {job_id}] Erreur: {response.status_code}")
        
        except requests.exceptions.Timeout as e:
            logger.error(f"[Job {job_id}] Timeout du webhook n8n: {str(e)}")
            async_jobs_cache[job_id] = {
                'status': 'failed',
                'error': {
                    'success': False,
                    'error': f'Timeout du webhook n8n après {N8N_WEBHOOK_TIMEOUT}s',
                    'details': str(e)
                },
                'timestamp': datetime.now()
            }
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[Job {job_id}] Erreur de connexion: {str(e)}")
            async_jobs_cache[job_id] = {
                'status': 'failed',
                'error': {
                    'success': False,
                    'error': f'Impossible de se connecter au webhook n8n',
                    'webhook_url': N8N_WEBHOOK_URL_RECO_NUTRITION,
                    'details': str(e)
                },
                'timestamp': datetime.now()
            }
        
        except Exception as e:
            logger.error(f"[Job {job_id}] Erreur générale: {str(e)}")
            async_jobs_cache[job_id] = {
                'status': 'failed',
                'error': {
                    'success': False,
                    'error': f'Erreur lors de l\'appel au webhook',
                    'details': str(e)
                },
                'timestamp': datetime.now()
            }
    
    def post(self, request, *args, **kwargs):
        """
        Appelle le webhook n8n avec les données du profil nutritionnel
        Mode synchrone par défaut, asynchrone si async=true
        """
        logger.info(f"=== RecommenderIAProfilNutritionnelWebhookView.post() appelée ===")
        logger.info(f"Utilisateur authentifié: {request.user}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Timeout configuré: {N8N_WEBHOOK_TIMEOUT}s")
        
        # Vérifier si mode async demandé
        is_async = request.data.get('async', False)
        logger.info(f"Mode async: {is_async}")
        
        try:
            # Récupérer le profil nutritionnel
            try:
                profil_id = request.data.get('profil_id')
                logger.info(f"profil_id extrait: {profil_id}")
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction de profil_id: {str(e)}")
                profil_id = None
            
            if profil_id:
                try:
                    profil = ProfilNutritionnel.objects.get(id=profil_id)
                    logger.info(f"Profil trouvé par ID: {profil_id}")
                except ProfilNutritionnel.DoesNotExist:
                    logger.error(f"Profil avec ID {profil_id} non trouvé")
                    return Response({
                        'success': False,
                        'error': 'Profil nutritionnel non trouvé'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # Utiliser le profil de l'utilisateur courant
                try:
                    utilisateur = request.user
                    client = Client.objects.get(utilisateur=utilisateur)
                    profil = ProfilNutritionnel.objects.get(client=client)
                    logger.info(f"Profil trouvé pour l'utilisateur: {utilisateur}")
                except Client.DoesNotExist:
                    logger.error(f"Pas de Client trouvé pour l'utilisateur {utilisateur}")
                    return Response({
                        'success': False,
                        'error': 'Aucun client trouvé pour cet utilisateur'
                    }, status=status.HTTP_404_NOT_FOUND)
                except ProfilNutritionnel.DoesNotExist:
                    logger.error(f"Pas de ProfilNutritionnel trouvé")
                    return Response({
                        'success': False,
                        'error': 'Profil nutritionnel non trouvé pour cet utilisateur'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Préparer le payload pour n8n
            payload = {
                'profil': {
                    'age': profil.age,
                    'poids': float(profil.poids),
                    'taille': float(profil.taille),
                    'sexe': profil.sexe,
                    'objectif': profil.objectif,
                    'allergies': profil.allergies or '',
                    'restrictions_alimentaires': profil.restrictions_alimentaires or '',
                    'niveau_activite': profil.niveau_activite,
                    'imc': float(profil.calculer_imc()) if profil.calculer_imc() else None,
                    'bmr': float(profil.calculer_bmr()) if profil.calculer_bmr() else None,
                    'calories_cibles': float(profil.besoins_caloriques_journaliers()) if profil.besoins_caloriques_journaliers() else None,
                    'categorie_imc': str(profil.determiner_categorie_imc()) if profil.determiner_categorie_imc() else None
                }
            }
            
            # MODE ASYNCHRONE
            if is_async:
                job_id = str(uuid.uuid4())
                logger.info(f"Mode ASYNC activé - Job ID: {job_id}")
                
                # Marquer le job comme en attente
                async_jobs_cache[job_id] = {
                    'status': 'pending',
                    'result': None,
                    'timestamp': datetime.now()
                }
                
                # Lancer le traitement en arrière-plan (thread)
                thread = threading.Thread(
                    target=self._call_n8n_webhook,
                    args=(job_id, payload),
                    daemon=True
                )
                thread.start()
                logger.info(f"Thread lancé pour job {job_id}")
                
                return Response({
                    'success': True,
                    'message': 'Traitement lancé en arrière-plan',
                    'job_id': job_id,
                    'status': 'pending',
                    'check_status_url': f'/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/job-status/{job_id}/'
                }, status=status.HTTP_202_ACCEPTED)
            
            # MODE SYNCHRONE (par défaut)
            else:
                logger.info(f"Mode SYNCHRONE (timeout: {N8N_WEBHOOK_TIMEOUT}s)")
                
                try:
                    response = requests.post(
                        N8N_WEBHOOK_URL_RECO_NUTRITION,
                        json=payload,
                        timeout=N8N_WEBHOOK_TIMEOUT
                    )
                    
                    logger.info(f"Réponse n8n (status {response.status_code}): {response.text[:500]}")
                    
                    if response.status_code == 200:
                        try:
                            recommendations = response.json()
                        except json.JSONDecodeError:
                            recommendations = {'raw_response': response.text}
                        
                        return Response({
                            'success': True,
                            'message': 'Recommandations obtenues avec succès',
                            'profil': payload['profil'],
                            'recommendations': recommendations
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'success': False,
                            'error': f'Erreur du webhook n8n: {response.status_code}',
                            'details': response.text[:1000]
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                except requests.exceptions.Timeout as e:
                    logger.error(f"Timeout du webhook n8n: {str(e)}")
                    return Response({
                        'success': False,
                        'error': f'Timeout du webhook n8n après {N8N_WEBHOOK_TIMEOUT}s',
                        'details': str(e),
                        'suggestion': 'Essayez avec "async": true pour un traitement en arrière-plan'
                    }, status=status.HTTP_504_GATEWAY_TIMEOUT)
                
                except requests.exceptions.ConnectionError as e:
                    logger.error(f"Erreur de connexion: {str(e)}")
                    return Response({
                        'success': False,
                        'error': f'Impossible de se connecter au webhook n8n',
                        'webhook_url': N8N_WEBHOOK_URL_RECO_NUTRITION,
                        'details': str(e)
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
                except Exception as e:
                    logger.error(f"Erreur générale: {str(e)}")
                    return Response({
                        'success': False,
                        'error': f'Erreur lors de l\'appel au webhook',
                        'details': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"Erreur générale dans RecommenderIAProfilNutritionnelWebhookView: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Recherche dans les Menus et Plats par nom ou description.
        Paramètres: q (query string)
        """
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Le paramètre q est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = []
        
        # Rechercher dans les menus
        menus = Menu.objects.filter(
            est_actif=True
        ).filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )
        for menu in menus:
            serializer = UnifiedMenuItemSerializer(menu)
            items.append(serializer.data)
        
        # Rechercher dans les plats
        plats = Plat.objects.filter(
            est_disponible=True
        ).filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )
        for plat in plats:
            serializer = UnifiedMenuItemSerializer(plat)
            items.append(serializer.data)
        
        return Response(items, status=status.HTTP_200_OK)




# ============================================
# UNIFIED MENUS AND PLATS VIEWSET
# ============================================

class UnifiedMenuItemViewSet(viewsets.ViewSet):
    """
    ViewSet unifié pour combiner Menus et Plats avec catégorisation par régime.
    Permet de récupérer tous les articles (Menus + Plats) avec filtrage par catégorie de régime.
    """
    print("UnifiedMenuItemViewSet initialisé")
    permission_classes = [AllowAny]
    
    def list(self, request):
        """
        Liste tous les Menus et Plats avec filtrage optionnel par catégorie de régime.
        Paramètres de requête:
        - diet_category: 'high-protein', 'low-carb', 'vegan', 'gluten-free', ou 'autre'
        - item_type: 'menu' ou 'plat' pour filtrer par type
        """
        print("UnifiedMenuItemViewSet.list() appelée")
        diet_category = request.query_params.get('diet_category', None)
        item_type = request.query_params.get('item_type', None)
        
        items = []
        
        # Récupérer les menus actifs
        if item_type is None or item_type == 'menu':
            menus = Menu.objects.filter(est_actif=True)
            print(f"Menus avant filtrage: {menus.count()}")
            if diet_category:
                menus = menus.filter(diet_category=diet_category)
            
            for menu in menus:
                serializer = UnifiedMenuItemSerializer(menu)
                print(f"Menu sérialisé: {serializer.data}")
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


