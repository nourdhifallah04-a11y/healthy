# Score Professionnel - Guide complet
## Quand utiliser calculer_score_professionnel()
### Utiliser quand :
- Profil Nutritionnel COMPLET (taille, poids, age, sexe, activite, objectif)
- Recommandations personnalisees haute precision
- Besoin du breakdown detaille (return_details=True)
### NE PAS utiliser pour :
- Tuiles plats anonymes -> calculer_score_nutritionnel()
- Reco basee IMC seulement -> calculer_score_recommendation()
- Batch > 1000 plats -> score IMC + cache
## Methodologie (6 sous-scores = 100 pts)
| Composante | Max | Logique |
|---|---|---|
| Calories  | 25 | Cibles selon IMC |
| Proteines | 30 | Priorite maximale |
| Glucides  | 15 | Selon objectif |
| Lipides   | 15 | Limites si surpoids/obesite |
| Fibres    | 10 | 1/3 des besoins journaliers |
| Age/Sexe  |  5 | Bonus contextuels |
| TOTAL     |100 | max(0, min(100, total)) |
## Exemples
    # Score simple
    score = Plat.calculer_score_professionnel(plat, profil)
    # Avec breakdown
    score, details = Plat.calculer_score_professionnel(
        plat, profil, return_details=True
    )
    # Mode debug
    Plat.calculer_score_professionnel(plat, profil, verbose=True)
## Monitoring
    from myapp.score_monitoring import score_monitor
    stats = score_monitor.get_stats('professionnel')
    alerts = score_monitor.get_alerts(level='CRITICAL')
Dashboard URL : /monitoring/scores/  (staff uniquement)
- Stats : moyenne, mediane, ecart-type, variance, min/max
- Alertes : scores hors [0,100], outliers (z-score > 3)
- Sante : OK / WARNING / CRITICAL
- Auto-refresh 30 secondes
### Seuils dalerte par defaut
| Seuil | Valeur | Effet |
|---|---|---|
| min/max_score      | 0 / 100  | CRITICAL si depasse |
| max_stddev         | 35       | CRITICAL (recalibrer) |
| min/max_mean_warn  | 25 / 90  | WARNING moyenne anormale |
| outlier_zscore     | 3.0      | WARNING outlier |
## Tests
    python manage.py test myapp.tests_score_professionnel
Couvre : bornes [0,100], allergies, 4 IMC x cas reels, monotonie, caps,
integration monitoring.
## Helpers prives (refactor)
| Helper | Role |
|---|---|
| _pro_check_restrictions() | Allergies & restrictions |
| _pro_calc_besoins()       | BMR + besoins (cal/prot/fib) |
| _pro_score_calories()     | Score 0-25 selon IMC |
| _pro_score_proteines()    | Score 0-30 selon IMC |
| _pro_score_glucides()     | Score 0-15 selon objectif |
| _pro_score_lipides()      | Score 0-15 selon IMC |
| _pro_score_fibres()       | Score 0-10 (1/3 besoins) |
| _pro_score_age_sexe()     | Bonus 0-5 contextuel |
| _pro_evaluation()         | Label qualitatif |
Tous statiques, purs, faciles a tester.
