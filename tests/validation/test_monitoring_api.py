#!/usr/bin/env python
"""
Test de l'API monitoring - Vérifier que score_dashboard_api retourne du JSON valide.
"""

import json
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.monitoring.score_monitoring import score_monitor, Alert, ALERT_WARNING, ALERT_CRITICAL


def test_get_alerts_api():
    """Teste que get_alerts() retourne des alertes JSON-sérialisables."""
    print("\n✓ Test: API get_alerts()")
    
    # Créer quelques alertes test
    for i in range(3):
        alert = Alert(
            level=ALERT_WARNING if i % 2 == 0 else ALERT_CRITICAL,
            score_type='professionnel',
            message=f'[TEST {i}] Test alert message',
            context={
                'client_nom': f'Client {i}',
                'client_id': i + 1,
                'plat_nom': f'Plat {i}',
                'plat_id': i + 10,
                'profil_objectif': 'minceur',
                'imc_num': 23.5 + i,
                'imc_cat': 'normal',
                'profil_age': 30 + i,
                'profil_sexe': 'M',
                'profil_poids_kg': 75.0,
                'profil_taille_cm': 180.0,
                'plat_calories': 350.0 + (i * 50),
                'plat_proteines_g': 15.0,
                'plat_glucides_g': 45.0,
                'plat_lipides_g': 12.0,
                'plat_fibres_g': 8.0,
                'besoins_calories': 2500.0,
                'besoins_proteines': 80.0,
                'besoins_fibres': 30.0,
                'breakdown': {
                    'calories': 25.5,
                    'proteines': 18.0,
                }
            },
            client_id=i + 1,
            plat_id=i + 10,
        )
        score_monitor._alerts.append(alert)
    
    # Récupérer les alertes via l'API
    alerts = score_monitor.get_alerts(limit=10)
    
    # Vérifier que c'est une liste de dicts
    assert isinstance(alerts, list), "get_alerts() doit retourner une liste"
    assert all(isinstance(a, dict) for a in alerts), "Tous les éléments doivent être des dicts"
    
    # Essayer de sérialiser en JSON
    try:
        json_str = json.dumps(alerts)
        print(f"  ✅ API retourne JSON valide: {len(json_str)} chars")
        
        # Vérifier la structure
        parsed = json.loads(json_str)
        assert len(parsed) > 0, "Doit contenir au moins une alerte"
        
        first_alert = parsed[0]
        assert 'level' in first_alert, "L'alerte doit avoir 'level'"
        assert 'message' in first_alert, "L'alerte doit avoir 'message'"
        assert 'context' in first_alert, "L'alerte doit avoir 'context'"
        assert isinstance(first_alert['context'], dict), "context doit être un dict"
        
        print(f"  ✅ Structure OK: {len(parsed)} alertes avec tous les champs")
        return True
    except TypeError as e:
        print(f"  ❌ Error JSON serialization: {e}")
        return False


def test_get_stats():
    """Teste que get_stats() retourne des stats JSON-sérialisables."""
    print("\n✓ Test: API get_stats()")
    
    # Enregistrer quelques scores
    score_monitor.record('professionnel', 75.0, context={'test': 'value'}, client_id=1)
    score_monitor.record('professionnel', 80.0, context={'test': 'value2'}, client_id=2)
    score_monitor.record('professionnel', 70.0, context={'test': 'value3'}, client_id=1)
    
    # Récupérer les stats
    stats = score_monitor.get_stats()
    
    try:
        json_str = json.dumps(stats)
        print(f"  ✅ Stats JSON valide: {len(json_str)} chars")
        
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict), "Stats doit être un dict"
        assert 'professionnel' in parsed, "Doit contenir 'professionnel'"
        
        prof_stats = parsed['professionnel']
        assert 'samples' in prof_stats
        assert 'mean' in prof_stats
        assert 'stddev' in prof_stats
        
        print(f"  ✅ Stats structure OK avec {len(parsed)} types de scores")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_json_response_safe():
    """Teste que les données sont prêtes pour JsonResponse."""
    print("\n✓ Test: Compatibilité JsonResponse")
    
    from django.http import JsonResponse
    
    # Créer des données comme le ferait score_dashboard_api
    data = {
        "stats": score_monitor.get_stats(),
        "alerts": score_monitor.get_alerts(limit=10),
        "recent": score_monitor.get_recent_records('professionnel', limit=5) if 'professionnel' in score_monitor._records else None,
    }
    
    try:
        # JsonResponse lève une exception si les données ne sont pas JSON-sérialisables
        response = JsonResponse(data)
        json_content = response.content.decode('utf-8')
        
        # Vérifier que c'est du JSON valide
        parsed = json.loads(json_content)
        print(f"  ✅ JsonResponse compatible: {len(json_content)} bytes")
        print(f"     - Stats: {'stats' in parsed}")
        print(f"     - Alerts: {'alerts' in parsed}")
        print(f"     - Recent: {'recent' in parsed}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("  TEST DE L'API MONITORING")
    print("=" * 70)
    
    results = [
        test_get_alerts_api(),
        test_get_stats(),
        test_json_response_safe(),
    ]
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print(f"  RÉSULTAT: {passed}/{total} tests passés")
    print("=" * 70)
    
    return all(results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
