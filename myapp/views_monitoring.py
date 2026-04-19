"""
Vues du dashboard de monitoring des scores nutritionnels.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .score_monitoring import score_monitor


@staff_member_required
@require_GET
def score_dashboard(request):
    """Page HTML du dashboard (réservée au staff)."""
    return render(request, "monitoring/score_dashboard.html", {
        "stats": score_monitor.get_stats(),
        "alerts": score_monitor.get_alerts(limit=30),
    })


@staff_member_required
@require_GET
def score_dashboard_api(request):
    """Endpoint JSON pour rafraîchissement AJAX."""
    score_type = request.GET.get("type")
    return JsonResponse({
        "stats": score_monitor.get_stats(score_type) if score_type else score_monitor.get_stats(),
        "alerts": score_monitor.get_alerts(
            level=request.GET.get("level"),
            limit=int(request.GET.get("limit", 50)),
        ),
        "recent": (
            score_monitor.get_recent_records(score_type, limit=50)
            if score_type else None
        ),
    })


@staff_member_required
def score_dashboard_reset(request):
    """Réinitialise les compteurs (POST uniquement)."""
    if request.method != "POST":
        return JsonResponse({"error": "POST requis"}, status=405)
    score_type = request.POST.get("type")
    score_monitor.reset(score_type)
    return JsonResponse({"ok": True, "reset": score_type or "all"})

