from django.shortcuts import render
from .models import SystemeIA


def index(request):
    """Vue d'index pour le système IA"""
    systemes = SystemeIA.objects.filter(est_actif=True)
    return render(request, 'ai/index.html', {'systemes': systemes})
