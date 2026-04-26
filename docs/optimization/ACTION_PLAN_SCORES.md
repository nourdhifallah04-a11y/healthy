# 📋 PLAN D'ACTION - CORRECTION DES CALCULS DE SCORE

**Priorité:** 🔴 URGENT | **Durée:** 4-8 heures | **Impact:** Production-blocking

---

## 🎯 OBJECTIF

**Fixer les calculs de score pour les catégories SURPOIDS et OBÉSITÉ qui échouent à 100% des tests.**

---

## 🔴 PROBLÈME RÉSUMÉ

```
Cas obésité simple: Soupe légère (150 cal, 10g prot)
❌ Score obtenu: 42/100 (MAUVAIS)
✅ Score attendu: 85-100 (EXCELLENT pour régime)

Raison: L'algorithme échoue à valoriser les plats légers
        et pénalise trop les protéines basses
```

---

## ✅ PLAN D'ACTION (4 étapes)

### ÉTAPE 1: Valider les Données (15 min)
**Fichier:** Aucun - juste vérification

```bash
# Vérifier que les valeurs plat ne sont pas agrégées
python manage.py shell
>>> from myapp.models import Plat
>>> plat = Plat.objects.filter(nom__icontains="Cabillaud").first()
>>> print(f"Cal: {plat.calorie}, Prot: {plat.proteine}")
# Attendu: ~300-900 cal, ~20-80g prot
# NON pas 1900 cal, 800g prot!
```

**Action:** Si valeurs érronées, nettoyer la DB

---

### ÉTAPE 2: Fixer `_score_by_strategy()` (1.5 heures)
**Fichier:** [myapp/models.py](myapp/models.py#L415)

**Changement:** Remplacer la fonction pour utiliser des caps intermédiaires

**Avant:**
```python
# Additionne sans limite → résultats imprévisibles
score = 0
score += calories_bonus  # 0-35 pts
score += protein_bonus   # 0-35 pts
# ... etc
return score / 100 * 80  # Division arbitraire!
```

**Après:**
```python
# CAP chaque critère à sa valeur max
scores = {
    'calories': min(calc_cal_score(plat), 25),
    'protein': min(calc_prot_score(plat), 30),
    'carbs': min(calc_carbs_score(plat), 20),
    'fat': min(calc_fat_score(plat), 20),
    'fiber': min(calc_fiber_score(plat), 20),
}
return min(100, sum(scores.values()))  # MAX 100
```

**Tests validant cette étape:**
```python
# Après fix, doit passer:
plat_soupe = Plat.objects.get(nom__icontains="Soupe")
score = Plat.calculer_score_recommendation(
    plat_soupe, 
    categorie_imc='obesite',
    age=35, sexe='femme'
)
assert 85 <= score <= 100, f"Expected 85-100, got {score}"  # ✅ DOIT PASSER
```

---

### ÉTAPE 3: Ajouter "Zones Grises" aux Stratégies (45 min)
**Fichier:** [myapp/score_constants.py](myapp/score_constants.py#L70)

**Problème:** Les stratégies n'ont que PASSE/ÉCHOUE, pas de dégradé

**Changement:** Pour surpoids/obésité, ajouter seuils "acceptables"

```python
'surpoids': {
    'calories_max': 500,          # EXCELLENT (→ +25 pts)
    'calories_acceptable': 600,   # BON (→ +15 pts)
    'calories_limit': 750,        # ACCEPTABLE (→ +5 pts)
    
    'protein_range': (25, 40),    # IDÉAL (→ +30 pts)
    'protein_minimum': 15,        # ACCEPTABLE (→ +10 pts)
    # NE PAS pénaliser trop dur si < 15g
    
    # ... idem pour autres nutriments
}
```

**Résultat:** Les plats légers (soupe) recevront des points même avec protéines basses

---

### ÉTAPE 4: Lancer Tests de Validation (30 min)
**Fichier:** `test_2_score_recommendation_imc.py`

**Commande:**
```bash
python test_2_score_recommendation_imc.py
```

**Résultat attendu:**
```
INSUFFISANCE_PONDERALE:  3/3 ✅  (était 1/3)
NORMAL:                  3/3 ✅  (était 2/3)
SURPOIDS:                3/3 ✅  (était 0/3)  ← KEY FIX
OBÉSITÉ:                 3/3 ✅  (était 0/3)  ← KEY FIX
TOTAL:                  12/12 = 100% ✅
```

---

## 📊 IMPACT ESTIMÉ

| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| Tests réussis | 3/12 (25%) | 12/12 (100%) | +300% |
| Production ready | ❌ | ✅ | ✅ |
| Utilisateurs affectés | 40% (SURP/OBE) | 0% | 100% |
| Temps fix | - | 4-8h | - |

---

## 🔍 VÉRIFICATION FINALE

Après les 4 étapes, vérifier:

```bash
# 1. Tests simples
python test_1_score_simple.py
# Expected: 5/5 ✅

# 2. Tests IMC
python test_2_score_recommendation_imc.py
# Expected: 12/12 ✅

# 3. Tests recommandation
python test_3_restrictions.py
# Expected: Aucune erreur

# 4. Validation globale
python validate_scores.py
# Expected: Aucun score invalide
```

---

## ⚠️ RISQUES ET MITIGATIONS

| Risque | Sévérité | Mitigation |
|--------|----------|-----------|
| Modifications cassent autres calculs | MEDIUM | Lancer full test suite |
| Données utilisateur mal formées | HIGH | Vérifier DB avant fix |
| JavaScript non synchronisé | MEDIUM | Vérifier pas de dépendance JS |
| Performances dégradées | LOW | Benchmark avant/après |

---

## 📅 TIMELINE ESTIMÉE

```
[JOUR 1 - 4-5 heures]
├─ 08:00-08:15: Validation données DB
├─ 08:15-10:00: Fix _score_by_strategy()
├─ 10:00-10:45: Recalibrer stratégies
├─ 10:45-11:15: Tests de validation
└─ 11:15-12:00: Documentation

[JOUR 2 - 2-3 heures]
├─ Révision et feedback
├─ Tests additionnels
└─ Déploiement
```

---

## ✍️ NOTES DÉVELOPPEUR

### Points clés à retenir:

1. **La clé est la normalisation:** Chaque critère doit avoir un max fixe (25-30 pts), pas une somme illimitée

2. **Les "zones grises" importent:** Au lieu de PASSE/ÉCHOUE, avoir des dégradés

3. **Tester après chaque changement:** Les scores sont interdépendants

4. **Valider les données d'entrée:** Les valeurs plat ne doivent pas être agrégées

### Fichiers modifiés:
- `myapp/models.py` - 2-3 fonctions
- `myapp/score_constants.py` - 1 dictionnaire
- Aucun changement frontend (si Python correct)

### Pas de dépendances:
- ✅ Pas d'API externe
- ✅ Pas de migration DB
- ✅ Pas de change frontend

---

## 🎯 CRITÈRE DE SUCCÈS

✅ **PRODUCTION PRÊT QUAND:**
- 100% des tests simples passent
- 100% des tests IMC passent
- Tous les scores ∈ [0, 100]
- Aucune alerte de performance
- Documentation mise à jour

---

**Créé:** 19 Avril 2026  
**Urgence:** 🔴 À faire aujourd'hui  
**Questions?** Voir ANALYSE_TECHNIQUE_SCORES.md
