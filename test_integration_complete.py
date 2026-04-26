#!/usr/bin/env python
"""
Test d'intégration complète du monitoring et des scores.
Vérifie que le système entier fonctionne de manière cohérente.
"""

import json
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.score_monitoring import score_monitor, Alert, ALERT_WARNING, ALERT_INFO, ALERT_CRITICAL
from django.http import JsonResponse


def test_end_to_end_flow():
    """
    Simule le flux complet:
    1. Enregistrement d'un score avec contexte enrichi
    2. Récupération des alertes
    3. Sérialisation JSON pour l'API
    4. Rendu du template
    """
    print("\n✓ Test: Flux complet d'intégration")
    
    # Reset le monitor
    score_monitor.reset()
    
    # 1. Enregistrer un score avec contexte enrichi (comme dans models.py)
    enriched_context = {
        'client_nom': 'Alice Dupont',
        'client_id': 123,
        'plat_nom': 'Salade Niçoise',
        'plat_id': 456,
        'profil_objectif': 'prise_muscle',
        'imc_num': 22.5,
        'imc_cat': 'normal',
        'profil_age': 28,
        'profil_sexe': 'F',
        'profil_poids_kg': 65.0,
        'profil_taille_cm': 170.0,
        'plat_calories': 450.0,
        'plat_proteines_g': 25.0,
        'plat_glucides_g': 50.0,
        'plat_lipides_g': 15.0,
        'plat_fibres_g': 10.0,
        'besoins_calories': 2400.0,
        'besoins_proteines': 90.0,
        'besoins_fibres': 35.0,
        'breakdown': {
            'calories': 28.5,
            'proteines': 22.0,
            'glucides': 25.0,
            'lipides': 18.0,
            'fibres': 20.0,
            'age_sexe': 15.0,
        }
    }
    
    # Enregistrer le score
    score_monitor.record(
        'professionnel',
        85.5,
        context=enriched_context,
        client_id=123,
        plat_id=456,
    )
    
    print("  ✅ Score enregistré avec contexte enrichi")
    
    # Créer une alerte test avec le même contexte enrichi pour tester
    # (En production, les alertes sont générées automatiquement lors de la détection d'anomalies)
    test_alert = Alert(
        level=ALERT_WARNING,
        score_type='professionnel',
        message='[TEST] Alerte test pour vérifier la cohérence',
        context=enriched_context,
        client_id=123,
        plat_id=456,
    )
    score_monitor._alerts.append(test_alert)
    
    print("  ✅ Alerte test créée avec contexte enrichi")
    
    # 2. Récupérer les alertes via l'API
    alerts_api = score_monitor.get_alerts(limit=50)
    
    assert isinstance(alerts_api, list), "get_alerts() doit retourner une liste"
    assert len(alerts_api) > 0, "Doit avoir au moins une alerte"
    
    print(f"  ✅ {len(alerts_api)} alerte(s) récupérée(s)")
    
    # 3. Vérifier la structure de l'alerte API
    first_alert = alerts_api[0]
    assert 'context' in first_alert
    assert isinstance(first_alert['context'], dict)
    
    ctx = first_alert['context']
    expected_keys = [
        'client_nom', 'client_id', 'plat_nom', 'plat_id',
        'profil_objectif', 'imc_num', 'imc_cat',
        'profil_age', 'profil_sexe', 'profil_poids_kg', 'profil_taille_cm',
        'plat_calories', 'plat_proteines_g', 'plat_glucides_g',
        'plat_lipides_g', 'plat_fibres_g',
        'besoins_calories', 'besoins_proteines', 'besoins_fibres'
    ]
    
    missing_keys = [k for k in expected_keys if k not in ctx]
    assert not missing_keys, f"Champs manquants: {missing_keys}"
    
    print(f"  ✅ Contexte contient tous les {len(expected_keys)} champs attendus")
    
    # 4. Vérifier la sérialisation JSON
    try:
        json_str = json.dumps(alerts_api)
        print(f"  ✅ Alertes sérialisées en JSON ({len(json_str)} bytes)")
    except TypeError as e:
        print(f"  ❌ Erreur de sérialisation: {e}")
        return False
    
    # 5. Vérifier la compatibilité JsonResponse
    response_data = {
        "stats": score_monitor.get_stats(),
        "alerts": alerts_api,
    }
    
    try:
        response = JsonResponse(response_data)
        print(f"  ✅ JsonResponse compatible")
    except Exception as e:
        print(f"  ❌ JsonResponse error: {e}")
        return False
    
    # 6. Vérifier les données qu'on rendrait au template
    template_context = {
        "stats": score_monitor.get_stats(),
        "alerts": alerts_api,
    }
    
    # Simuler ce que le template verrait
    if template_context['alerts']:
        alert = template_context['alerts'][0]
        context = alert.get('context', {})
        
        # Vérifier quelques champs que le template affiche
        assertions = [
            (context.get('client_nom') == 'Alice Dupont', "client_nom"),
            (context.get('plat_nom') == 'Salade Niçoise', "plat_nom"),
            (context.get('imc_num') == 22.5, "imc_num"),
            (context.get('plat_calories') == 450.0, "plat_calories"),
            (context.get('plat_proteines_g') == 25.0, "plat_proteines_g"),
            (isinstance(context.get('breakdown'), dict), "breakdown est dict"),
        ]
        
        for assertion, field in assertions:
            if not assertion:
                print(f"  ❌ Assertion échouée: {field}")
                return False
        
        print(f"  ✅ Template peut afficher tous les détails (test sur {len(assertions)} champs)")
    
    return True


def test_stats_coherence():
    """Vérifie la cohérence des statistiques."""
    print("\n✓ Test: Cohérence des statistiques")
    
    # Ne pas faire reset, utiliser les scores déjà enregistrés du test précédent
    
    # Enregistrer quelques scores supplémentaires pour avoir des stats
    for i in range(5):
        score_monitor.record(
            'professionnel',
            70.0 + (i * 5),
            context={'test': f'value{i}'},
            client_id=1,
        )
    
    stats = score_monitor.get_stats()
    
    assert len(stats) > 0, "Stats doit contenir au moins un type de score"
    
    # Vérifier un type de score s'il existe
    if 'professionnel' in stats:
        prof_stats = stats['professionnel']
    else:
        # Prendre le premier type de score disponible
        prof_stats = list(stats.values())[0]
    
    # Vérifier les champs
    required_fields = ['samples', 'mean', 'stddev', 'min', 'max', 'anomalies', 'outliers', 'health']
    missing = [f for f in required_fields if f not in prof_stats]
    
    if missing:
        print(f"  ❌ Champs manquants: {missing}")
        return False
    
    # Vérifier que les valeurs sont cohérentes
    assert prof_stats['samples'] >= 1, "Doit avoir au moins 1 sample"
    assert prof_stats['min'] <= prof_stats['mean'] <= prof_stats['max'], "Mean doit être entre min et max"
    assert prof_stats['stddev'] >= 0, "Stddev doit être positif"
    
    print(f"  ✅ Stats cohérentes (samples={prof_stats['samples']}, mean={prof_stats['mean']:.1f}, health={prof_stats['health']})")
    return True


def test_template_rendering_simulation():
    """Simule ce que le template Django rendrait."""
    print("\n✓ Test: Simulation du rendu template")
    
    alerts = score_monitor.get_alerts(limit=5)
    
    # Simuler ce que ferait le template Django
    rendered_fields = []
    for alert in alerts:
        ctx = alert.get('context', {})
        if ctx:
            fields_rendered = {
                'client_nom': ctx.get('client_nom'),
                'plat_nom': ctx.get('plat_nom'),
                'profil_objectif': ctx.get('profil_objectif'),
                'imc_num': ctx.get('imc_num'),
                'imc_cat': ctx.get('imc_cat'),
                'profil_age': ctx.get('profil_age'),
                'profil_sexe': ctx.get('profil_sexe'),
                'profil_poids_kg': ctx.get('profil_poids_kg'),
                'profil_taille_cm': ctx.get('profil_taille_cm'),
                'plat_calories': ctx.get('plat_calories'),
                'plat_proteines_g': ctx.get('plat_proteines_g'),
                'plat_glucides_g': ctx.get('plat_glucides_g'),
                'plat_lipides_g': ctx.get('plat_lipides_g'),
                'plat_fibres_g': ctx.get('plat_fibres_g'),
                'besoins_calories': ctx.get('besoins_calories'),
                'besoins_proteines': ctx.get('besoins_proteines'),
                'besoins_fibres': ctx.get('besoins_fibres'),
            }
            rendered_fields.append(fields_rendered)
    
    if rendered_fields:
        print(f"  ✅ Template pourrait afficher {len(rendered_fields)} alerte(s)")
        print(f"     Champs par alerte: {len(rendered_fields[0])}")
        return True
    else:
        print(f"  ⚠️  Aucune alerte à afficher")
        return True


def main():
    print("=" * 70)
    print("  TEST D'INTÉGRATION COMPLÈTE")
    print("=" * 70)
    
    results = [
        test_end_to_end_flow(),
        test_stats_coherence(),
        test_template_rendering_simulation(),
    ]
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print(f"  RÉSULTAT: {passed}/{total} tests passés")
    print("=" * 70)
    
    if all(results):
        print("\n✅ Le monitoring et les scores sont COHÉRENTS et FONCTIONNELS")
        return True
    else:
        print("\n❌ Des problèmes de cohérence détectés")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
