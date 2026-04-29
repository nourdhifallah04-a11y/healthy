from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage, send_mail
from django.http import JsonResponse
from django.shortcuts import render
import logging


logger = logging.getLogger(__name__)

# ===== Configuration Timeout N8N =====
N8N_WEBHOOK_TIMEOUT = getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 600)  # Default: 120 secondes
N8N_WEBHOOK_URL = getattr(settings, 'N8N_WEBHOOK_URL', 'http://192.168.1.184:5678/webhook/reco-nutrition')

# ===== Async Jobs Cache =====
# Dictionnaire pour stocker les résultats des jobs async
# Clé: job_id, Valeur: {'status': 'pending|completed|failed', 'result': {...}, 'error': {...}, 'timestamp': datetime}
async_jobs_cache = {}



# ===== Template Views =====





def unified_browse(request):
    """Affiche la page de navigation unifiée pour menus et plats"""
    return render(request, 'menu/unified-browse.html', {})





def contact(request):
    """Affiche la page de contact et traite l'envoi de messages"""
    context = {}

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip() or 'Sans sujet'
        message_text = request.POST.get('message', '').strip()

        if not name or len(name) < 2:
            error = 'Veuillez entrer un nom valide d\'au moins 2 caractères.'
        elif not email:
            error = 'Veuillez entrer votre email.'
        elif not message_text or len(message_text) < 10:
            error = 'Veuillez écrire un message d\'au moins 10 caractères.'
        else:
            email_subject = f'Message de contact - {subject}'
            print(f"DEBUG: Préparation de l'email - Sujet: {email_subject}, De: {email}, Nom: {name}")
            print(f"DEBUG: Contenu du message:\n{message_text}")
            print(f"DEBUG: Configuration email - Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}, TLS: {settings.EMAIL_USE_TLS}, User: {settings.EMAIL_HOST_USER}")
            print(f"DEBUG: DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
            email_body = (
                f'Nom: {name}\n'
                f'Email: {email}\n'
                f'Sujet: {subject}\n\n'
                f'Message:\n{message_text}\n'
            )
            from_email = ''
            recipient_list = [from_email]

        try:
            message = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=from_email,
                to=recipient_list,
                reply_to=[email],  # ✔️ accepté ici
            )
            message.send(fail_silently=False)

            success_message = 'Merci ! Votre message a bien été envoyé. Nous vous répondrons dès que possible.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': success_message})
            context['contact_success'] = success_message

        except BadHeaderError:
            error = "Impossible d'envoyer le message pour le moment. Veuillez réessayer."
        except Exception as e:
            logger.exception("Erreur lors de l'envoi du message de contact")
            error = "Une erreur est survenue lors de l'envoi du message. Veuillez réessayer plus tard."

            if request.method == 'POST' and 'error' in locals():
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error}, status=400)
                context['contact_error'] = error

    return render(request, 'contact/contact.html', context)







def administrateur(request):
    """Affiche la page du profil administrateur"""
    return render(request, 'administrateur/administrateur.html', {})


