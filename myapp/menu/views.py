from myapp.commande.models import LigneCommande
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
import logging
from myapp.plat.models import Plat
from myapp.menu.models import Menu
from myapp.menu.serializers import MenuSerializer

logger = logging.getLogger(__name__)

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
