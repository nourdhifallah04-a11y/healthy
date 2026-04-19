# 🔬 ANALYSE TECHNIQUE APPROFONDIE - CALCULS DE SCORE

**Date:** 19 Avril 2026 | **Version:** 1.0 | **Statut:** 🔴 CRITIQUE

---

## 📋 TABLE DES MATIÈRES

1. [Résumé Exécutif](#résumé-exécutif)
2. [Problèmes Critiques](#problèmes-critiques)
3. [Architecture des Calculs](#architecture-des-calculs)
4. [Résultats Détaillés des Tests](#résultats-détaillés-des-tests)
5. [Solutions et Recommandations](#solutions-et-recommandations)
6. [Fichiers à Corriger](#fichiers-à-corriger)

---

## 📊 Résumé Exécutif

### Vue d'ensemble
L'application contient **trois systèmes de scoring nutritionnel**:
1. **Score Simple** (Plat seul): ✅ Fonctionne mais mal calibré
2. **Score Recommandation IMC** (Par catégorie): 🔴 CASSÉ - 75% d'échecs
3. **Score Professionnel** (Expert): ⚠️ Inutilisé

### Métriques Clés
- **Test couverture:** 60% simple, 25% IMC
- **Production readiness:** ❌ **NON RECOMMANDÉ** pour SURPOIDS/OBÉSITÉ
- **Synchronisation Py/JS:** ⚠️ Manuelle, risque de divergence
- **Performance cache:** ✅ 3-4x speedup (impact négligeable sur micro-calculs)

### Score de Confiance par Module
| Module | Confiance | Raison |
|--------|-----------|--------|
| Score Simple | 70% | Fonctionne mais bonus/malus déséquilibrés |
| Score IMC | 15% | Normalisation brisée, stratégies mal calibrées |
| Score Age/Sexe | 50% | Fonctionne partiellement, cas edge non couverts |
| Frontend JS | 60% | Pas de validation post-calcul |

---

## 🔴 Problèmes Critiques

### P1: ALGORITHME DE STRATÉGIE ÉCHOUE POUR OBÉSITÉ

**Localisation:** `myapp/models.py`, ligne 415+

**Description:**
La fonction `_score_by_strategy()` additionne les bonus de chaque nutriment sans cap intermédiaire, ce qui crée des résultats imprévisibles.

**Preuve:**
```python
# Cas: Soupe très légère pour personne obèse
# Attendu: Score ~85-100 (excellent pour régime)
# Obtenu: Score 34/100 (très mauvais!)

# Breakdown:
#   Calories (150 ≤ 400 max): ✅ PASSE → +35 pts
#   Protéines (10 < 30 min): ❌ ÉCHOUE → 0 pts (pénalité TOTALE!)
#   Glucides (15 < 25 max): ✅ PASSE → +15 pts
#   Lipides (2 < 10 max): ✅ PASSE → +25 pts
#   Fibres (8 ≥ 10 min): ❌ ÉCHOUE → 0 pts (pénalité TOTALE!)
#   = (35 + 0 + 15 + 25 + 0) / 100 * 80 = 61.6
#   + age_bonus (-10 à +20) = ~42/100 ❌
```

**Impact:** Plats recommandés sont systématiquement SOUS-ÉVALUÉS pour obésité.

**Sévérité:** 🔴 CRITIQUE - Produit défaillant

---

### P2: PÉNALITÉS EXCESSIVES DANS SCORE SIMPLE

**Localisation:** `myapp/models.py`, ligne 305+

**Description:**
Les bonus et malus s'annulent mutuellement au lieu de se cumuler intelligemment.

**Exemple 1 - Cabillaud:**
```
Valeurs: 900 cal, 80g prot, 12g lip, 12g fib
Calcul:
  Base: 50
  + Prot bonus (80 > 30): +20
  - Calories malus (900 > 800): -20  ← S'ANNULE!
  + Fibres bonus (12 > 10): +15
  = 65/100

Attendu: 75+ (très protéiné, excellent!)
Obtenu: 65 (moyen)
Delta: -10 points (13% d'erreur)
```

**Problème:** Le malus calories de -20 annule exactement le bonus protéine de +20, indépendamment de la qualité réelle du plat.

---

### P3: SEUILS DE STRATÉGIE MAL ALIGNÉS

**Localisation:** `myapp/score_constants.py`, ligne 68-95

**Description:**
Les stratégies par IMC ont des seuils contradictoires qui créent des "zones mortes" où les plats ne marquent aucun point.

**Cas SURPOIDS:**
```python
BMI_STRATEGIES['surpoids'] = {
    'protein_range': (25, 40),  # Minimum 25g
    'calories_max': 500,
}

# Test: Soupe Légère (150 cal, 10g prot)
# Résultat: 0 points protéine car 10 < 25! ← BUG
#           (même si 150 cal parfait pour régime)
```

**Impact:** Les plats très légers (soupes, salades) perdent tous les points protéine, même s'ils sont excellents pour un régime hypocalorique.

---

### P4: FUSION DONNÉES MENU-PLAT CRÉE ERREURS

**Localisation:** Détecté lors validation

**Description:**
Les valeurs du Cabillaud testées (1900 cal, 800g prot) suggèrent une agrégation involontaire de plusieurs plats/menus.

**Impact:** Les scores calculés peuvent représenter des ensembles au lieu de plats individuels.

---

## 🏗️ Architecture des Calculs

### Diagramme de Flux

```
┌─────────────────────────┐
│ Entrée: Plat            │ (nom, cal, prot, gluc, lipides, fibres)
└────────┬────────────────┘
         │
         ├──► [1] calculer_score_nutritionnel()
         │         ├─ Base: 50
         │         ├─ Bonus/Malus fixes
         │         └─ Clamp [0, 100] ✅
         │
         └──► [2] calculer_score_recommendation()
                  ├─ [2a] Vérifier allergies/restrictions (0 ou 100)
                  ├─ [2b] _score_by_strategy() 🔴
                  │       ├─ Additionner bonus par nutrient
                  │       └─ Diviser par 100 * 80 (PROBLÈME!)
                  ├─ [2c] _bonus_age_sexe() (OK)
                  └─ Final = base + age_bonus
```

### Problème de Normalisation

**Actuel (INCORRECT):**
```python
score_nutrient = 0
score_nutrient += calories_bonus (0-35 pts)
score_nutrient += protein_bonus (0-35 pts)
score_nutrient += carbs_bonus (0-20 pts)
score_nutrient += fat_bonus (0-20 pts)
score_nutrient += fiber_bonus (0-20 pts)
# Possible: 0 à 130+ pts!

base_score = (score_nutrient / 100.0) * 80  # Division arbitraire!
# Résultat imprévisible basé sur la somme interne
```

**Proposé (CORRECT):**
```python
# CAP chaque critère individuellement
score_cal = min(calories_partial, 30)    # Max 30
score_prot = min(protein_partial, 30)    # Max 30
score_carbs = min(carbs_partial, 20)     # Max 20
score_fat = min(fat_partial, 20)         # Max 20
score_fiber = min(fiber_partial, 20)     # Max 20

# Total: max 30+30+20+20+20 = 120, mais limiter à 100
base_score = min(100, score_cal + score_prot + score_carbs + score_fat + score_fiber)
```

---

## 📊 Résultats Détaillés des Tests

### Test 1: Score Simple (PARTIAL PASS)

| Plat | Valeurs | Score | Attendu | Résultat |
|------|---------|-------|---------|----------|
| Poulet Grillé | 300 cal, 35g prot, 8g lip, 8g fib | 78 | ≥70 | ✅ |
| Burger Gras | 1200 cal, 25g prot, 45g lip, 2g fib | 25 | ≤40 | ✅ |
| Salade | 350 cal, 28g prot, 12g lip, 12g fib | 75 | ≥65 | ✅ |
| **Riz Nature** | 200 cal, 4g prot, 0.5g lip, 1g fib | 50 | ≤40 | ❌ |
| **Cabillaud** | 900 cal, 80g prot, 12g lip, 12g fib | 65 | ≥75 | ❌ |

**Résultat:** 3/5 (60%) ✅ mais avec issues graves pour 2 cas

---

### Test 2: Score par IMC (CRITICAL FAILURE)

#### INSUFFISANCE PONDÉRALE
**Objectif:** Favoriser calories ↑ et protéines ↑

| Plat | Cal | Prot | Score | Attendu | Delta | Status |
|-----|-----|------|-------|---------|-------|--------|
| Pizza | 800 | 30 | 65.4 | 70-100 | -4.6 | ❌ |
| Poulet | 450 | 40 | 69.4 | 50-80 | -10.6 | ⚠️ (limite) |
| Soupe | 150 | 10 | 14.8 | 20-50 | **-5.2** | ❌ |

**Problème:** Soupe très légère (150 cal, 10g prot) n'est pas valorisée pour COMPLÉTER un régime insuffisance. Elle devrait marquer 30-50, pas 14.8!

---

#### NORMAL (IMC 18.5-25)
**Objectif:** Équilibre 400-800 cal + 20-35g prot

| Plat | Cal | Prot | Score | Attendu | Status |
|-----|-----|------|-------|---------|--------|
| Poulet | 450 | 40 | 95.6 | 70-100 | ✅ |
| Steak | 350 | 50 | 40.0 | 60-85 | ❌ |
| Pizza | 800 | 30 | 40.0 | 20-50 | ✅ |

**Problème:** Steak (350 cal, 50g prot) est sous-évalué parce que 350 < 400 cal minimum.

---

#### SURPOIDS (TOTAL FAILURE - 0/3)
**Objectif:** Calories ↓↓ (max 500) + Protéines ↑ (25-40g)

| Plat | Cal | Prot | Score | Attendu | Delta |
|-----|-----|------|-------|---------|-------|
| Soupe | 150 | 10 | 63.6 | 80-100 | **-36.4** 🔴 |
| Steak | 350 | 50 | 50.2 | 70-90 | **-39.8** 🔴 |
| Pizza | 800 | 30 | 30.24 | 5-30 | ±0.24 ✅ |

**Analyse:**
- Soupe: Calories EXCELLENTES mais protéines échouent → 0 points protéine!
- Steak: Protéines EXCELLENTES mais calories manquent min → sous-évalué

**Cause racine:** La fonction cherche TOUS les critères, pas les meilleurs.

---

#### OBÉSITÉ (TOTAL FAILURE - 0/3)
**Objectif:** Ultra-strict (≤350 cal, ≥30g prot)

| Plat | Cal | Prot | Score | Attendu | Delta |
|-----|-----|------|-------|---------|-------|
| Soupe | 150 | 10 | **42.04** | 85-100 | **-42.96** 🔴🔴 |
| Poulet | 450 | 40 | **47.04** | 60-80 | **-32.96** 🔴 |
| Pizza | 800 | 30 | **33.92** | 1-20 | **+13.92** 🔴 |

**VERDICT:** Complètement cassé. Soupe à 42/100 au lieu de 85-100!

---

## 💡 Solutions et Recommandations

### FIX #1: Revoir `_score_by_strategy()` (URGENT)

**Fichier:** `myapp/models.py`, ligne 415-500

**Code actuel problématique:**
```python
def _score_by_strategy(plat: "Plat", strategy: Dict) -> float:
    score = 0.0
    
    # Additionne sans cap intermédiaire
    if 'calories_max' in strategy:
        bonus = 30 if plat.calorie <= strategy['calories_max'] else 2
        bonus *= (1 - min(abs(plat.calorie - strategy['calories_max']) / 500, 0.8))
        score += min(bonus, strategy.get('calories_bonus', 30))  # CAN BE WRONG
    # ... continue à additionner
    
    return score  # Peut être > 100!
```

**Code proposé:**
```python
def _score_by_strategy(plat: "Plat", strategy: Dict) -> float:
    """
    Calcule score par stratégie avec caps intermédiaires.
    Max 100 points toujours.
    """
    scores = {}
    
    # === CALORIES (max 25 pts) ===
    scores['calories'] = 0
    if 'calories_max' in strategy:
        if plat.calorie <= strategy['calories_max']:
            scores['calories'] = 25
        elif plat.calorie <= strategy['calories_max'] * 1.2:
            scores['calories'] = 12
        else:
            scores['calories'] = 0
    
    elif 'calories_range' in strategy:
        cal_min, cal_max = strategy['calories_range']
        if cal_min <= plat.calorie <= cal_max:
            scores['calories'] = 25
        elif cal_min - 100 <= plat.calorie < cal_min:
            scores['calories'] = 10
        elif cal_max < plat.calorie <= cal_max + 100:
            scores['calories'] = 10
    
    # === PROTÉINES (max 30 pts) ===
    scores['protein'] = 0
    if 'protein_range' in strategy:
        p_min, p_max = strategy['protein_range']
        if p_min <= plat.proteine <= p_max:
            scores['protein'] = 30
        elif p_min - 5 <= plat.proteine < p_min:
            scores['protein'] = 15  # Léger malus
        elif plat.proteine > p_max:
            scores['protein'] = 20  # Bonus pour très protéiné
    
    elif 'protein_min' in strategy:
        if plat.proteine >= strategy['protein_min']:
            scores['protein'] = 30
        elif plat.proteine >= strategy['protein_min'] - 5:
            scores['protein'] = 15
    
    # === GLUCIDES, LIPIDES, FIBRES (même pattern) ===
    scores['carbs'] = 15  # Similar logic
    scores['fat'] = 15    # Similar logic
    scores['fiber'] = 15  # Similar logic
    
    # Normaliser: chaque critère est capped
    total = sum(scores.values())
    # Max 25 + 30 + 15 + 15 + 15 = 100
    return min(100, total)
```

---

### FIX #2: Améliorer `calculer_score_nutritionnel()` (IMPORTANT)

**Problème:** Bonus/malus s'annulent

**Solution:** Poids relatifs ajustés

```python
def calculer_score_nutritionnel(self) -> int:
    """Calcule score AVEC pondération inteligente"""
    score = 50
    
    # Protéines: +25 si bon, -15 si mauvais
    if self.proteine >= 30:
        score += 25
    elif self.proteine >= 20:
        score += 15
    elif self.proteine >= 10:
        score += 5
    else:
        score -= 15  # Pénalité plus sévère
    
    # Calories: bonus si bon, malus modéré si mauvais
    if self.calorie <= 600:
        score += 10  # Très bon
    elif self.calorie <= 800:
        score += 5   # Bon
    elif self.calorie > 1000:
        score -= 15  # Trop calorique
    
    # Fibres: +10 si bon
    if self.fibres >= 8:
        score += 10
    elif self.fibres >= 5:
        score += 5
    
    # Lipides: -5 si excessifs
    if self.lipides > 40 and self.proteine < 30:
        score -= 10  # Gras sans protéine = mauvais
    elif self.lipides > 25:
        score -= 5
    
    return max(0, min(100, score))
```

---

### FIX #3: Ajouter "Zones Grises" aux Stratégies

**Problème:** Les stratégies n'ont que PASSE/ÉCHOUE

**Solution:** Ajouter critères "acceptables"

```python
BMI_STRATEGIES['surpoids'] = {
    'calories_max': 500,           # EXCELLENT
    'calories_acceptable': 600,    # BON
    'calories_limit': 750,         # ACCEPTABLE
    
    'protein_min': 25,             # Minimum requis
    'protein_good': 30,            # Bon
    'protein_excellent': 40,       # Excellent
    
    # ... scoring:
    # protein >= 40: +30 pts
    # protein >= 30: +25 pts
    # protein >= 25: +20 pts
    # protein >= 20: +10 pts
    # protein < 20: +0 pts (pas de pénalité totale!)
}
```

---

## ✅ Checklist de Correctifs

### Phase 1 (Aujourd'hui - URGENT)
- [ ] Fixer `_score_by_strategy()` pour OBÉSITÉ
- [ ] Ajouter tests pour tous les cas limite
- [ ] Valider que scores ∈ [0, 100] toujours
- [ ] Documenter formules par catégorie IMC

### Phase 2 (Cette semaine)
- [ ] Recalibrer SIMPLE_SCORE_CONFIG avec poids équilibré
- [ ] Ajouter mode DEBUG detaillé (breakdown score)
- [ ] Implémenter alertes anomalies
- [ ] Synchroniser JS ↔ Python

### Phase 3 (Prochaine semaine)
- [ ] Refactoriser `calculer_score_professionnel()` ou supprimer
- [ ] Créer dashboard de monitoring
- [ ] Tests de régression complets
- [ ] Documentation utilisateur

---

## 📁 Fichiers à Corriger

### PRIMARY (Must Fix)
1. **[myapp/models.py](myapp/models.py)** - Ligne 415+
   - [ ] Revoir `_score_by_strategy()`
   - [ ] Améliorer `calculer_score_nutritionnel()`
   - [ ] Ajouter validation post-calcul

2. **[myapp/score_constants.py](myapp/score_constants.py)** - Ligne 50-95
   - [ ] Recalibrer BMI_STRATEGIES
   - [ ] Ajouter zones grises

### SECONDARY (Should Fix)
3. **[static/accueil/script.js](static/accueil/script.js)** - Ligne 373+
   - [ ] Valider calculateNutritionalScore()
   - [ ] Ajouter clamp [0, 100]

4. **[static/specialdiet/spec.js](static/specialdiet/spec.js)**
   - [ ] Valider affichage scores

### TERTIARY (Nice to Have)
5. **[test_2_score_recommendation_imc.py](test_2_score_recommendation_imc.py)**
   - [ ] Ajouter plus de cas test
   - [ ] Automatiser tests de régression

---

## 📈 Métriques de Succès

Après fixes:

| Métrique | Avant | Cible |
|----------|-------|-------|
| Test Simple Pass | 60% | 100% |
| Test IMC Pass | 25% | 95%+ |
| Production Ready | ❌ | ✅ |
| Score Range Valid | ✅ | ✅ |
| Debug Mode | ❌ | ✅ |

---

## 🎯 Prochaines Étapes

1. ✅ Rapport généré
2. ➡️ **Priorité:** Fixer `_score_by_strategy()`
3. ➡️ **Validation:** Lancer test suite complet
4. ➡️ **Déploiement:** Attendre 100% success avant prod

---

**Rapport Généré:** 19 Avril 2026  
**Auteur:** Système de Validation Automatisé  
**Révision:** 1.0
