from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from django.shortcuts import render

def acceuil(request):

    return render(request, 'menu/menu.html', {})

def acceuil(request):

    return render(request, 'acceuil/acceuil.html', {})
def acceuil(request):

    return render(request, 'specialdiet/specialdiet.html', {})

def acceuil(request):

    return render(request, 'contact/contact.html', {})

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(utilisateur=user)
    
    @action(detail=True, methods=['get'])
    def profil_nutritionnel(self, request, pk=None):
        client = self.get_object()
        try:
            profil = client.profil_nutritionnel
            serializer = ProfilNutritionnelSerializer(profil)
            return Response(serializer.data)
        except ProfilNutritionnel.DoesNotExist:
            return Response({'error': 'Profil nutritionnel non trouvé'}, status=404)
    
    @action(detail=True, methods=['post'])
    def creer_profil(self, request, pk=None):
        client = self.get_object()
        serializer = ProfilNutritionnelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'])
    def historique_commandes(self, request, pk=None):
        client = self.get_object()
        commandes = client.commandes.all().order_by('-date')
        serializer = CommandeSerializer(commandes, many=True)
        return Response(serializer.data)

class PlatViewSet(viewsets.ModelViewSet):
    queryset = Plat.objects.all()
    serializer_class = PlatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Plat.objects.all()
        disponible = self.request.query_params.get('disponible')
        if disponible:
            queryset = queryset.filter(est_disponible=disponible.lower() == 'true')
        return queryset
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        plats = Plat.objects.filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )
        serializer = self.get_serializer(plats, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def score_nutritionnel(self, request, pk=None):
        plat = self.get_object()
        score = plat.calculer_score_nutritionnel()
        return Response({'score': score, 'plat': plat.nom})

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Menu.objects.all()
        actif = self.request.query_params.get('actif')
        if actif:
            queryset = queryset.filter(est_actif=actif.lower() == 'true')
        return queryset
    
    @action(detail=True, methods=['post'])
    def ajouter_plat(self, request, pk=None):
        menu = self.get_object()
        plat_id = request.data.get('plat_id')
        quantite = request.data.get('quantite', 1)
        
        try:
            plat = Plat.objects.get(id=plat_id)
            menu.ajouter_plat(plat, int(quantite))
            serializer = self.get_serializer(menu)
            return Response(serializer.data)
        except Plat.DoesNotExist:
            return Response({'error': 'Plat non trouvé'}, status=404)
    
    @action(detail=True, methods=['delete'])
    def supprimer_plat(self, request, pk=None):
        menu = self.get_object()
        plat_id = request.data.get('plat_id')
        
        try:
            plat = Plat.objects.get(id=plat_id)
            menu.supprimer_plat(plat)
            return Response({'status': 'plat supprimé'})
        except Plat.DoesNotExist:
            return Response({'error': 'Plat non trouvé'}, status=404)
    
    @action(detail=True, methods=['get'])
    def valeur_nutritionnelle(self, request, pk=None):
        menu = self.get_object()
        valeurs = menu.calculer_valeur_nutritionnelle_totale()
        return Response(valeurs)

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Commande.objects.all()
        return Commande.objects.filter(client__utilisateur=user)
    
    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        commande = self.get_object()
        if commande.valider_commande():
            return Response({'status': 'commande validée'})
        return Response({'error': 'La commande ne peut pas être validée'}, status=400)
    
    @action(detail=True, methods=['post'])
    def ajouter_menu(self, request, pk=None):
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
            return Response({'error': 'Menu non trouvé'}, status=404)
    
    @action(detail=True, methods=['post'])
    def calculer_total(self, request, pk=None):
        commande = self.get_object()
        total = commande.calculer_total()
        return Response({'total': str(total)})

class SystemeIAViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemeIA.objects.filter(est_actif=True)
    serializer_class = SystemeIASerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recommandations(self, request):
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response({'error': 'client_id est requis'}, status=400)
        
        try:
            client = Client.objects.get(id=client_id)
            ia_system = SystemeIA.objects.filter(est_actif=True).first()
            
            if ia_system:
                recommandations = ia_system.recommander_menus(client)
                serializer = MenuSerializer(recommandations, many=True)
                return Response(serializer.data)
            else:
                return Response({'error': 'Système IA non disponible'}, status=404)
        except Client.DoesNotExist:
            return Response({'error': 'Client non trouvé'}, status=404)
    
    @action(detail=False, methods=['get'])
    def analyser_preferences(self, request):
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response({'error': 'client_id est requis'}, status=400)
        
        try:
            client = Client.objects.get(id=client_id)
            ia_system = SystemeIA.objects.filter(est_actif=True).first()
            
            if ia_system:
                preferences = ia_system.analyser_preferences(client)
                return Response(preferences)
            return Response({'error': 'Système IA non disponible'}, status=404)
        except Client.DoesNotExist:
            return Response({'error': 'Client non trouvé'}, status=404)