from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage, send_mail
from django.http import JsonResponse
from django.shortcuts import render
import logging


logger = logging.getLogger(__name__)

# ===== Configuration Timeout N8N =====
N8N_WEBHOOK_TIMEOUT = getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 600)  # Default: 120 secondes
N8N_WEBHOOK_URL_RECO_NUTRITION = getattr(settings, 'N8N_WEBHOOK_URL_RECO_NUTRITION', 'http://192.168.1.184:5678/webhook/reco-nutrition')

# ===== Async Jobs Cache =====
# Dictionnaire pour stocker les résultats des jobs async
# Clé: job_id, Valeur: {'status': 'pending|completed|failed', 'result': {...}, 'error': {...}, 'timestamp': datetime}
async_jobs_cache = {}



# ===== Template Views =====



def administrateur(request):
    """Affiche la page du profil administrateur"""
    return render(request, 'administrateur/administrateur.html', {})


