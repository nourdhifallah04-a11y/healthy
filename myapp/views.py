from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.html import mark_safe
import json
from .models import (
    Client, Plat, Menu, Commande, SystemeIA,
    ProfilNutritionnel, LigneCommande, CompositionMenu, Administrateur, Utilisateur
)
from .serializers import (
    ClientSerializer, PlatSerializer, MenuSerializer, CommandeSerializer,
    ProfilNutritionnelSerializer, SystemeIASerializer
)
from .forms import AdminLoginForm, RegistrationForm


def register(request):
    """
    Vue d'inscription pour créer un nouvel Utilisateur et Client
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Créer l'Utilisateur et le Client
                utilisateur, client = form.save()
                
                # Authentifier et connecter l'utilisateur
                login(request, utilisateur)
                
                messages.success(
                    request, 
                    f"Bienvenue {utilisateur.prenom} {utilisateur.nom}! Votre compte a été créé avec succès."
                )
                return redirect('acceuil')  # Rediriger vers la page d'accueil
            except Exception as e:
                messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Inscription'
    }
    return render(request, 'registration/register.html', context)

@require_http_methods(["GET", "POST"])
def login_admin(request):
    """
    Formulaire de connexion pour les administrateurs.
    Récupère l'administrateur à partir de l'email et de la base de données.
    """
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                # 1. Récupérer l'utilisateur par email depuis la base de données
                utilisateur = Utilisateur.objects.get(email=email)
                
                # 2. Vérifier que le mot de passe est correct
                if utilisateur.check_password(password):
                    # 3. Vérifier si cet utilisateur est un administrateur
                    if hasattr(utilisateur, 'administrateur'):
                        administrateur = Utilisateur.objects.get(email=email)
                        # Authentifier et connecter l'utilisateur
                        login(request, administrateur)
                        messages.success(request, f"Bienvenue {administrateur.prenom} {administrateur.nom}!")
                        return redirect('acceuil')
                    else:
                        messages.error(request, "Vous n'avez pas les droits d'accès administrateur.")
                        form.add_error(None, "Accès refusé : vous n'êtes pas un administrateur.")
                else:
                    messages.error(request, "Mot de passe incorrect.")
                    form.add_error('password', "Le mot de passe est incorrect.")
                    
            except Utilisateur.DoesNotExist:
                messages.error(request, "Aucun utilisateur trouvé avec cet email.")
                form.add_error('email', "Cet email n'existe pas dans la base de données.")
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {str(e)}")
                form.add_error(None, f"Erreur lors de la connexion : {str(e)}")
    else:
        form = AdminLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Connexion Administrateur'
    }
    return render(request, 'administrateur/login_admin.html', context)


# ===== Template Views =====

def acceuil(request):
    """Affiche la page d'accueil"""
    return render(request, 'acceuil/acceuil.html', {})


def menu(request):
    """Affiche la page de menu"""
    return render(request, 'menu/menu.html', {})


def specialdiet(request):
    """Affiche la page des régimes spéciaux avec les plats dynamiques"""
    # Récupérer tous les plats disponibles
    plats = Plat.objects.filter(est_disponible=True).all()
    
    # Organiser les plats par catégorie de régime spécial
    diet_meals = {
        "high-protein": [],
        "low-carb": [],
        "vegan": [],
        "gluten-free": []
    }
    
    for plat in plats:
        # Déterminer les catégories appropriées pour ce plat
        
        # High Protein: protéines > 30g
        if plat.proteine >= 30:
            diet_meals["high-protein"].append({
                'id': plat.id_plat,
                'name': plat.nom,
                'calories': plat.calorie,
                'protein': plat.proteine,
                'carbs': plat.glucides,
                'image': plat.image.url if plat.image else 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500',
                'description': plat.description
            })
        
        # Low Carb: glucides < 20g
        if plat.glucides <= 20:
            diet_meals["low-carb"].append({
                'id': plat.id_plat,
                'name': plat.nom,
                'calories': plat.calorie,
                'protein': plat.proteine,
                'carbs': plat.glucides,
                'image': plat.image.url if plat.image else 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500',
                'description': plat.description
            })
        
        # Vegan: pas de produits d'origine animale (à vérifier dans la description/nom)
        vegan_keywords = ['vegan', 'végétal', 'légume', 'fruit', 'légumineuse', 'tofu', 'pois chiche', 'lentille']
        if any(keyword in plat.nom.lower() or keyword in plat.description.lower() for keyword in vegan_keywords):
            diet_meals["vegan"].append({
                'id': plat.id_plat,
                'name': plat.nom,
                'calories': plat.calorie,
                'protein': plat.proteine,
                'carbs': plat.glucides,
                'image': plat.image.url if plat.image else 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500',
                'description': plat.description
            })
        
        # Gluten-free: pas de gluten (à vérifier)
        gluten_keywords = ['sans gluten', 'riz', 'quinoa', 'patate', 'légume', 'viande', 'poisson']
        if any(keyword in plat.nom.lower() or keyword in plat.description.lower() for keyword in gluten_keywords):
            if 'pâte' not in plat.nom.lower() and 'pain' not in plat.nom.lower() and 'blé' not in plat.nom.lower():
                diet_meals["gluten-free"].append({
                    'id': plat.id_plat,
                    'name': plat.nom,
                    'calories': plat.calorie,
                    'protein': plat.proteine,
                    'carbs': plat.glucides,
                    'image': plat.image.url if plat.image else 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500',
                    'description': plat.description
                })
    
    context = {
        'plats': plats,
        'diet_meals_json': mark_safe(json.dumps(diet_meals))
    }
    return render(request, 'specialdiet/specialdiet.html', context)


def contact(request):
    """Affiche la page de contact"""
    return render(request, 'contact/contact.html', {})

def connex(request):
    """Page de connexion et d'inscription avec les deux formulaires"""
    # Initialiser les formulaires
    login_form = AuthenticationForm()
    register_form = RegistrationForm()
    
    if request.method == 'POST':
        # Vérifier si c'est une soumission d'inscription
        if 'register-submit' in request.POST:
            register_form = RegistrationForm(request.POST)
            
            if register_form.is_valid():
                try:
                    # Créer l'Utilisateur et le Client
                    utilisateur, client = register_form.save()
                    
                    # Authentifier et connecter l'utilisateur
                    login(request, utilisateur)
                    
                    messages.success(
                        request,
                        f"Bienvenue {utilisateur.prenom} {utilisateur.nom}! Votre compte a été créé avec succès."
                    )
                    return redirect('acceuil')
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
                    # Retourner le formulaire avec l'erreur
            # Si le formulaire n'est pas valide, les erreurs s'afficheront dans le template
            login_form = AuthenticationForm()
        else:
            # C'est une soumission de connexion
            login_form = AuthenticationForm(request, data=request.POST)
            
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, f"Bienvenue {user.prenom} {user.nom}!")
                return redirect('acceuil')
            # Si le formulaire n'est pas valide, les erreurs s'afficheront dans le template
            register_form = RegistrationForm()
    
    context = {
        'form': login_form,  # Pour compatibilité avec LoginView et le formulaire de connexion
        'registration_form': register_form,  # Pour le formulaire d'inscription
    }
    return render(request, 'acceuil/connex.html', context)


def profilNutritionnel(request):
    """Affiche la page du profil nutritionnel"""
    return render(request, 'profil_nutritionnel/profilNutritionnel.html', {})

def list_plats(request):
    """Affiche la page des plats"""
    return render(request, 'plats/list_plats.html', {})

def ajouter_plat(request):
    """Affiche la page pour ajouter un nouveau plat"""
    return render(request, 'plats/ajouter_plat.html', {})

def modifier_plat(request):
    """Affiche la page pour modifier un plat"""
    return render(request, 'plats/modifier_plat.html', {})

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


class RecommenderPlatsView(generics.ListAPIView):
    """Vue pour obtenir les plats recommandés basés sur le profil nutritionnel de l'utilisateur"""
    serializer_class = PlatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les plats recommandés basés sur le profil nutritionnel"""
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = ProfilNutritionnel.objects.get(client=client)
            
            # Récupérer les plats recommandés (limite: 10)
            plats_recommandes = profil.recommander_plats(limite=10)
            return plats_recommandes
        except Client.DoesNotExist:
            return Plat.objects.none()
        except ProfilNutritionnel.DoesNotExist:
            # Si pas de profil, retourner les plats disponibles
            return Plat.objects.filter(est_disponible=True)[:10]
    
    def list(self, request, *args, **kwargs):
        """Override pour ajouter les scores aux plats recommandés"""
        try:
            utilisateur = request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = ProfilNutritionnel.objects.get(client=client)
            categorie_imc = profil.determiner_categorie_imc()
            
            # Récupérer les plats avec leurs scores
            plats_disponibles = Plat.objects.filter(est_disponible=True)
            plats_avec_score = []
            
            for plat in plats_disponibles:
                score = Plat.calculer_score_recommendation(
                    plat,
                    categorie_imc,
                    allergies=profil.allergies,
                    restrictions=profil.restrictions_alimentaires
                )
                
                # Ajouter le score au plat sérialisé
                plat_data = PlatSerializer(plat).data
                plat_data['score'] = score
                
                plats_avec_score.append((plat_data, score))
            
            # Trier par score décroissant et garder les plats avec score > 0
            plats_avec_score.sort(key=lambda x: x[1], reverse=True)
            plats_filtres = [p[0] for p in plats_avec_score if p[1] > 0][:10]
            
            return Response(plats_filtres)
        
        except Client.DoesNotExist:
            return Response([])
        except ProfilNutritionnel.DoesNotExist:
            # Si pas de profil, retourner les plats disponibles sans score
            plats = Plat.objects.filter(est_disponible=True)[:10]
            serializer = self.get_serializer(plats, many=True)
            plats_data = serializer.data
            
            # Ajouter un score par défaut pour les plats sans profil
            for plat in plats_data:
                plat['score'] = 0.0
            
            return Response(plats_data)