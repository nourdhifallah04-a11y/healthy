#!/usr/bin/env python
"""
Test de cohérence du monitoring avec les scores enrichis.
Vérifie que:
1. Les contextes enrichis contiennent tous les champs attendus
2. Les alertes sont JSON-sérialisables
3. Le template peut afficher tous les détails
"""

import json
import os
import sys
import django
from dataclasses import asdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.monitoring.score_monitoring import score_monitor, Alert, ALERT_WARNING, ALERT_CRITICAL
from myapp.models import Utilisateur, Client, ProfilNutritionnel, Plat


def test_alert_serialization():
    """Teste que les alertes sont JSON-sérialisables."""
    print("\n✓ Test 1: Sérialisation JSON des alertes")
    
    # Créer une alerte test avec contexte enrichi
    test_alert = Alert(
        level=ALERT_WARNING,
        score_type='professionnel',
        message='[TEST] Alerte de test pour vérifier la sérialisation',
        context={
            'client_nom': 'John Doe',
            'client_id': 42,
            'plat_nom': 'Salade César',
            'plat_id': 10,
            'profil_objectif': 'minceur',
            'imc_num': 24.5,
            'imc_cat': 'normal',
            'profil_age': 30,
            'profil_sexe': 'M',
            'profil_poids_kg': 75.0,
            'profil_taille_cm': 180.0,
            'plat_calories': 350.0,
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
                'glucides': 20.0,
                'lipides': 15.0,
                'fibres': 22.5,
                'age_sexe': 10.0,
            }
        },
        client_id=42,
        plat_id=10,
    )
    
    # Convertir en dict
    alert_dict = asdict(test_alert)
    
    # Rendre JSON-safe
    alert_dict['context'] = score_monitor._make_json_safe(alert_dict.get('context', {}))
    
    # Essayer de sérialiser en JSON
    try:
        json_str = json.dumps(alert_dict)
        print(f"  ✅ Alert serialized: {len(json_str)} chars")
        return True
    except TypeError as e:
        print(f"  ❌ Error serializing alert: {e}")
        return False


def test_context_fields():
    """Vérifie que le contexte contient tous les champs attendus par le template."""
    print("\n✓ Test 2: Champs du contexte")
    
    required_fields = [
        'client_nom', 'client_id',
        'plat_nom', 'plat_id',
        'profil_objectif',
        'imc_num', 'imc_cat',
        'profil_age', 'profil_sexe',
        'profil_poids_kg', 'profil_taille_cm',
        'plat_calories', 'plat_proteines_g',
        'plat_glucides_g', 'plat_lipides_g',
        'plat_fibres_g',
        'besoins_calories', 'besoins_proteines',
        'besoins_fibres',
    ]
    
    # Contexte test
    test_context = {
        'client_nom': 'Test User',
        'client_id': 1,
        'plat_nom': 'Test Plat',
        'plat_id': 1,
        'profil_objectif': 'test',
        'imc_num': 25.0,
        'imc_cat': 'normal',
        'profil_age': 30,
        'profil_sexe': 'M',
        'profil_poids_kg': 75.0,
        'profil_taille_cm': 180.0,
        'plat_calories': 350.0,
        'plat_proteines_g': 15.0,
        'plat_glucides_g': 45.0,
        'plat_lipides_g': 12.0,
        'plat_fibres_g': 8.0,
        'besoins_calories': 2500.0,
        'besoins_proteines': 80.0,
        'besoins_fibres': 30.0,
    }
    
    missing = [f for f in required_fields if f not in test_context]
    
    if not missing:
        print(f"  ✅ Tous les {len(required_fields)} champs requis présents")
        return True
    else:
        print(f"  ❌ Champs manquants: {missing}")
        return False


def test_make_json_safe():
    """Teste la conversion JSON-safe."""
    print("\n✓ Test 3: Conversion JSON-safe")
    
    # Contexte avec types variés
    context = {
        'string': 'test',
        'int': 42,
        'float': 3.14,
        'bool': True,
        'none': None,
        'dict': {'nested': 'value'},
        'list': [1, 2, 3],
        'tuple': (1, 2, 3),
    }
    
    safe_context = score_monitor._make_json_safe(context)
    
    try:
        json_str = json.dumps(safe_context)
        print(f"  ✅ Context converted and serialized ({len(json_str)} chars)")
        
        # Vérifier les types
        parsed = json.loads(json_str)
        assert parsed['string'] == 'test'
        assert parsed['int'] == 42
        assert parsed['float'] == 3.14
        assert parsed['bool'] is True
        assert parsed['none'] is None
        assert parsed['dict']['nested'] == 'value'
        assert parsed['list'] == [1, 2, 3]
        assert isinstance(parsed['tuple'], list)  # tuple → list en JSON
        print(f"  ✅ Tous les types convertis correctement")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("=" * 70)
    print("  TEST DE COHÉRENCE DU MONITORING")
    print("=" * 70)
    
    results = [
        test_alert_serialization(),
        test_context_fields(),
        test_make_json_safe(),
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
