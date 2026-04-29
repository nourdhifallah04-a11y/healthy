from myapp.commande.models import Commande, LigneCommande
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import logging
from myapp.users.models import Client
from myapp.plat.models import Plat
from myapp.menu.models import Menu


logger = logging.getLogger(__name__)


from myapp.commande.serializers import CommandeSerializer, LigneCommandeSerializer



# ===== API ViewSets =====
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


@login_required
def historique_commandes(request):
    """
    Affiche l'historique complet des commandes (Admin uniquement)
    """
    # Vérifier que l'utilisateur est administrateur
    if not request.user.administrateur:
        messages.error(request, "Vous n'avez pas accès à cette page")
        return redirect('accueil')
    
    # Récupérer les paramètres de filtrage
    statut_filtre = request.GET.get('statut', '')
    client_filtre = request.GET.get('client', '')
    page_num = request.GET.get('page', 1)
    
    # Requête de base
    commandes = Commande.objects.select_related('client__utilisateur').order_by('-date')
    
    # Appliquer les filtres
    if statut_filtre:
        commandes = commandes.filter(statut=statut_filtre)
    
    if client_filtre:
        commandes = commandes.filter(
            client__utilisateur__nom__icontains=client_filtre
        ) | commandes.filter(
            client__utilisateur__prenom__icontains=client_filtre
        )
    
    # Pagination
    paginator = Paginator(commandes, 20)
    page = paginator.get_page(page_num)
    
    # Obtenir les statuts disponibles pour le filtre
    statuts = Commande.STATUTS
    
    # Calculer les statistiques
    total_commandes = Commande.objects.count()
    total_revenus = sum(cmd.total for cmd in Commande.objects.all())
    commandes_confirmees = Commande.objects.filter(statut='confirmee').count()
    commandes_livrees = Commande.objects.filter(statut='livree').count()
    
    context = {
        'page': page,
        'paginator': paginator,
        'statuts': statuts,
        'statut_filtre': statut_filtre,
        'client_filtre': client_filtre,
        'total_commandes': total_commandes,
        'total_revenus': total_revenus,
        'commandes_confirmees': commandes_confirmees,
        'commandes_livrees': commandes_livrees,
    }
    return render(request, 'commande/historique_commandes.html', context)


@login_required
def admin_commande_detail(request, commande_id):
    """
    Affiche les détails d'une commande avec options de gestion (Admin uniquement)
    """
    # Vérifier que l'utilisateur est administrateur
    if not request.user.administrateur:
        messages.error(request, "Vous n'avez pas accès à cette page")
        return redirect('accueil')
    
    try:
        commande = Commande.objects.select_related('client__utilisateur').get(
            id_commande=commande_id
        )
    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée")
        return redirect('historique_commandes')
    
    # Traiter les mises à jour de statut
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        if nouveau_statut and nouveau_statut in dict(Commande.STATUTS):
            commande.statut = nouveau_statut
            commande.save()
            messages.success(request, f"Statut changé en {commande.get_statut_display()}")
            return redirect('admin_commande_detail', commande_id=commande_id)
    
    # Récupérer toutes les lignes de commande avec leurs détails nutritionnels
    lignes = commande.lignecommande_set.all()
    
    # Calculer les valeurs nutritionnelles totales
    nutrition_totale = commande.calculer_nutrition_totale()
    
    # Statuts disponibles
    statuts_disponibles = Commande.STATUTS
    
    # Compter les autres commandes du client
    autres_commandes = commande.client.commandes.exclude(
        id_commande=commande_id
    ).count()
    
    context = {
        'commande': commande,
        'lignes': lignes,
        'nutrition_totale': nutrition_totale,
        'statuts_disponibles': statuts_disponibles,
        'autres_commandes': autres_commandes,
    }
    return render(request, 'commande/admin_commande_detail.html', context)

