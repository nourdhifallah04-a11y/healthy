"""
Script de test et démonstration des améliorations du monitoring des alertes
avec client_id, plat_id et menu_id.

Usage:
    python manage.py shell < test_monitoring_improved.py
    ou
    python test_monitoring_improved.py
"""

from myapp.score_monitoring import score_monitor

print("=" * 80)
print("TEST: Amélioration des logs d'alertes avec IDs")
print("=" * 80)

# ============================================================================
# TEST 1: Enregistrement simple avec traçabilité
# ============================================================================
print("\n[TEST 1] Enregistrement de scores avec traçabilité complète\n")

test_cases = [
    {
        'type': 'professionnel',
        'value': 85.2,
        'client_id': 1,
        'plat_id': 10,
        'menu_id': 5,
        'context': {'user': 'Alice', 'action': 'order'},
    },
    {
        'type': 'professionnel',
        'value': 72.0,
        'client_id': 2,
        'plat_id': 11,
        'menu_id': 6,
        'context': {'user': 'Bob'},
    },
    {
        'type': 'simple',
        'value': 65.5,
        'client_id': 1,
        'plat_id': 12,
        'context': {'user': 'Alice', 'note': 'another order'},
    },
]

for tc in test_cases:
    score_monitor.record(
        score_type=tc['type'],
        value=tc['value'],
        client_id=tc['client_id'],
        plat_id=tc.get('plat_id'),
        menu_id=tc.get('menu_id'),
        context=tc['context'],
    )
    print(f"✓ Enregistré: {tc['type']} = {tc['value']} (client={tc['client_id']}, "
          f"plat={tc.get('plat_id')}, menu={tc.get('menu_id')})")

# ============================================================================
# TEST 2: Récupération des alertes récentes
# ============================================================================
print("\n[TEST 2] Récupération des alertes récentes\n")

all_alerts = score_monitor.get_alerts(limit=100)
print(f"Total d'alertes enregistrées: {len(all_alerts)}")

for alert in all_alerts[-3:]:  # Les 3 dernières
    print(f"\n  Alerte: {alert['level']} [{alert['score_type']}]")
    print(f"    Client ID: {alert.get('client_id', 'N/A')}")
    print(f"    Plat ID: {alert.get('plat_id', 'N/A')}")
    print(f"    Menu ID: {alert.get('menu_id', 'N/A')}")
    print(f"    Message: {alert['message'][:60]}...")
    print(f"    Timestamp: {alert['timestamp']}")

# ============================================================================
# TEST 3: Filtrer les alertes par client_id
# ============================================================================
print("\n[TEST 3] Filtrer les alertes par client_id\n")

client_alerts = score_monitor.get_alerts(client_id=1, limit=50)
print(f"Alertes pour client_id=1: {len(client_alerts)}")
for alert in client_alerts:
    print(f"  - [{alert['level']}] Client {alert.get('client_id')} | "
          f"Plat {alert.get('plat_id')} | {alert['message'][:50]}...")

# ============================================================================
# TEST 4: Utiliser la méthode dédiée get_recent_alerts_by_client
# ============================================================================
print("\n[TEST 4] Utiliser get_recent_alerts_by_client()\n")

client_1_alerts = score_monitor.get_recent_alerts_by_client(client_id=1, limit=50)
print(f"Alertes récentes du client 1: {len(client_1_alerts)}")

client_2_alerts = score_monitor.get_recent_alerts_by_client(client_id=2, limit=50)
print(f"Alertes récentes du client 2: {len(client_2_alerts)}")

# ============================================================================
# TEST 5: Récupérer les enregistrements de score avec filtrage
# ============================================================================
print("\n[TEST 5] Récupérer les enregistrements de score\n")

all_records = score_monitor.get_recent_records('professionnel', limit=100)
print(f"Total d'enregistrements 'professionnel': {len(all_records)}")

client_1_records = score_monitor.get_recent_records(
    'professionnel', 
    limit=100,
    client_id=1
)
print(f"Enregistrements du client 1 pour 'professionnel': {len(client_1_records)}")

for record in client_1_records:
    print(f"  - Client {record.get('client_id')} | Score: {record['value']} | "
          f"Plat: {record.get('plat_id')} | Menu: {record.get('menu_id')}")

# ============================================================================
# TEST 6: Enregistrer un score qui déclenche une anomalie
# ============================================================================
print("\n[TEST 6] Enregistrer une anomalie (score hors plage)\n")

# Score invalide qui déclenche une alerte CRITICAL
score_monitor.record(
    score_type='professionnel',
    value=150.0,  # Hors plage [0, 100]
    client_id=3,
    plat_id=99,
    menu_id=77,
    context={'test': 'anomaly detection'},
)

critical_alerts = score_monitor.get_alerts(level='CRITICAL', limit=10)
print(f"Alertes CRITICAL détectées: {len(critical_alerts)}")
if critical_alerts:
    alert = critical_alerts[-1]
    print(f"\n  Alerte: {alert['message']}")
    print(f"  Client ID: {alert.get('client_id')}")
    print(f"  Plat ID: {alert.get('plat_id')}")
    print(f"  Menu ID: {alert.get('menu_id')}")

# ============================================================================
# TEST 7: Statistiques
# ============================================================================
print("\n[TEST 7] Statistiques de monitoring\n")

stats = score_monitor.get_stats()
for score_type, stat in stats.items():
    print(f"\nType: {score_type}")
    print(f"  Samples: {stat.get('samples')}")
    print(f"  Mean: {stat.get('mean')}")
    print(f"  Std Dev: {stat.get('stddev')}")
    print(f"  Min/Max: {stat.get('min')} / {stat.get('max')}")
    print(f"  Anomalies: {stat.get('anomalies')}")
    print(f"  Outliers: {stat.get('outliers')}")
    print(f"  Health: {stat.get('health')}")

# ============================================================================
# RÉSUMÉ
# ============================================================================
print("\n" + "=" * 80)
print("RÉSUMÉ DES AMÉLIORATIONS")
print("=" * 80)
print("""
✓ Paramètres client_id, plat_id, menu_id supportés dans record()
✓ Filtrage par client_id dans get_alerts()
✓ Nouvelle méthode get_recent_alerts_by_client()
✓ Filtrage par client_id dans get_recent_records()
✓ Logs améliorés avec affichage des IDs
✓ Traçabilité complète de chaque anomalie

Logs format:
  [LEVEL][score_type] | client_id=X | plat_id=Y | menu_id=Z | message...

API endpoints disponibles:
  GET /api/score-dashboard/                    (toutes les alertes)
  GET /api/score-dashboard/?client_id=42       (alertes du client 42)
  GET /api/score-dashboard/?level=CRITICAL     (alertes critiques)
  GET /api/score-dashboard/?client_id=42&level=WARNING  (combined filters)
""")

print("\n✅ Tous les tests sont terminés!")
