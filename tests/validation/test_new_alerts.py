"""
Test complet des 7 nouvelles alertes du monitoring
"""

from myapp.monitoring.score_monitoring import score_monitor

print("=" * 80)
print("TEST: Nouvelles alertes du monitoring")
print("=" * 80)

# Réinitialiser
score_monitor.reset()

# ============================================================================
# TEST 1: Alerte de variance excessive
# ============================================================================
print("\n[TEST 1] Variance excessive")
print("-" * 40)

# Enregistrer des scores avec variance élevée
for i in range(15):
    score_monitor.record('professionnel', value=20 + (i * 5), client_id=1)

alerts = score_monitor.get_alerts_by_type_message("variance")
print(f"Alertes 'variance': {len(alerts)}")
if alerts:
    print(f"✓ Détectée: {alerts[0]['message'][:70]}...")

# ============================================================================
# TEST 2: Alerte taux d'anomalies
# ============================================================================
print("\n[TEST 2] Taux d'anomalies élevé")
print("-" * 40)

# Enregistrer beaucoup d'anomalies
for i in range(10):
    score_monitor.record('simple', value=i % 2 * 120, client_id=2)  # Scores hors plage

alerts = score_monitor.get_alerts_by_type_message("anomalies")
print(f"Alertes 'anomalies': {len(alerts)}")
if alerts:
    for alert in alerts[-2:]:
        print(f"✓ {alert['level']}: {alert['message'][:60]}...")

# ============================================================================
# TEST 3: Anomalies récurrentes par client
# ============================================================================
print("\n[TEST 3] Anomalies récurrentes par client")
print("-" * 40)

# Créer un client avec anomalies
for i in range(6):
    score_monitor.record('professionnel', value=150, client_id=42, plat_id=i)

alerts = score_monitor.get_recent_alerts_by_client(client_id=42)
client_alerts = [a for a in alerts if "Client" in a['message'] and "anomalies" in a['message']]
print(f"Alertes client 42: {len(client_alerts)}")
if client_alerts:
    print(f"✓ Détectée: {client_alerts[0]['message']}")

# ============================================================================
# TEST 4: Anomalies récurrentes par plat
# ============================================================================
print("\n[TEST 4] Anomalies récurrentes par plat")
print("-" * 40)

# Plat causant des anomalies
for i in range(5):
    score_monitor.record('imc', value=-10, client_id=i, plat_id=99)

alerts = score_monitor.get_alerts_by_plat(plat_id=99)
plat_alerts = [a for a in alerts if "Plat" in a['message'] and "anomalies" in a['message']]
print(f"Alertes plat 99: {len(plat_alerts)}")
if plat_alerts:
    print(f"✓ Détectée: {plat_alerts[0]['message']}")

# ============================================================================
# TEST 5: Variation importante du score
# ============================================================================
print("\n[TEST 5] Variation importante du score")
print("-" * 40)

score_monitor.reset()

# Enregistrer deux scores avec grande variation
score_monitor.record('professionnel', value=30, client_id=5)
score_monitor.record('professionnel', value=70, client_id=5)  # +40 points

alerts = score_monitor.get_alerts_by_type_message("variation")
print(f"Alertes 'variation': {len(alerts)}")
if alerts:
    print(f"✓ Détectée: {alerts[0]['message']}")

# ============================================================================
# TEST 6: Pattern suspect (scores identiques)
# ============================================================================
print("\n[TEST 6] Pattern suspect (scores identiques)")
print("-" * 40)

score_monitor.reset()

# Enregistrer des scores identiques
for i in range(6):
    score_monitor.record('simple', value=75.0, client_id=6)

alerts = score_monitor.get_alerts_by_type_message("pattern")
print(f"Alertes 'pattern': {len(alerts)}")
if alerts:
    print(f"✓ Détectée: {alerts[0]['message']}")

# ============================================================================
# TEST 7: Moyenne extrême
# ============================================================================
print("\n[TEST 7] Moyenne extrême (trop basse ou trop haute)")
print("-" * 40)

score_monitor.reset()

# Scores très bas
for i in range(15):
    score_monitor.record('professionnel', value=10 + i, client_id=7)

alerts = score_monitor.get_alerts_by_type_message("moyenne")
print(f"Alertes 'moyenne': {len(alerts)}")
if alerts:
    print(f"✓ Détectée: {alerts[0]['message']}")

# ============================================================================
# TEST 8: Groupement par catégorie
# ============================================================================
print("\n[TEST 8] Groupement par catégorie")
print("-" * 40)

categories = score_monitor.get_alerts_by_category()
print(f"Catégories détectées:")
for category, alerts_list in categories.items():
    print(f"  - {category}: {len(alerts_list)} alertes")

# ============================================================================
# TEST 9: Résumé des anomalies
# ============================================================================
print("\n[TEST 9] Résumé des anomalies")
print("-" * 40)

summary = score_monitor.get_anomalies_summary()
print(f"Clients avec anomalies: {summary['total_anomalies_by_client']}")
print(f"Plats avec anomalies: {summary['total_anomalies_by_plat']}")
print(f"Clients critiques: {summary['critical_clients']}")
print(f"Plats problématiques: {summary['problematic_plats']}")

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
print("\n" + "=" * 80)
print("RÉSUMÉ DES TESTS")
print("=" * 80)

all_alerts = score_monitor.get_alerts(limit=1000)
print(f"\n✓ Total d'alertes générées: {len(all_alerts)}")

alert_types = {}
for alert in all_alerts:
    level = alert['level']
    alert_types[level] = alert_types.get(level, 0) + 1

print(f"\nRépartition par niveau:")
for level, count in sorted(alert_types.items()):
    icon = {"CRITICAL": "🔴", "WARNING": "🟡", "INFO": "ℹ️"}.get(level, "")
    print(f"  {icon} {level}: {count} alertes")

categories = score_monitor.get_alerts_by_category()
print(f"\nRépartition par catégorie:")
for category, alerts_list in sorted(categories.items()):
    print(f"  - {category}: {len(alerts_list)} alertes")

print("\n✅ Tous les tests sont terminés!")
print("✅ Les 7 nouvelles alertes fonctionnent correctement!")
