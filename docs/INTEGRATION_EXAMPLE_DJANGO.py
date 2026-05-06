#!/usr/bin/env python
"""
EXAMPLE: Intégration Python/Django avec la refonte UX Nutriments

Ce fichier montre comment intégrer la nouvelle visualisation des nutriments
dans votre backend Django.
"""

from django.template.loader import render_to_string
from django.http import JsonResponse
import json


# ==============================================================================
# 1. VUE DJANGO - Exposer les données menus en JSON
# ==============================================================================

def get_comparison_data(request):
    """
    Endpoint API pour récupérer les données nutritionnelles des menus
    
    GET /api/menus/comparison/?ids=21,22,23
    
    Response:
    {
        "success": true,
        "menus": [
            {
                "id": "21",
                "name": "Menu automatique 21",
                "calories": 520,
                "proteins": 28,
                "carbs": 65,
                "fats": 12
            },
            ...
        ]
    }
    """
    menu_ids = request.GET.get('ids', '').split(',')
    
    # Récupérer depuis votre modèle Django
    from myapp.models import Menu  # À adapter à votre structure
    
    menus = Menu.objects.filter(id__in=menu_ids).values(
        'id',
        'name',
        'calories',
        'proteins',
        'carbs',
        'fats'
    )
    
    return JsonResponse({
        'success': True,
        'menus': list(menus)
    })


# ==============================================================================
# 2. CONTEXT PROCESSOR - Ajouter styles CSS
# ==============================================================================

def comparison_context(request):
    """
    Context processor pour ajouter les fichiers CSS/JS nécessaires
    """
    return {
        'comparison_css': [
            'menu/compare-modal-refactored.css',
            'menu/nutrients-visualization.css',
        ],
        'comparison_js': [
            'menu/nutrients-visualization-integration.js',
        ]
    }


# ==============================================================================
# 3. TEMPLATE TAG - Simplifier l'inclusion du modal
# ==============================================================================

from django import template

register = template.Library()


@register.inclusion_tag('menu/comparison_modal_tag.html')
def comparison_modal():
    """
    Template tag pour inclure le modal de comparaison
    
    Utilisation dans template:
    {% load menu_tags %}
    {% comparison_modal %}
    """
    return {
        'nutrients': [
            {'key': 'calories', 'icon': '🔥', 'label': 'Calories', 'unit': 'kcal'},
            {'key': 'proteins', 'icon': '💪', 'label': 'Protéines', 'unit': 'g'},
            {'key': 'carbs', 'icon': '🌾', 'label': 'Glucides', 'unit': 'g'},
            {'key': 'fats', 'icon': '🧈', 'label': 'Lipides', 'unit': 'g'},
        ]
    }


# ==============================================================================
# 4. JAVASCRIPT HELPER - Initialiser la comparaison
# ==============================================================================

"""
Dans votre fichier JavaScript existant (menu-comparison.js):

class MenuComparison {
    constructor(options = {}) {
        this.menuIds = options.menuIds || [];
        this.apiUrl = options.apiUrl || '/api/menus/comparison/';
        this.init();
    }
    
    async init() {
        // Charger les données
        const data = await this.fetchMenuData();
        
        // Initialiser les graphiques
        NutrientVisualization.initializeNutrientCharts(data.menus);
        
        // Ajouter listeners
        this.attachEventListeners();
    }
    
    async fetchMenuData() {
        const params = new URLSearchParams({ ids: this.menuIds.join(',') });
        const response = await fetch(`${this.apiUrl}?${params}`);
        return response.json();
    }
    
    attachEventListeners() {
        // Gestion hover sur les barres
        document.querySelectorAll('.chart-bar-fill').forEach(bar => {
            bar.addEventListener('mouseenter', (e) => {
                console.log('Hover bar:', e.target);
                // Log analytics, etc.
            });
        });
    }
}

// Utilisation
const comparison = new MenuComparison({
    menuIds: ['21', '22', '23'],
    apiUrl: '/api/menus/comparison/'
});
"""


# ==============================================================================
# 5. MODEL DJANGO - Structure de données
# ==============================================================================

"""
Dans votre models.py:

from django.db import models

class Menu(models.Model):
    NUTRIMENT_FIELDS = ['calories', 'proteins', 'carbs', 'fats']
    
    name = models.CharField(max_length=200)
    calories = models.IntegerField(default=0)
    proteins = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)
    
    def get_nutriment_dict(self):
        '''Retourner tous les nutriments en dict'''
        return {
            'id': str(self.id),
            'name': self.name,
            **{field: getattr(self, field) for field in self.NUTRIMENT_FIELDS}
        }
    
    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
"""


# ==============================================================================
# 6. TEMPLATE HTML - Inclure les ressources
# ==============================================================================

"""
Dans votre template menu/menu_comparison.html:

{% extends 'base.html' %}
{% load static %}
{% load menu_tags %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'menu/compare-modal-refactored.css' %}">
    <link rel="stylesheet" href="{% static 'menu/nutrients-visualization.css' %}">
{% endblock %}

{% block content %}
    <h1>Comparateur de Menus</h1>
    
    {% comparison_modal %}
{% endblock %}

{% block extra_js %}
    <script src="{% static 'menu/nutrients-visualization-integration.js' %}"></script>
    <script src="{% static 'menu/menu-comparison.js' %}"></script>
    
    <script>
        // Initialiser la comparaison au chargement
        document.addEventListener('DOMContentLoaded', function() {
            const comparison = new MenuComparison({
                menuIds: {{ menu_ids|safe }},
                apiUrl: '/api/menus/comparison/'
            });
        });
    </script>
{% endblock %}
"""


# ==============================================================================
# 7. TEST UNITAIRE - Valider les données
# ==============================================================================

"""
Dans tests/test_menu_comparison.py:

from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import Menu


class MenuComparisonTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        # Créer menus de test
        self.menu1 = Menu.objects.create(
            name='Menu Test 1',
            calories=520,
            proteins=28,
            carbs=65,
            fats=12
        )
        self.menu2 = Menu.objects.create(
            name='Menu Test 2',
            calories=480,
            proteins=35,
            carbs=52,
            fats=14
        )
    
    def test_comparison_api_returns_valid_json(self):
        '''API retourne JSON valide avec bonne structure'''
        response = self.client.get(
            reverse('menu_comparison'),
            {'ids': f'{self.menu1.id},{self.menu2.id}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['menus']), 2)
    
    def test_comparison_data_has_required_fields(self):
        '''Les données retournées ont tous les nutriments'''
        response = self.client.get(
            reverse('menu_comparison'),
            {'ids': self.menu1.id}
        )
        menu_data = response.json()['menus'][0]
        required_fields = ['id', 'name', 'calories', 'proteins', 'carbs', 'fats']
        for field in required_fields:
            self.assertIn(field, menu_data)
    
    def test_nutrient_values_are_numbers(self):
        '''Les valeurs nutritionnelles sont des nombres'''
        response = self.client.get(
            reverse('menu_comparison'),
            {'ids': self.menu1.id}
        )
        menu_data = response.json()['menus'][0]
        self.assertIsInstance(menu_data['calories'], (int, float))
        self.assertIsInstance(menu_data['proteins'], (int, float))
"""


# ==============================================================================
# 8. URL CONFIGURATION
# ==============================================================================

"""
Dans urls.py:

from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # API
    path('api/comparison/', views.get_comparison_data, name='comparison_api'),
    
    # Pages
    path('compare/', views.comparison_view, name='comparison'),
]
"""


# ==============================================================================
# 9. INTÉGRATION AVEC PAGINATION
# ==============================================================================

def get_paginated_menus_for_comparison(request):
    """
    Si vous avez beaucoup de menus, paginez-les
    """
    from django.core.paginator import Paginator
    from myapp.models import Menu
    
    page = request.GET.get('page', 1)
    per_page = 20
    
    all_menus = Menu.objects.all()
    paginator = Paginator(all_menus, per_page)
    page_menus = paginator.get_page(page)
    
    return JsonResponse({
        'success': True,
        'menus': [menu.get_nutriment_dict() for menu in page_menus],
        'total_pages': paginator.num_pages,
        'current_page': page,
        'total_count': paginator.count
    })


# ==============================================================================
# 10. EXPORT PDF - BONUS
# ==============================================================================

def export_comparison_as_pdf(request):
    """
    Exporter la comparaison en PDF (avec reportlab)
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    menu_ids = request.GET.get('ids', '').split(',')
    
    # Créer PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "Comparaison Nutritionnelle")
    
    # Ajouter data...
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='comparison.pdf')


# ==============================================================================
# CHECKLIST D'INTÉGRATION
# ==============================================================================

"""
✅ Intégration Django complète

1. Backend
   [ ] Ajouter endpoint API pour récupérer menus
   [ ] Structurer données JSON (id, name, calories, proteins, carbs, fats)
   [ ] Tester API avec Postman/curl
   
2. Frontend
   [ ] Charger CSS: compare-modal-refactored.css
   [ ] Charger CSS: nutrients-visualization.css
   [ ] Charger JS: nutrients-visualization-integration.js
   
3. Initialisation
   [ ] Appeler NutrientVisualization.initializeNutrientCharts(menus)
   [ ] Passer structure: [{id, name, calories, proteins, carbs, fats}]
   
4. Tests
   [ ] Vérifier les barres s'affichent
   [ ] Vérifier les valeurs sont correctes
   [ ] Tester hover effect
   [ ] Tester responsive mobile
   
5. Analytics (optionnel)
   [ ] Logger quels nutriments sont comparés
   [ ] Tracker navigation clavier
   [ ] Monitor performance (animations 60fps)

6. Production
   [ ] Minifier CSS/JS
   [ ] Ajouter cache headers
   [ ] Tester sur navigateurs réels
"""


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   NUTRIENTS VISUALIZATION - Django Integration Example     ║
    ║                                                            ║
    ║   Fichier de référence pour intégrer la nouvelle UX       ║
    ║   Copier les patterns pertinents dans votre code          ║
    ║                                                            ║
    ║   Documentation: docs/UX_REFACTORING_NUTRIENTS_VISUALIZATION.md
    ╚════════════════════════════════════════════════════════════╝
    """)
