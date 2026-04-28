from django.shortcuts import render
from django.conf import settings
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
    """Affiche la page de contact"""
    return render(request, 'contact/contact.html', {})







def administrateur(request):
    """Affiche la page du profil administrateur"""
    return render(request, 'administrateur/administrateur.html', {})


