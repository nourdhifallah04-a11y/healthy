from myapp.commande.models import LigneCommande
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.conf import settings
import logging
import base64
import json
import requests
import threading
import uuid
from datetime import datetime
from myapp.plat.models import Plat
from myapp.menu.models import Menu
from myapp.menu.serializers import MenuSerializer

logger = logging.getLogger(__name__)

# ===== Configuration Timeout N8N =====
N8N_WEBHOOK_TIMEOUT = getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 120)
N8N_MENU_CREATION_WEBHOOK_URL = getattr(settings, 'N8N_MENU_CREATION_WEBHOOK_URL', 'http://192.168.1.17:5678/webhook/menu-creation')
N8N_MENU_MODIFICATION_WEBHOOK_URL = getattr(settings, 'N8N_MENU_MODIFICATION_WEBHOOK_URL', 'http://192.168.1.17:5678/webhook/menu-modification')
N8N_MENU_DELETE_WEBHOOK_URL = getattr(settings, 'N8N_MENU_DELETE_WEBHOOK_URL', 'http://192.168.1.17:5678/webhook/menu-suppression')

def menu(request):
    """Affiche la page de menu"""
    return render(request, 'menu/menu.html', {})


def unified_browse(request):
    """Affiche la page de navigation unifiée pour menus et plats"""
    return render(request, 'menu/unified-browse.html', {})

def list_menus(request):
    """Affiche la page de gestion des menus"""
    return render(request, 'menu/list_menus.html', {})

def ajouter_menu(request):
    """Affiche la page pour ajouter un nouveau menu"""
    return render(request, 'menu/ajouter_menu.html', {})

def modifier_menu(request):
    """Affiche la page pour modifier un menu"""
    return render(request, 'menu/modifier_menu.html', {})


class MenuViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les menus.
    Permet de créer, consulter, ajouter/supprimer des plats et calculer les valeurs nutritionnelles.
    """
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les menus selon s'ils sont actifs ou non"""
        queryset = Menu.objects.all()
        actif = self.request.query_params.get('actif')
        if actif:
            queryset = queryset.filter(est_actif=actif.lower() == 'true')
        return queryset
    
    @action(detail=False, methods=['post'])
    def creer_avec_plats(self, request):
        """Crée un menu avec des plats en un seul appel"""
        try:
            menu_data = request.data.get('menu', {})
            plats_data = request.data.get('plats', [])
            
            # Créer le menu
            menu_serializer = self.get_serializer(data=menu_data)
            if not menu_serializer.is_valid():
                return Response(
                    {'error': 'Données du menu invalides', 'details': menu_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            menu = menu_serializer.save()
            
            # Ajouter les plats au menu
            for plat_info in plats_data:
                plat_id = plat_info.get('plat_id')
                quantite = plat_info.get('quantite', 1)
                
                if not plat_id:
                    menu.delete()
                    return Response(
                        {'error': 'plat_id est requis pour chaque plat'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    quantite = int(quantite)
                    if quantite <= 0:
                        menu.delete()
                        return Response(
                            {'error': 'La quantité doit être positive'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    plat = Plat.objects.get(id_plat=plat_id)
                    menu.ajouter_plat(plat, quantite)
                except ValueError:
                    menu.delete()
                    return Response(
                        {'error': 'La quantité doit être un nombre entier'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except Plat.DoesNotExist:
                    menu.delete()
                    return Response(
                        {'error': f'Plat avec l\'id {plat_id} non trouvé'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Retourner le menu avec ses plats
            serializer = self.get_serializer(menu)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f'Erreur lors de la création du menu avec plats: {str(e)}')
            return Response(
                {'error': 'Erreur lors de la création du menu'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def ajouter_plat(self, request, pk=None):
        """Ajoute un plat à un menu"""
        menu = self.get_object()
        plat_id = request.data.get('plat_id')
        quantite = request.data.get('quantite', 1)
        
        if not plat_id:
            return Response(
                {'error': 'plat_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantite = int(quantite)
            if quantite <= 0:
                return Response(
                    {'error': 'La quantité doit être positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            plat = Plat.objects.get(id=plat_id)
            menu.ajouter_plat(plat, quantite)
            serializer = self.get_serializer(menu)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {'error': 'La quantité doit être un nombre entier'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Plat.DoesNotExist:
            return Response(
                {'error': 'Plat non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def supprimer_plat(self, request, pk=None):
        """Supprime un plat d'un menu"""
        menu = self.get_object()
        plat_id = request.data.get('plat_id')
        
        if not plat_id:
            return Response(
                {'error': 'plat_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            plat = Plat.objects.get(id=plat_id)
            est_utilise_dans_commande = LigneCommande.objects.filter(plat=plat).exists()
            if est_utilise_dans_commande:
                return Response(
                    {
                        'error': 'Ce plat ne peut pas être supprimé car il est utilisé dans une ou plusieurs commandes',
                        'plat_id': plat_id,
                        'nom_plat': plat.nom
                    },
                    status=status.HTTP_409_CONFLICT
            )
            menu.supprimer_plat(plat)
            return Response({'status': 'plat supprimé'}, status=status.HTTP_200_OK)
        except Plat.DoesNotExist:
            return Response(
                {'error': 'Plat non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def valeur_nutritionnelle(self, request, pk=None):
        """Calcule les valeurs nutritionnelles totales d'un menu"""
        menu = self.get_object()
        try:
            valeurs = menu.calculer_valeur_nutritionnelle_totale()
            return Response(valeurs, status=status.HTTP_200_OK)
        except AttributeError:
            return Response(
                {'error': 'La méthode calculer_valeur_nutritionnelle_totale n\'est pas disponible'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
        print(f"DEBUG: Récupération auth headers menu - User: {user}, Auth Header: {auth_header}")
        if user is not None and getattr(user, 'is_authenticated', False):
            admin_profile = getattr(user, 'administrateur', None)
            if admin_profile is not None:
                username = getattr(user, 'email', None) or getattr(user, 'username', None)
                password = getattr(admin_profile, 'n8n_basic_auth_password', None)

        if not username:
            username = getattr(settings, 'N8N_MENU_CREATION_BASIC_AUTH_USER', None)
        if not password:
            password = getattr(settings, 'N8N_MENU_CREATION_BASIC_AUTH_PASSWORD', None)

        if username and password:
            token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            return {'Authorization': f'Basic {token}'}

        return {}

    def _build_n8n_creation_payload(self, menu):
        """Construit le payload envoyé à N8N lors de la création d'un menu."""
        plats_ids = []
        try:
            print(f"DEBUG: Construction payload N8N création menu - plats: {menu.plats.all().values_list('id_plat', flat=True)}, nom: {menu.nom}")
            for item in menu.plats.all():
                plats_ids.append(str(item.id_plat))
                print(f"DEBUG: Plat ajouté au payload N8N création menu - id_plat: {item.id_plat}")
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des plats du menu: {e}")

        return {
            'event': 'creationMenu',
            'menu': {
                'id_menu': menu.id_menu,
                'nom': menu.nom,
                'description': menu.description if hasattr(menu, 'description') else '',
                'diet_category': menu.get_diet_category() if hasattr(menu, 'get_diet_category') else 'inconnue',
                'plats': ','.join(plats_ids),
                'date_debut': menu.date_debut.isoformat() if hasattr(menu, 'date_debut') and menu.date_debut else None,
                'date_fin': menu.date_fin.isoformat() if hasattr(menu, 'date_fin') and menu.date_fin else None,
                'est_actif': menu.est_actif,
                'created_at': menu.created_at.isoformat() if hasattr(menu, 'created_at') and menu.created_at else None
            },
            'source': 'healthy-ia'
        }

    def _build_n8n_modification_payload(self, menu):
        """Construit le payload envoyé à N8N lors de la modification d'un menu."""
        plats_ids = []
        try:
            for item in menu.plats.all():
                plats_ids.append(str(item.id_plat))
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des plats du menu: {e}")

        return {
            'event': 'modificationMenu',
            'menu': {
                'id_menu': menu.id_menu,
                'nom': menu.nom,
                'description': menu.description if hasattr(menu, 'description') else '',
                'plats': ','.join(plats_ids),
                'diet_category': menu.get_diet_category() if hasattr(menu, 'get_diet_category') else 'inconnue',
                'date_debut': menu.date_debut.isoformat() if hasattr(menu, 'date_debut') and menu.date_debut else None,
                'date_fin': menu.date_fin.isoformat() if hasattr(menu, 'date_fin') and menu.date_fin else None,
                'est_actif': menu.est_actif,
                'modified_at': datetime.now().isoformat()
            },
            'source': 'healthy-ia'
        }

    def _build_n8n_deletion_payload(self, menu):
        """Construit le payload envoyé à N8N lors de la suppression d'un menu."""
        return {
            'event': 'suppressionMenu',
            'menu': {
                'id_menu': menu.id_menu,
                'nom': menu.nom,
                'deleted_at': datetime.now().isoformat()
            },
            'source': 'healthy-ia'
        }

    def _notify_n8n_menu_creation(self, menu, headers=None):
        """Envoie en arrière-plan un événement de création de menu à N8N."""
        payload = self._build_n8n_creation_payload(menu)
        auth_headers = headers or {}
        logger.info(f"Appel N8N création menu: {N8N_MENU_CREATION_WEBHOOK_URL}")
        logger.debug(f"Payload création menu: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        logger.debug(f"Headers N8N création menu: {auth_headers}")
        print(f"DEBUG: Appel N8N création menu - URL: {N8N_MENU_CREATION_WEBHOOK_URL}, Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}, Headers: {auth_headers}")
        try:
            response = requests.post(
                N8N_MENU_CREATION_WEBHOOK_URL,
                json=payload,
                headers=auth_headers,
                timeout=N8N_WEBHOOK_TIMEOUT
            )
            logger.info(f"Réponse N8N création menu (status {response.status_code}): {response.text[:500]}")
            if response.status_code != 200:
                logger.warning(
                    f"N8N création menu a répondu {response.status_code}: {response.text[:500]}"
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout N8N création menu: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erreur de connexion N8N création menu: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel N8N création menu: {str(e)}")

    def _notify_n8n_menu_modification(self, menu, headers=None):
        """Envoie en arrière-plan un événement de modification de menu à N8N."""
        payload = self._build_n8n_modification_payload(menu)
        auth_headers = headers or {}
        logger.info(f"Appel N8N modification menu: {N8N_MENU_MODIFICATION_WEBHOOK_URL}")
        logger.debug(f"Payload modification menu: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        logger.debug(f"Headers N8N modification menu: {auth_headers}")
        print(f"DEBUG: Appel N8N modification menu - URL: {N8N_MENU_MODIFICATION_WEBHOOK_URL}, Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}, Headers: {auth_headers}")
        try:
            response = requests.post(
                N8N_MENU_MODIFICATION_WEBHOOK_URL,
                json=payload,
                headers=auth_headers,
                timeout=N8N_WEBHOOK_TIMEOUT
            )
            logger.info(f"Réponse N8N modification menu (status {response.status_code}): {response.text[:500]}")
            if response.status_code != 200:
                logger.warning(
                    f"N8N modification menu a répondu {response.status_code}: {response.text[:500]}"
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout N8N modification menu: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erreur de connexion N8N modification menu: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel N8N modification menu: {str(e)}")

    def _notify_n8n_menu_delete(self, menu, headers=None):
        """Envoie en arrière-plan un événement de suppression de menu à N8N."""
        payload = self._build_n8n_deletion_payload(menu)
        auth_headers = headers or {}
        logger.info(f"Appel N8N suppression menu: {N8N_MENU_DELETE_WEBHOOK_URL}")
        logger.debug(f"Payload suppression menu: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        logger.debug(f"Headers N8N suppression menu: {auth_headers}")
        print(f"DEBUG: Appel N8N suppression menu - URL: {N8N_MENU_DELETE_WEBHOOK_URL}, Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}, Headers: {auth_headers}")
        try:
            response = requests.post(
                N8N_MENU_DELETE_WEBHOOK_URL,
                json=payload,
                headers=auth_headers,
                timeout=N8N_WEBHOOK_TIMEOUT
            )
            logger.info(f"Réponse N8N suppression menu (status {response.status_code}): {response.text[:500]}")
            if response.status_code != 200:
                logger.warning(
                    f"N8N suppression menu a répondu {response.status_code}: {response.text[:500]}"
                )
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout N8N suppression menu: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erreur de connexion N8N suppression menu: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel N8N suppression menu: {str(e)}")

    def create(self, request, *args, **kwargs):
        """Crée un nouveau menu avec plats et notifie N8N en arrière-plan."""
        # Extraire les plats du payload s'ils existent
        plats_data = request.data.get('plats', [])
        
        # Créer une copie mutable des données pour éviter de modifier request.data
        data = dict(request.data)
        # Supprimer les plats des données car ils ne font pas partie du modèle Menu
        data.pop('plats', None)
        request._full_data = data
        
        # Créer le menu
        response = super().create(request, *args, **kwargs)
        
        try:
            menu_id = response.data.get('id_menu') or response.data.get('id')
            if menu_id:
                menu = Menu.objects.get(id_menu=menu_id)
                
                # Ajouter les plats au menu s'ils ont été fournis
                if plats_data:
                    for plat_id in plats_data:
                        try:
                            plat = Plat.objects.get(id_plat=plat_id)
                            menu.ajouter_plat(plat)
                            logger.info(f"Plat {plat_id} ajouté au menu {menu_id}")
                        except Plat.DoesNotExist:
                            logger.warning(f"Plat avec id {plat_id} non trouvé lors de la création du menu")
                        except Exception as e:
                            logger.error(f"Erreur lors de l'ajout du plat {plat_id} au menu: {e}")
                
                # Notifier N8N en arrière-plan
                headers = self._get_n8n_auth_headers(request)
                print(f"DEBUG: Démarrage thread N8N pour menu {menu_id} avec headers: {headers}")
                thread = threading.Thread(
                    target=self._notify_n8n_menu_creation,
                    args=(menu, headers),
                    daemon=True
                )
                thread.start()
                logger.info(f"Thread N8N créé pour la création du menu {menu_id}")
            else:
                logger.warning("Impossible de récupérer l'id du menu créé pour notifier N8N")
        except Exception as e:
            logger.error(f"Impossible de notifier N8N après création du menu: {e}")
        return response

    def update(self, request, *args, **kwargs):
        """Modifie un menu avec plats et notifie N8N en arrière-plan."""
        # Extraire les plats du payload s'ils existent
        plats_data = request.data.get('plats', None)
        
        # Créer une copie mutable des données pour éviter de modifier request.data
        data = dict(request.data)
        # Supprimer les plats des données car ils ne font pas partie du modèle Menu
        data.pop('plats', None)
        request._full_data = data
        
        # Modifier le menu
        response = super().update(request, *args, **kwargs)
        
        try:
            menu_id = response.data.get('id_menu') or response.data.get('id')
            if menu_id:
                menu = Menu.objects.get(id_menu=menu_id)
                
                # Gérer les plats s'ils ont été fournis
                if plats_data is not None:
                    # Supprimer tous les plats existants
                    menu.plats.clear()
                    
                    # Ajouter les nouveaux plats
                    for plat_id in plats_data:
                        try:
                            plat = Plat.objects.get(id_plat=plat_id)
                            menu.ajouter_plat(plat)
                            logger.info(f"Plat {plat_id} ajouté au menu {menu_id}")
                        except Plat.DoesNotExist:
                            logger.warning(f"Plat avec id {plat_id} non trouvé lors de la modification du menu")
                        except Exception as e:
                            logger.error(f"Erreur lors de l'ajout du plat {plat_id} au menu: {e}")
                
                # Notifier N8N en arrière-plan
                headers = self._get_n8n_auth_headers(request)
                print(f"DEBUG: Démarrage thread N8N pour modification menu {menu_id} avec headers: {headers}")
                thread = threading.Thread(
                    target=self._notify_n8n_menu_modification,
                    args=(menu, headers),
                    daemon=True
                )
                thread.start()
                logger.info(f"Thread N8N créé pour la modification du menu {menu_id}")
            else:
                logger.warning("Impossible de récupérer l'id du menu modifié pour notifier N8N")
        except Exception as e:
            logger.error(f"Impossible de notifier N8N après modification du menu: {e}")
        return response

    def destroy(self, request, *args, **kwargs):
        """
        Supprime un menu en vérifiant d'abord s'il est utilisé dans une commande.
        Notifie N8N en arrière-plan si la suppression est réussie.
        """
        menu = self.get_object()
        menu_id = menu.id_menu
        menu_nom = menu.nom
        
        # Vérifier si le menu est utilisé dans une commande avec statut panier
        est_utilise_dans_commande = LigneCommande.objects.filter(menu=menu, commande__statut='panier').exists()
        
        if est_utilise_dans_commande:
            return Response(
                {
                    'error': 'Ce menu ne peut pas être supprimé',
                    'details': 'ce menu est utilisé dans une ou plusieurs commandes',
                    'menu_id': menu.id_menu,
                    'nom_menu': menu.nom,
                    'est_utilise_dans_commande': est_utilise_dans_commande
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # Si le menu n'est pas utilisé, procéder à la suppression et notifier N8N
        response = super().destroy(request, *args, **kwargs)
        
        try:
            menu_temp = type('obj', (object,), {
                'id_menu': menu_id,
                'nom': menu_nom
            })()
            headers = self._get_n8n_auth_headers(request)
            print(f"DEBUG: Démarrage thread N8N pour suppression menu {menu_id} avec headers: {headers}")
            thread = threading.Thread(
                target=self._notify_n8n_menu_delete,
                args=(menu_temp, headers),
                daemon=True
            )
            thread.start()
            logger.info(f"Thread N8N créé pour la suppression du menu {menu_id}")
        except Exception as e:
            logger.error(f"Impossible de notifier N8N après suppression du menu: {e}")
        
        return response
