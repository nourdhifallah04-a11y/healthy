from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.html import mark_safe
from django.conf import settings
import json
from .models import (
    Client, Plat, Menu, Commande, SystemeIA,
    ProfilNutritionnel, LigneCommande, Administrateur, Utilisateur
)
from .serializers import (
    ClientSerializer, PlatSerializer, MenuSerializer, CommandeSerializer,
    ProfilNutritionnelSerializer, SystemeIASerializer, LigneCommandeSerializer,
    UnifiedMenuItemSerializer
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
                return redirect('accueil')  # Rediriger vers la page d'accueil
            except ValueError as e:
                messages.error(request, f"Erreur de validation: {str(e)}")
            except Exception as e:
                messages.error(request, "Une erreur est survenue lors de l'inscription.")
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
                if not utilisateur.check_password(password):
                    messages.error(request, "Mot de passe incorrect.")
                    form.add_error('password', "Le mot de passe est incorrect.")
                    return render(request, 'administrateur/login_admin.html', {'form': form, 'page_title': 'Connexion Administrateur'})
                
                # 3. Vérifier si cet utilisateur est un administrateur
                if not Administrateur.objects.filter(utilisateur=utilisateur).exists():
                    messages.error(request, "Vous n'avez pas les droits d'accès administrateur.")
                    form.add_error(None, "Accès refusé : vous n'êtes pas un administrateur.")
                    return render(request, 'administrateur/login_admin.html', {'form': form, 'page_title': 'Connexion Administrateur'})
                
                # Authentifier et connecter l'utilisateur
                login(request, utilisateur)
                messages.success(request, f"Bienvenue {utilisateur.prenom} {utilisateur.nom}!")
                return redirect('accueil')
                    
            except Utilisateur.DoesNotExist:
                messages.error(request, "Aucun utilisateur trouvé avec cet email.")
                form.add_error('email', "Cet email n'existe pas dans la base de données.")
            except Exception as e:
                messages.error(request, "Une erreur est survenue lors de la connexion.")
                form.add_error(None, f"Erreur: {type(e).__name__}")
    else:
        form = AdminLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Connexion Administrateur'
    }
    return render(request, 'administrateur/login_admin.html', context)


# ===== Template Views =====

def accueil(request):
    """Affiche la page d'accueil"""
    return render(request, 'accueil/accueil.html', {})


def menu(request):
    """Affiche la page de menu"""
    return render(request, 'menu/menu.html', {})


def unified_browse(request):
    """Affiche la page de navigation unifiée pour menus et plats"""
    return render(request, 'menu/unified-browse.html', {})


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
                    return redirect('accueil')
                except ValueError as e:
                    messages.error(request, f"Erreur de validation: {str(e)}")
                except Exception as e:
                    messages.error(request, "Une erreur est survenue lors de l'inscription.")
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
                return redirect('accueil')
            # Si le formulaire n'est pas valide, les erreurs s'afficheront dans le template
            register_form = RegistrationForm()
    
    context = {
        'form': login_form,  # Pour compatibilité avec LoginView et le formulaire de connexion
        'registration_form': register_form,  # Pour le formulaire d'inscription
    }
    return render(request, 'accueil/connex.html', context)


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
    """Vue pour obtenir les menus recommandés basés sur le profil nutritionnel de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    
    # Configuration des limites de recommandation
    MAX_RECOMMENDATIONS = 100
    
    def get_serializer_class(self):
        """Retourne le serializer approprié"""
        from .serializers import MenuRecommandationSerializer
        return MenuRecommandationSerializer
    
    def _calculer_score_menu(self, menu, client):
        """Calcule le score pour un menu basé sur le profil du client"""
        try:
            profil = client.profil_nutritionnel
            preferences = SystemeIA.objects.first().analyser_preferences(client) if SystemeIA.objects.first() else {}
            
            valeurs = menu.calculer_valeur_nutritionnelle_totale()
            score = 0
            
            # Score basé sur l'objectif nutritionnel
            if profil.objectif == 'perte_poids' and valeurs['calories'] < 600:
                score += 30
            elif profil.objectif == 'prise_muscle' and valeurs['proteines'] > 30:
                score += 30
            elif profil.objectif == 'performance' and valeurs['calories'] > 700:
                score += 30
                
            # Score basé sur les préférences historiques
            if preferences.get('preferences'):
                if valeurs['calories'] < 400 and preferences['preferences'].get('leger', 0) > 0:
                    score += 20
                elif valeurs['calories'] > 700 and preferences['preferences'].get('energetique', 0) > 0:
                    score += 20
                    
            # Score nutritionnel
            score_nutritionnel = (valeurs['proteines'] * 2 - valeurs['lipides']) / 100 if valeurs.get('proteines') else 0
            score += max(0, min(20, score_nutritionnel))
            
            return round(score, 2)
        except Exception:
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