"""
Vues du dashboard de monitoring des scores nutritionnels.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods

from .score_monitoring import score_monitor


@staff_member_required
@require_GET
def score_dashboard(request):
    """Page HTML du dashboard (réservée au staff)."""
    client_id_str = request.GET.get("client_id")
    client_id = int(client_id_str) if client_id_str else None
    return render(request, "monitoring/score_dashboard.html", {
        "stats": score_monitor.get_stats(),
        "alerts": score_monitor.get_alerts(limit=30, client_id=client_id),
        "client_id": client_id,
    })


@staff_member_required
@require_GET
def score_dashboard_api(request):
    """Endpoint JSON pour rafraîchissement AJAX avec filtrage avancé."""
    score_type = request.GET.get("type")
    client_id_str = request.GET.get("client_id")
    plat_id_str = request.GET.get("plat_id")
    level = request.GET.get("level")
    limit = int(request.GET.get("limit", 50))
    
    # Parser les filtres numériques
    def parse_float(value):
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    
    client_id = int(client_id_str) if client_id_str else None
    plat_id = int(plat_id_str) if plat_id_str else None
    
    # Filtres nutritionnels (range-based)
    calorie_min = parse_float(request.GET.get("calorie_min"))
    calorie_max = parse_float(request.GET.get("calorie_max"))
    proteines_min = parse_float(request.GET.get("proteines_min"))
    proteines_max = parse_float(request.GET.get("proteines_max"))
    glucides_min = parse_float(request.GET.get("glucides_min"))
    glucides_max = parse_float(request.GET.get("glucides_max"))
    lipides_min = parse_float(request.GET.get("lipides_min"))
    lipides_max = parse_float(request.GET.get("lipides_max"))
    fibres_min = parse_float(request.GET.get("fibres_min"))
    fibres_max = parse_float(request.GET.get("fibres_max"))
    imc_min = parse_float(request.GET.get("imc_min"))
    imc_max = parse_float(request.GET.get("imc_max"))
    
    return JsonResponse({
        "stats": score_monitor.get_stats(score_type) if score_type else score_monitor.get_stats(),
        "alerts": score_monitor.get_alerts(
            level=level,
            limit=limit,
            client_id=client_id,
            plat_id=plat_id,
            calorie_min=calorie_min,
            calorie_max=calorie_max,
            proteines_min=proteines_min,
            proteines_max=proteines_max,
            glucides_min=glucides_min,
            glucides_max=glucides_max,
            lipides_min=lipides_min,
            lipides_max=lipides_max,
            fibres_min=fibres_min,
            fibres_max=fibres_max,
            imc_min=imc_min,
            imc_max=imc_max,
        ),
        "recent": (
            score_monitor.get_recent_records(score_type, limit=50, client_id=client_id)
            if score_type else None
        ),
    })


@staff_member_required
@require_GET
def score_dashboard_filters_data(request):
    """Endpoint pour récupérer les données disponibles pour les filtres (clients, plats, plages).
    
    Returns:
        JSON avec:
        - clients: Liste des clients uniques avec leurs alertes
        - plats: Liste des plats uniques avec leurs alertes
        - nutritional_ranges: Plages min/max pour tous les nutriments
    """
    from .models import Client, Plat, Utilisateur
    
    # Récupérer toutes les alertes pour extraire les données disponibles
    alerts = score_monitor.get_alerts(limit=500)
    
    # Extraire clients uniques
    unique_clients = {}
    for alert in alerts:
        client_id = alert.get('client_id')
        if client_id and client_id not in unique_clients:
            try:
                user = Utilisateur.objects.get(id=client_id)
                unique_clients[client_id] = f"{user.nom} {user.prenom} (ID: {client_id})"
            except:
                unique_clients[client_id] = f"Client ID: {client_id}"
    
    # Extraire plats uniques
    unique_plats = {}
    for alert in alerts:
        plat_id = alert.get('plat_id')
        if plat_id and plat_id not in unique_plats:
            plat_name = alert.get('context', {}).get('plat', {}).get('nom', f'Plat ID: {plat_id}')
            unique_plats[plat_id] = plat_name
    
    # Calculer les plages nutritionnelles de tous les plats
    try:
        all_plats = Plat.objects.all()
        if all_plats.exists():
            calories = [p.calorie for p in all_plats if p.calorie]
            proteines = [p.proteine for p in all_plats if p.proteine]
            glucides = [p.glucides for p in all_plats if p.glucides]
            lipides = [p.lipides for p in all_plats if p.lipides]
            fibres = [p.fibres for p in all_plats if p.fibres]
            
            nutritional_ranges = {
                'calories': {'min': min(calories) if calories else 0, 'max': max(calories) if calories else 0},
                'proteines': {'min': min(proteines) if proteines else 0, 'max': max(proteines) if proteines else 0},
                'glucides': {'min': min(glucides) if glucides else 0, 'max': max(glucides) if glucides else 0},
                'lipides': {'min': min(lipides) if lipides else 0, 'max': max(lipides) if lipides else 0},
                'fibres': {'min': min(fibres) if fibres else 0, 'max': max(fibres) if fibres else 0},
            }
        else:
            nutritional_ranges = {
                'calories': {'min': 0, 'max': 0},
                'proteines': {'min': 0, 'max': 0},
                'glucides': {'min': 0, 'max': 0},
                'lipides': {'min': 0, 'max': 0},
                'fibres': {'min': 0, 'max': 0},
            }
    except Exception as e:
        nutritional_ranges = {
            'calories': {'min': 0, 'max': 0},
            'proteines': {'min': 0, 'max': 0},
            'glucides': {'min': 0, 'max': 0},
            'lipides': {'min': 0, 'max': 0},
            'fibres': {'min': 0, 'max': 0},
        }
    
    return JsonResponse({
        "clients": unique_clients,
        "plats": unique_plats,
        "nutritional_ranges": nutritional_ranges,
    })
def score_dashboard_reset(request):
    """Réinitialise les compteurs (POST uniquement)."""
    score_type = request.POST.get("type")
    score_monitor.reset(score_type)
    return JsonResponse({"ok": True, "reset": score_type or "all"})

