from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import render
from .models import (
    Client, Plat, Menu, Commande, SystemeIA,
    ProfilNutritionnel, LigneCommande, CompositionMenu
)
from .serializers import (
    ClientSerializer, PlatSerializer, MenuSerializer, CommandeSerializer,
    ProfilNutritionnelSerializer, SystemeIASerializer
)


# ===== Template Views =====

def acceuil(request):
    """Affiche la page d'accueil"""
    return render(request, 'acceuil/acceuil.html', {})


def menu(request):
    """Affiche la page de menu"""
    return render(request, 'menu/menu.html', {})


def specialdiet(request):
    """Affiche la page des régimes spéciaux"""
    return render(request, 'specialdiet/specialdiet.html', {})


def contact(request):
    """Affiche la page de contact"""
    return render(request, 'contact/contact.html', {})

def connex(request):
    """Affiche la page de connexion"""
    return render(request, 'acceuil/connex.html', {})


def profilNutritionnel(request):
    """Affiche la page du profil nutritionnel"""
    return render(request, 'profil_nutritionnel/profilNutritionnel.html', {})

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
            profil = client.profil_nutritionnel
            serializer = ProfilNutritionnelSerializer(profil)
            return Response(serializer.data)
        except ProfilNutritionnel.DoesNotExist:
            return Response(
                {'error': 'Profil nutritionnel non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def creer_profil(self, request, pk=None):
        """Crée ou met à jour le profil nutritionnel d'un client"""
        client = self.get_object()
        serializer = ProfilNutritionnelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def historique_commandes(self, request, pk=None):
        """Récupère l'historique des commandes d'un client"""
        client = self.get_object()
        commandes = client.commandes.all().order_by('-date')
        serializer = CommandeSerializer(commandes, many=True)
        return Response(serializer.data)

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
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche les plats par nom ou description"""
        query = request.query_params.get('q', '')
        plats = Plat.objects.filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )
        serializer = self.get_serializer(plats, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def score_nutritionnel(self, request, pk=None):
        """Récupère le score nutritionnel d'un plat"""
        plat = self.get_object()
        score = plat.calculer_score_nutritionnel()
        return Response({'score': score, 'plat': plat.nom})

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
    
    @action(detail=True, methods=['post'])
    def ajouter_plat(self, request, pk=None):
        """Ajoute un plat à un menu"""
        menu = self.get_object()
        plat_id = request.data.get('plat_id')
        quantite = request.data.get('quantite', 1)
        
        try:
            plat = Plat.objects.get(id=plat_id)
            menu.ajouter_plat(plat, int(quantite))
            serializer = self.get_serializer(menu)
            return Response(serializer.data)
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
        
        try:
            plat = Plat.objects.get(id=plat_id)
            menu.supprimer_plat(plat)
            return Response({'status': 'plat supprimé'})
        except Plat.DoesNotExist:
            return Response(
                {'error': 'Plat non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def valeur_nutritionnelle(self, request, pk=None):
        """Calcule les valeurs nutritionnelles totales d'un menu"""
        menu = self.get_object()
        valeurs = menu.calculer_valeur_nutritionnelle_totale()
        return Response(valeurs)

class CommandeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commandes.
    Permet de créer, consulter, valider et gérer les articles des commandes.
    """
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Les utilisateurs voient uniquement leurs commandes, sauf s'ils sont admin"""
        user = self.request.user
        if user.is_superuser:
            return Commande.objects.all()
        return Commande.objects.filter(client__utilisateur=user)
    
    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Valide une commande (passe du statut panier à confirmée)"""
        commande = self.get_object()
        if commande.valider_commande():
            return Response({'status': 'commande validée'})
        return Response(
            {'error': 'La commande ne peut pas être validée'},
            status=status.HTTP_400_BAD_REQUEST
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
        total = commande.calculer_total()
        return Response({'total': str(total)})


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
            
            if ia_system:
                recommandations = ia_system.recommander_menus(client)
                serializer = MenuSerializer(recommandations, many=True)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'Système IA non disponible'},
                    status=status.HTTP_404_NOT_FOUND
                )
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
            
            if ia_system:
                preferences = ia_system.analyser_preferences(client)
                return Response(preferences)
            return Response(
                {'error': 'Système IA non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )


# ===== Profile Views =====

class CreerProfilNutritionnelView(generics.CreateAPIView):
    """Vue API pour créer un profil nutritionnel pour l'utilisateur courant"""
    serializer_class = ProfilNutritionnelSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Crée ou met à jour le profil nutritionnel de l'utilisateur connecté"""
        try:
            # Récupérer le client de l'utilisateur courant
            utilisateur = request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Ajouter le client aux données
            data = request.data.copy()
            data['client'] = client.id
            
            # Créer ou mettre à jour le profil
            try:
                profil = ProfilNutritionnel.objects.get(client=client)
                serializer = self.get_serializer(profil, data=data, partial=True)
            except ProfilNutritionnel.DoesNotExist:
                serializer = self.get_serializer(data=data)
            
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response({
                'success': True,
                'message': 'Profil nutritionnel créé avec succès',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Client.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Client non trouvé pour cet utilisateur'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        serializer.save()


class ObtenirProfilNutritionnelView(generics.RetrieveAPIView):
    """Vue pour récupérer le profil nutritionnel de l'utilisateur courant"""
    serializer_class = ProfilNutritionnelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = ProfilNutritionnel.objects.get(client=client)
            return profil
        except Client.DoesNotExist:
            raise generics.NotFound('Client non trouvé pour cet utilisateur')
        except ProfilNutritionnel.DoesNotExist:
            raise generics.NotFound('Profil nutritionnel non trouvé')


class SupprimerProfilNutritionnelView(generics.DestroyAPIView):
    """Vue pour supprimer le profil nutritionnel de l'utilisateur courant"""
    serializer_class = ProfilNutritionnelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = ProfilNutritionnel.objects.get(client=client)
            return profil
        except Client.DoesNotExist:
            raise generics.NotFound('Client non trouvé pour cet utilisateur')
        except ProfilNutritionnel.DoesNotExist:
            raise generics.NotFound('Profil nutritionnel non trouvé')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Profil nutritionnel supprimé avec succès'
        }, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        instance.delete()