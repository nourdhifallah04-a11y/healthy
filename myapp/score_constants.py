# ========== CONSTANTES CENTRALISÉES POUR TOUS LES CALCULS DE SCORE ==========
# Ce fichier centralise tous les paramètres de scoring nutritionnel pour l'application

from typing import Dict

# ========== CONSTANTES DE SCORE NUTRITIONNEL SIMPLE (Plat) ==========
SIMPLE_SCORE_CONFIG = {
    'base': 50,
    'protein': {
        'high_threshold': 30,
        'high_bonus': 20,
        'medium_threshold': 20,
        'medium_bonus': 10,
    },
    'calories': {
        'high_threshold': 800,
        'high_malus': 20,
        'medium_threshold': 600,
        'medium_malus': 10,
    },
    'fiber': {
        'high_threshold': 10,
        'high_bonus': 15,
        'medium_threshold': 5,
        'medium_bonus': 8,
    },
    'fat': {
        'high_threshold': 30,
        'high_malus': 15,
        'medium_threshold': 20,
        'medium_malus': 8,
    }
}

# ========== CONSTANTES DE SCORE MENU (avec macros) ==========
MENU_SCORE_CONFIG = {
    'PROTEIN_MAX': 50,
    'PROTEIN_REF': 50,
    'FIBER_MAX': 20,
    'FIBER_REF': 30,
    'BALANCE_MAX': 30,
    'BALANCE_PENALTY': 50,
    'IDEAL_RATIOS': {'carbs': 0.4, 'protein': 0.3, 'fat': 0.3},
    'CALS_PER_CARB': 4,
    'CALS_PER_PROTEIN': 4,
    'CALS_PER_FAT': 9
}

# ========== STRATÉGIES PAR CATÉGORIE IMC ==========
BMI_STRATEGIES = {
    'insuffisance_ponderale': {
        'label': 'INSUFFISANCE PONDÉRALE',
        'calories_min': 1000,
        'calories_ideal_bonus': 25,
        'protein_ideal': 40,
        'protein_bonus': 25,
        'carbs_ideal': 50,
        'carbs_bonus': 20,
        'fat_ideal': 30,
        'fat_bonus': 15,
        'fiber_ideal': 10,
        'fiber_bonus': 15,
    },
    'normal': {
        'label': 'NORMAL',
        'calories_range': (400, 800),
        'calories_bonus': 20,
        'protein_range': (20, 35),
        'protein_bonus': 25,
        'carbs_range': (30, 50),
        'carbs_bonus': 20,
        'fat_range': (10, 25),
        'fat_bonus': 15,
        'fiber_range': (5, 12),
        'fiber_bonus': 20,
    },
    'surpoids': {
        'label': 'SURPOIDS',
        'calories_max': 500,
        'calories_bonus': 30,
        'protein_range': (25, 40),
        'protein_bonus': 30,
        'carbs_max': 30,
        'carbs_bonus': 18,
        'fat_max': 15,
        'fat_bonus': 20,
        'fiber_range': (8, 15),
        'fiber_bonus': 18,
    },
    'obesite': {
        'label': 'OBÉSITÉ',
        'calories_max': 400,
        'calories_bonus': 35,
        'protein_min': 30,
        'protein_bonus': 35,
        'carbs_max': 25,
        'carbs_bonus': 15,
        'fat_max': 10,
        'fat_bonus': 25,
        'fiber_min': 10,
        'fiber_bonus': 20,
    }
}

# ========== PROFILS PAR ÂGE ET SEXE ==========
AGE_GENDER_PROFILES = {
    # JEUNES (< 20 ans)
    'femme_jeune': {
        'label': 'Femme - Jeune (< 20 ans)',
        'age_range': (0, 20),
        'sexe': 'femme',
        'calories_factor': 1.1,  # Besoins énergétiques élevés
        'protein_factor': 1.0,   # Protéines normales
        'preferred_calories_min': 600,
        'preferred_calories_max': 900,
        'preferred_protein_min': 25,
        'preferred_protein_max': 50,
        'preferred_fiber_min': 6,
        'prefer_carbs': True,  # Besoin énergétique
        'energy_bonus': 15,  # Bonus significatif pour calories adéquates
    },
    'homme_jeune': {
        'label': 'Homme - Jeune (< 20 ans)',
        'age_range': (0, 20),
        'sexe': 'homme',
        'calories_factor': 1.2,  # Besoins énergétiques très élevés
        'protein_factor': 1.15,  # Protéines importantes pour croissance
        'preferred_calories_min': 700,
        'preferred_calories_max': 1100,
        'preferred_protein_min': 30,
        'preferred_protein_max': 60,
        'preferred_fiber_min': 6,
        'prefer_carbs': True,
        'energy_bonus': 18,
        'protein_bonus': 12,
    },
    # ADULTES (20-49 ans)
    'femme_adulte': {
        'label': 'Femme - Adulte (20-49 ans)',
        'age_range': (20, 50),
        'sexe': 'femme',
        'calories_factor': 1.0,
        'protein_factor': 0.95,
        'preferred_calories_min': 400,
        'preferred_calories_max': 700,
        'preferred_protein_min': 20,
        'preferred_protein_max': 35,
        'preferred_fiber_min': 7,
        'prefer_balanced': True,
        'energy_bonus': 8,
    },
    'homme_adulte': {
        'label': 'Homme - Adulte (20-49 ans)',
        'age_range': (20, 50),
        'sexe': 'homme',
        'calories_factor': 1.05,
        'protein_factor': 1.05,
        'preferred_calories_min': 500,
        'preferred_calories_max': 850,
        'preferred_protein_min': 25,
        'preferred_protein_max': 45,
        'preferred_fiber_min': 7,
        'prefer_balanced': True,
        'protein_bonus': 10,
        'energy_bonus': 5,
    },
    # SENIORS (>= 50 ans)
    'femme_senior': {
        'label': 'Femme - Senior (>= 50 ans)',
        'age_range': (50, 120),
        'sexe': 'femme',
        'calories_factor': 0.9,  # Besoins réduits
        'protein_factor': 1.1,   # Protéines importantes (prévention sarcopénie)
        'preferred_calories_min': 350,
        'preferred_calories_max': 600,
        'preferred_protein_min': 22,
        'preferred_protein_max': 40,
        'preferred_fiber_min': 8,
        'prefer_fiber': True,  # Santé digestive importante
        'protein_bonus': 15,
        'fiber_bonus': 12,
    },
    'homme_senior': {
        'label': 'Homme - Senior (>= 50 ans)',
        'age_range': (50, 120),
        'sexe': 'homme',
        'calories_factor': 0.95,
        'protein_factor': 1.15,
        'preferred_calories_min': 400,
        'preferred_calories_max': 700,
        'preferred_protein_min': 25,
        'preferred_protein_max': 45,
        'preferred_fiber_min': 8,
        'prefer_fiber': True,
        'protein_bonus': 18,
        'fiber_bonus': 14,
    }
}

# ========== RESTRICTIONS ALIMENTAIRES ==========
DIETARY_RESTRICTIONS = {
    'vegetarien': {
        'keywords': ['viande', 'poulet', 'boeuf', 'poisson', 'saumon', 'thon', 'canard']
    },
    'vegane': {
        'keywords': ['viande', 'poulet', 'boeuf', 'poisson', 'oeuf', 'lait', 'fromage', 'beurre', 'creme', 'yaourt']
    },
    'sans gluten': {
        'keywords': ['blé', 'gluten', 'pain', 'pate', 'biscuit', 'cereale']
    },
    'sans lactose': {
        'keywords': ['lait', 'fromage', 'beurre', 'creme', 'yaourt']
    }
}

# Cache pour optimiser les calculs répétés
_score_cache: Dict = {}

def get_cached_score(key: str, compute_func=None):
    """Récupère un score du cache ou le calcule et le met en cache"""
    if key in _score_cache:
        return _score_cache[key]
    
    if compute_func:
        value = compute_func()
        _score_cache[key] = value
        return value
    
    return None

def clear_score_cache():
    """Vide le cache de scores"""
    global _score_cache
    _score_cache.clear()

def set_cached_score(key: str, value):
    """Stocke un score en cache"""
    _score_cache[key] = value

def get_age_gender_profile(age: int = None, sexe: str = None) -> Dict:
    """
    Retourne le profil d'âge/sexe approprié
    
    Args:
        age: Âge de la personne (0-120)
        sexe: 'homme' ou 'femme'
    
    Returns:
        Dict avec les paramètres du profil ou profil par défaut
    """
    if not age or not sexe:
        return AGE_GENDER_PROFILES.get('homme_adulte', {})
    
    sexe_lower = sexe.lower().strip()
    
    # Déterminer le groupe d'âge
    if age < 20:
        age_group = 'jeune'
    elif age < 50:
        age_group = 'adulte'
    else:
        age_group = 'senior'
    
    # Construire la clé du profil
    if sexe_lower.startswith('f'):
        profile_key = f'femme_{age_group}'
    else:
        profile_key = f'homme_{age_group}'
    
    return AGE_GENDER_PROFILES.get(profile_key, AGE_GENDER_PROFILES.get('homme_adulte', {}))
