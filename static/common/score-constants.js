/**
 * ========== CONSTANTES CENTRALISÉES POUR TOUS LES CALCULS DE SCORE ==========
 * Ce fichier centralise tous les paramètres de scoring nutritionnel côté frontend
 * À synchroniser avec score_constants.py du backend
 */

// ========== CONSTANTES DE SCORE MENU (avec macros) ==========
const MENU_SCORE_CONFIG = {
    PROTEIN_MAX: 50,
    PROTEIN_REF: 50,
    FIBER_MAX: 20,
    FIBER_REF: 30,
    BALANCE_MAX: 30,
    BALANCE_PENALTY: 50,
    IDEAL_RATIOS: { carbs: 0.4, protein: 0.3, fat: 0.3 },
    CALS_PER_CARB: 4,
    CALS_PER_PROTEIN: 4,
    CALS_PER_FAT: 9
};

// ========== CONSTANTES DE SCORE NUTRITIONNEL SIMPLE (Plat) ==========
const SIMPLE_SCORE_CONFIG = {
    base: 50,
    protein: {
        high_threshold: 30,
        high_bonus: 20,
        medium_threshold: 20,
        medium_bonus: 10,
    },
    calories: {
        high_threshold: 800,
        high_malus: 20,
        medium_threshold: 600,
        medium_malus: 10,
    },
    fiber: {
        high_threshold: 10,
        high_bonus: 15,
        medium_threshold: 5,
        medium_bonus: 8,
    },
    fat: {
        high_threshold: 30,
        high_malus: 15,
        medium_threshold: 20,
        medium_malus: 8,
    }
};

// ========== CACHE GLOBAL ==========
const GLOBAL_SCORE_CACHE = new Map();

/**
 * Récupère un score du cache global
 */
function getGlobalCachedScore(key) {
    return GLOBAL_SCORE_CACHE.get(key);
}

/**
 * Stocke un score dans le cache global
 */
function setGlobalCachedScore(key, value) {
    GLOBAL_SCORE_CACHE.set(key, value);
    return value;
}

/**
 * Vide le cache global
 */
function clearGlobalScoreCache() {
    GLOBAL_SCORE_CACHE.clear();
}

/**
 * Stocke la taille du cache
 */
function getGlobalCacheSize() {
    return GLOBAL_SCORE_CACHE.size;
}
