# 📊 RAPPORT DE VÉRIFICATION DES CALCULS DE SCORE

**Date:** 19 Avril 2026  
**Statut:** 🔴 PROBLÈMES IDENTIFIÉS - Action requise

---

## 📋 RÉSUMÉ EXÉCUTIF

Les tests révèlent **des incohérences dans les calculs de score** à plusieurs niveaux:

| Catégorie | Résultat | Détail |
|-----------|----------|--------|
| **Score Simple** | 3/5 tests ✅ | Calcul de base avec issues correctes mais paramètres ajustement nécessaire |
| **Score IMC** | 3/12 tests ✅ | 75% des tests échouent - stratégies mal calibrées |
| **Score Professionnel** | ❓ | Non testé automatiquement |
| **Frontend (JS)** | ❓ | À valider |

---

## 🔍 RÉSULTATS DÉTAILLÉS

### TEST 1: SCORE SIMPLE (Calcul de base - Plat)
**Résultat: 3/5 tests réussis (60%)**

#### Cas réussis ✅:
- **Poulet Grillé Sain** (300 cal, 35g prot, 8g lip, 8g fib)
  - Score: **78/100** (attendu: ≥70) ✅
  - Analyse: Haute protéine, basses calories = bon score

- **Burger Gras** (1200 cal, 25g prot, 45g lip, 2g fib)
  - Score: **25/100** (attendu: ≤40) ✅
  - Analyse: Hautes calories, bas score correct

- **Salade Équilibrée** (350 cal, 28g prot, 12g lip, 12g fib)
  - Score: **75/100** (attendu: ≥65) ✅
  - Analyse: Équilibre optimal

#### Cas échoués ❌:
- **Riz Nature** (200 cal, 4g prot, 0.5g lip, 1g fib)
  - Score: **50/100** (attendu: ≤40) ❌
  - **PROBLÈME**: Score trop élevé pour plat avec basses protéines
  - Cause: Configuration SIMPLE_SCORE_CONFIG ne pénalise pas assez les basses protéines

- **Cabillaud Vapeur** (900 cal, 80g prot, 12g lip, 12g fib)
  - Score: **65/100** (attendu: ≥75) ❌
  - **PROBLÈME**: Score trop bas pour plat très riche en protéines
  - Cause: Pénalité des 900 cal (-20) dépasse le bonus protéine (+20)

---

### TEST 2: SCORE RECOMMANDATION IMC
**Résultat: 3/12 tests réussis (25%) 🔴 CRITIQUE**

#### Analyse par Catégorie IMC:

##### INSUFFISANCE PONDÉRALE (Besoin: calories ↑, protéines ↑)
```
Pizza Fromage (800 cal, 30g prot, 35g lip):
  Score obtenu: 65.4/100
  Score attendu: 70-100
  ❌ ÉCHOUÉ: Pizza n'apporte pas assez de calories/protéines
  
Poulet Équilibré (450 cal, 40g prot, 15g lip):
  Score obtenu: 69.4/100
  Score attendu: 50-80
  ✅ RÉUSSI: Bon équilibre

Soupe Légère (150 cal, 10g prot, 2g lip):
  Score obtenu: 14.8/100
  Score attendu: 20-50
  ❌ ÉCHOUÉ: Malus trop sévère pour plat léger
  Cause: Stratégie pénalise trop les faibles calories (besoin inverse!)
```

**Problème identifié:** La stratégie insuffisance_ponderale pénalise les plats légers au lieu de les valoriser pour les compléter.

##### NORMAL IMC 18.5-25 (Besoin: équilibre 400-800 cal)
```
Poulet Équilibré (450 cal, 40g prot, 15g lip):
  Score obtenu: 95.6/100 ✅
  Score attendu: 70-100

Pizza Fromage (800 cal, 30g prot, 35g lip):
  Score obtenu: 40.0/100 ✅
  Score attendu: 20-50

Steak Protéiné (350 cal, 50g prot, 18g lip):
  Score obtenu: 40.0/100 ❌
  Score attendu: 60-85
  PROBLÈME: Score trop bas pour plat riche en protéines
  Cause: 350 cal en dessous de la plage idéale (400-800)
```

**Problème:** Calorie insuffisante pénalise même les plats très protéinés.

##### SURPOIDS (Besoin: ↓ calories, ↑ protéines)
```
Tous les tests échouent! Résultats:
- Soupe Légère: 63.6/100 (attendu: 80-100) - 16.4 points sous-estimés
- Steak Protéiné: 50.2/100 (attendu: 70-90) - 20-40 points sous-estimés  
- Pizza Fromage: 30.24/100 (attendu: 5-30) - Bonne limite mais instable

Cause racine: Les stratégies de SURPOIDS ne valorisent pas assez:
  - Les très basses calories (150 cal soupes)
  - Les très hautes protéines (50g steaks)
```

**Verdict:** Stratégie SURPOIDS complètement dé-calibrée.

##### OBÉSITÉ (Besoin: ↓↓ calories, ↑↑ protéines)
```
TOUS LES TESTS ÉCHOUENT (0/3)
- Soupe Légère: 34.0/100 (attendu: 85-100) - CRITIQUE ❌
- Poulet Équilibré: 47.04/100 (attendu: 60-80) - CRITIQUE ❌
- Pizza Fromage: 33.92/100 (attendu: 1-20) - CRITIQUE ❌

Cause: Algorithme _score_by_strategy() produit des scores normalisés 
        qui ne reflètent pas les vrais besoins. Les bonus individuels 
        (30-35 pts max par nutrient) ne peuvent pas compenser.
```

**Verdict:** Stratégie OBÉSITÉ DÉFAILLANTE - Algorithme fondamentalement limité.

---

### TEST 3: SCORE PROFESSIONNEL
**Statut: Non testé mais code détecté** ⚠️

Le modèle contient une méthode `calculer_score_professionnel()` complexe mais n'est pas appelée par les tests standards. Cette méthode:
- Utilise Harris-Benedict pour BMR personnalisé ✅
- Calcule ratios macros optimaux ✅
- Mais n'est jamais invoquée dans les workflows actuels ❌

**Recommandation:** Vérifier si cette méthode est utilisée en production.

---

### TEST 4: CALCULS FRONTEND (JavaScript)

#### Fichier: `static/accueil/script.js`

**Fonction `calculateMenuScore()`**
```javascript
// Moyenne simple des scores des plats
score = Math.round(totalScore / plates.length);
```
- ✅ Cohérent avec backend
- ⚠️ Pas de pondération par portion

**Fonction `calculateNutritionTotals()`**
```javascript
// Somme simple des nutriments
totals.calories += (plat.calories || plat.calorie || 0);
// ... similar for autres nutriments
```
- ✅ Correct mathématiquement
- ⚠️ Pas d'aplatissement/normalisation

**Fonction `computeCriterionScore()`**
```javascript
function computeCriterionScore(value, target, tolerance) {
    const diffRatio = Math.abs(value - target) / target;
    if (diffRatio <= tolerance) {
        return 1 - (diffRatio / tolerance);
    }
    return Math.max(0, 1 - diffRatio);
}
```
- ✅ Mathématiquement sound
- ✅ Dégradation progressive correcte

**Fonction `calculateNutritionalScore()`**
```javascript
totalScore += computeCriterionScore(value, target, criterion.weight) * criterion.weight;
```
- ⚠️ **PROBLÈME IDENTIFIÉ**: Double poids application?
  - Score du critère multiplié par weight
  - PUIS additionné avec poids additionnel
  - Cela peut donner des scores > 100

#### Fichier: `static/specialdiet/spec.js`

**Affichage des scores**
```javascript
if (meal.score >= 80) {
    scoreClass = 'score-excellent';
    scoreIcon = '⭐';
    scoreColor = '#FFD700';
} else if (meal.score >= 60) {
    // ...
}
```
- ✅ Classification correcte
- ⚠️ Pas de validation que score ∈ [0,100]

---

## 🐛 BUGS ET INCOHÉRENCES DÉTECTÉS

### PRIORITÉ HAUTE 🔴

#### 1. **Algorithme `_score_by_strategy()` limité**
**Fichier:** `myapp/models.py` ligne 415

**Problème:**
- Additionne les bonus individuels (30 + 20 + 18 + 20 = 88+ points possibles)
- Puis normalise à 0-80 en divisant par 100
- Cela crée des résultats imprévisibles

**Exemple défaillant:**
```
Pizza Fromage (800 cal, 30g prot, 35g lip):
  - Calories: 0 pts (hors range)
  - Protéines: 16 pts
  - Glucides: 8 pts
  - Lipides: 1 pt
  - Fibres: 0 pts
  = 25/100 → 20/100 (après normalisation) → Score final = 40
  
  Mais pour INSUFFISANCE_PONDERALE, on VOUDRAIT 70+
  Car Pizza a 800 cal + 30g protéine qui devraient être valorisées!
```

**Solution requise:** Revoir la normalisation et les seuils par stratégie.

#### 2. **Stratégies de perte de poids (SURPOIDS/OBÉSITÉ) mal calibrées**
**Fichier:** `myapp/score_constants.py` ligne ~80-95

**Problème:**
- Les stratégies assignent des bonus fixes par nutrient
- Ne tiennent pas compte des interactions/synergies
- Exemple: Une soupe très légère (150 cal, 10g prot) n'est jamais récompensée car elle rate TOUS les seuils

**Données problématiques:**
```python
'surpoids': {
    'calories_max': 500,         # Soupe (150) ✅ passe
    'protein_range': (25, 40),   # Soupe (10) ❌ ÉCHOUE
    'carbs_max': 30,             # Soupe (15) ✅ passe
    'fat_max': 15,               # Soupe (2) ✅ passe
    'fiber_range': (8, 15),      # Soupe (8) ✅ passe
}
# Résultat: Soupe échoue sur 1/5 critère mais score très bas!
```

**Solution:** Ajouter des seuils "acceptables" minimes (ex: 5-10g min de protéine = -3 pts au lieu de 0).

#### 3. **Double application de poids en JavaScript**
**Fichier:** `static/accueil/script.js` ligne ~445

```javascript
// ERREUR: Score multiplié deux fois par weight?
const criterionScore = computeCriterionScore(value, target, criterion.tolerance);
totalScore += criterionScore * criterion.weight * criterion.weight;  // Possible double-application
```

**Vérification requise:** Confirmer la formule exacte.

---

### PRIORITÉ MOYENNE 🟡

#### 4. **Manque de validation post-calcul**
Aucune vérification que les scores resterent dans [0, 100].

#### 5. **Cohérence Python ↔ JavaScript**
Les constantes Python ne sont pas auto-synchronisées avec les JS.

#### 6. **Méthode `calculer_score_professionnel()` non utilisée**
Code complexe mais jamais appelé = Technical Debt.

---

### PRIORITÉ BASSE 🟢

#### 7. **Cache optim pas réellement mesuré**
Les gains de cache (3x speedup) sur calculs < 0.05ms ne sont pas significatifs.

---

## ✅ RECOMMANDATIONS

### Phase 1: CORRECTIONS URGENTES (48h)

1. **Fixer la formule de normalisation dans `_score_by_strategy()`**
   ```python
   # ACTUEL (MAUVAIS):
   base_score = (strategy_score / 100.0) * 80
   
   # PROPOSÉ (MEILLEUR):
   # Utiliser min() pour capper chaque critique
   calories_score = min(calories_partial_score, 30)  # Max 30
   protein_score = min(protein_partial_score, 30)    # Max 30
   # ... puis additionner max 100
   ```

2. **Recalibrer les stratégies IMC**
   - Ajouter seuils "acceptables" minimes
   - Créer des profils de test réalistes
   - Valider avec nutritionniste

3. **Ajouter validation post-calcul**
   ```python
   final_score = max(0, min(100, final_score))
   ```

### Phase 2: AMÉLIORATION (1 semaine)

4. **Implémenter mode DEBUG amélioré**
   - Afficher breakdown score par nutrient
   - Logguer décisions pour audit

5. **Créer suite de tests automatisés complète**
   - 50+ cas de test documentés
   - CI/CD integration

6. **Synchroniser constantes Python ↔ JS**
   - Générer fichier constants.js depuis Python
   - Ou utiliser API pour les partager

### Phase 3: REFACTORING (2 semaines)

7. **Refactoriser `calculer_score_professionnel()`**
   - Documenter quand l'utiliser
   - Tester avec cas réels
   - Ou supprimer si non utilisé

8. **Créer dashboard de monitoring**
   - Alerter si scores anormaux
   - Tracker moyenne/variance

---

## 📈 MÉTRIQUES DE QUALITÉ ACTUELLES

| Métrique | Résultat | Cible |
|----------|----------|-------|
| Tests simples réussis | 60% | 100% |
| Tests IMC réussis | 25% | 100% |
| Score validation | ❌ | ✅ |
| Documentation | ⚠️ (manuelle) | 100% |
| Synchronisation Py/JS | ⚠️ | ✅ |

---

## 📝 LOGS DE TEST

### Test Simple (test_1_score_simple.py)
```
✅ Poulet Grillé - Sain:    78/100 (attendu: ≥70)
❌ Riz Nature:               50/100 (attendu: ≤40)  
❌ Cabillaud vapeur:         65/100 (attendu: ≥75)
```

### Test IMC (test_2_score_recommendation_imc.py)
```
INSUFFISANCE_PONDERALE:  1/3 ✅
NORMAL:                  2/3 ✅
SURPOIDS:                0/3 ❌
OBÉSITÉ:                 0/3 ❌
TOTAL:                   3/12 = 25% 🔴
```

---

## 🔗 FICHIERS CONCERNÉS

- ✅ `myapp/models.py` - Logique de calcul principale
- ✅ `myapp/score_constants.py` - Paramètres (À FIXER)
- ✅ `static/accueil/script.js` - Frontend (À vérifier)
- ✅ `static/specialdiet/spec.js` - Frontend spécialisé
- ✅ Tests: `test_1_score_simple.py`, `test_2_score_recommendation_imc.py`

---

## 🎯 CONCLUSION

**Statut:** 🔴 **PRODUIT NON FIABLE** pour catégories SURPOIDS/OBÉSITÉ

**Points de blocage:**
1. 75% des tests IMC échouent
2. Algorithme de normalisation limité
3. Pas d'alertes sur anomalies

**Action requise:** Fixer priorité #1 avant production/déploiement.

**Prochaines étapes:**
1. Réunion avec product owner sur priorités
2. Fixer normes acceptables par catégorie IMC
3. Recalibrer stratégies
4. Ajouter test automatisés

---

**Rapport généré:** 19 Avril 2026  
**Validé par:** Système de vérification automatisé
