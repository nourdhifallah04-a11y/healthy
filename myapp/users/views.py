from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
import logging
from django.contrib.auth.forms import AuthenticationForm
from myapp.commande.models import Commande
from myapp.commande.serializers import CommandeSerializer
from myapp.profilNutritionnel.models import ProfilNutritionnel
from myapp.profilNutritionnel.serializers import ProfilNutritionnelSerializer
from myapp.users.forms import AdminLoginForm, RegistrationForm
from myapp.users.models import Client, Utilisateur, Administrateur
from myapp.users.serializers import ClientSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# ===== Configuration Timeout N8N =====
N8N_WEBHOOK_TIMEOUT = getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 600)  # Default: 120 secondes
N8N_WEBHOOK_URL = getattr(settings, 'N8N_WEBHOOK_URL', 'http://192.168.1.184:5678/webhook/reco-nutrition')

# ===== Async Jobs Cache =====
# Dictionnaire pour stocker les résultats des jobs async
# Clé: job_id, Valeur: {'status': 'pending|completed|failed', 'result': {...}, 'error': {...}, 'timestamp': datetime}
async_jobs_cache = {}

def _send_activation_email(request, utilisateur):
    """Envoie un e-mail d'activation au nouvel utilisateur."""
    try:
        uidb64 = urlsafe_base64_encode(force_bytes(utilisateur.pk))
        token = default_token_generator.make_token(utilisateur)
        activation_url = request.build_absolute_uri(
            reverse('activate_account', kwargs={'uidb64': uidb64, 'token': token})
        )
        subject = 'Activez votre compte Healthy IA'
        context = {
            'utilisateur': utilisateur,
            'activation_url': activation_url,
        }
        message = render_to_string('registration/activation_email.txt', context)
        html_message = render_to_string('registration/activation_email.html', context)

        result = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [utilisateur.email],
            html_message=html_message,
        )
        
        if result == 0:
            logger.warning(f"Email d'activation non envoyé pour {utilisateur.email}. Backend: {settings.EMAIL_BACKEND}")
            if settings.DEBUG:
                logger.info("En développement (DEBUG=True), consultez la console pour voir le contenu de l'email")
        else:
            logger.info(f"Email d'activation envoyé avec succès à {utilisateur.email}")
            
    except BadHeaderError as e:
        logger.error(f"BadHeaderError lors de l'envoi du mail: {e}")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email d'activation: {e}", exc_info=True)
        raise


def activate_account(request, uidb64, token):
    """Active le compte à partir du lien d'activation."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        utilisateur = Utilisateur.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
        utilisateur = None

    if utilisateur is not None and default_token_generator.check_token(utilisateur, token):
        utilisateur.is_active = True
        utilisateur.est_actif = True
        utilisateur.save()
        messages.success(request, 'Votre compte a bien été activé. Vous pouvez maintenant vous connecter.')
        return redirect('login')

    messages.error(request, 'Le lien d\'activation est invalide ou a expiré.')
    return redirect('login')


def accueil(request):
    """Affiche la page d'accueil"""
    context = {}
    
    # Ajouter le profil nutritionnel au contexte si l'utilisateur est authentifié
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(utilisateur=request.user)
            profil = ProfilNutritionnel.objects.get(client=client)
            context['profil_nutritionnel'] = profil
        except (Client.DoesNotExist, ProfilNutritionnel.DoesNotExist):
            pass
    
    return render(request, 'accueil/accueil.html', context)

def profilNutritionnel(request):
    """Affiche la page du profil nutritionnel"""
    return render(request, 'profil_nutritionnel/profilNutritionnel.html', {})

def register(request):
    """
    Vue d'inscription pour créer un nouvel Utilisateur et Client
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                utilisateur, client = form.save()
                _send_activation_email(request, utilisateur)
                messages.success(
                    request,
                    f"Merci {utilisateur.prenom} {utilisateur.nom}. Un e-mail d'activation a été envoyé à {utilisateur.email}."
                )
                return redirect('login')
            except ValueError as e:
                messages.error(request, f"Erreur de validation: {str(e)}")
            except BadHeaderError:
                messages.error(request, "Erreur lors de l'envoi du message. Veuillez réessayer plus tard.")
            except Exception as e:
                logger.exception("Erreur lors de l'inscription ou de l'envoi de l'email d'activation")
                messages.error(request, "Une erreur est survenue lors de l'inscription. Veuillez réessayer plus tard.")
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
                return redirect('menu')
                    
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
                    utilisateur, client = register_form.save()
                    _send_activation_email(request, utilisateur)
                    messages.success(
                        request,
                        f"Merci {utilisateur.prenom} {utilisateur.nom}. Un e-mail d'activation a été envoyé à {utilisateur.email}."
                    )
                    return redirect('login')
                except ValueError as e:
                    messages.error(request, f"Erreur de validation: {str(e)}")
                except BadHeaderError:
                    messages.error(request, "Erreur lors de l'envoi du message. Veuillez réessayer plus tard.")
                except Exception as e:
                    logger.exception("Erreur lors de l'inscription ou de l'envoi de l'email d'activation")
                    messages.error(request, "Une erreur est survenue lors de l'inscription. Veuillez réessayer plus tard.")
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
