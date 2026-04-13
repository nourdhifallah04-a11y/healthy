// Initialize Bootstrap dropdowns
document.addEventListener('DOMContentLoaded', function() {
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(function(element) {
        new bootstrap.Dropdown(element);
    });
});

// ========== DONNÉES DES PLATS PAR CATÉGORIE DIET ==========
// Données par défaut (fallback)
let dietMeals = {
    "high-protein": [],
    "low-carb": [],
    "vegan": [],
    "gluten-free": [],
    "plat-recommander": []
};

/**
 * Transforme un objet Plat depuis l'API en objet meal pour l'affichage
 * @param {Object} plat - Objet plat reçu de l'API
 * @returns {Object} Objet meal formaté
 */
function transformerPlatEnMealDiet(plat) {
    return {
        id: plat.id_plat || plat.id,
        name: plat.nom,
        calories: plat.calorie,
        protein: plat.proteine,
        carbs: plat.glucides,
        fat: plat.lipides,
        fiber: plat.fibres,
        image: plat.image ? plat.image : "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        description: plat.description,
        score: plat.score || 0  // Ajouter le score depuis l'API
    };
}

/**
 * Catégorise les plats par type de régime
 * @param {Array} plats - Liste des plats
 * @returns {Object} Plats organisés par catégorie diet
 */
function categoriserPlatsByDiet(plats) {
    const categorized = {
        "high-protein": [],
        "low-carb": [],
        "vegan": [],
        "gluten-free": []
    };

    plats.forEach(meal => {
        // High-protein: protéine >= 35g
        if (meal.protein >= 35) {
            categorized["high-protein"].push(meal);
        }
        
        // Low-carb: glucides <= 20g
        if (meal.carbs <= 20) {
            categorized["low-carb"].push(meal);
        }
        
        // Gluten-free: catégorisé par défaut (tous les plats)
        categorized["gluten-free"].push(meal);
        
        // Vegan: peut être déterminé par un champ dans l'API ou par description
        if (meal.description && (meal.description.toLowerCase().includes('vegan') || 
            meal.description.toLowerCase().includes('végétal') ||
            meal.description.toLowerCase().includes('sans produit animal'))) {
            categorized["vegan"].push(meal);
        }
    });

    return categorized;
}

/**
 * Charge les plats depuis l'API et les organise par régime
 */
function chargerDietMeals() {
    // Charger les plats par catégorie
    fetch('/api/plats/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Données brutes reçues de l\'API:', data);
            
            // Adapter les données de l'API au format attendu
            const platsArray = Array.isArray(data) ? data : (data.results || []);
            
            // Filtrer les plats disponibles uniquement et transformer
            const mealsFormatted = platsArray
                .filter(plat => plat.est_disponible === true)
                .map(plat => transformerPlatEnMealDiet(plat));
            
            // Catégoriser les plats par type de régime
            dietMeals = categoriserPlatsByDiet(mealsFormatted);
            
            // Charger aussi les plats recommandés basés sur le profil
            chargerPlatsRecommandes();
            console.log('✅ Régimes spéciaux chargés avec succès depuis l\'API !', dietMeals);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des régimes spéciaux:', error);
            // Fallback: afficher un message d'erreur
            if (dietGrid) {
                dietGrid.innerHTML = `<div class="no-results">⚠️ Erreur lors du chargement des plats</div>`;
            }
        });
}

/**
 * Charge les plats recommandés basés sur le profil nutritionnel de l'utilisateur
 */
function chargerPlatsRecommandes() {
    fetch('/api/profil-nutritionnel/recommander-plats/')
        .then(response => {
            // Si l'utilisateur n'est pas authentifié (401), c'est normal
            if (response.status === 401) {
                console.log('ℹ️ Utilisateur non authentifié pour les recommandations');
                dietMeals["plat-recommander"] = [];
                displayDietMeals();
                return;
            }
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            console.log('Plats recommandés reçus:', data);
            
            // Adapter les données au format plat
            const platsArray = Array.isArray(data) ? data : (data.results || []);
            
            // Transformer les plats
            const mealsFormatted = platsArray.map(plat => transformerPlatEnMealDiet(plat));
            
            // Ajouter au dictionnaire des régimes
            dietMeals["plat-recommander"] = mealsFormatted;
            
            // Afficher si c'est la catégorie active
            if (currentDiet === "plat-recommander") {
                displayDietMeals();
            }
            console.log('✅ Plats recommandés chargés avec succès !', mealsFormatted);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des plats recommandés:', error);
            dietMeals["plat-recommander"] = [];
        });
}

// ========== VARIABLES GLOBALES ==========
let currentDiet = "high-protein";

// ========== RÉFÉRENCES DOM ==========
const dietGrid = document.getElementById('dietGrid');
const dietCards = document.querySelectorAll('.diet-card');
const selectedDietSpan = document.getElementById('selectedDiet');

// ========== DICTIONNAIRE DES NOMS DE RÉGIMES ==========
const dietNames = {
    "high-protein": "High Protein",
    "low-carb": "Low Carb",
    "vegan": "Vegan",
    "gluten-free": "Sans Gluten",
    "plat-recommander": "Votre profil nutritionnel"
};

// ========== FONCTION POUR AFFICHER LES PLATS ==========
function displayDietMeals() {
    if (!dietGrid) return;

    const meals = dietMeals[currentDiet] || [];
    const dietName = dietNames[currentDiet] || currentDiet;

    // Mettre à jour le titre
    if (selectedDietSpan) {
        selectedDietSpan.textContent = dietName;
    }

    // Affichage des résultats
    if (meals.length === 0) {
        dietGrid.innerHTML = `<div class="no-results">🍽️ Aucun plat disponible pour cette catégorie</div>`;
        return;
    }

    dietGrid.innerHTML = meals.map(meal => {
        // Déterminer la couleur du score
        let scoreClass = 'score-low';
        let scoreIcon = '😢';
        
        if (meal.score >= 80) {
            scoreClass = 'score-excellent';
            scoreIcon = '⭐';
        } else if (meal.score >= 60) {
            scoreClass = 'score-good';
            scoreIcon = '👍';
        } else if (meal.score >= 40) {
            scoreClass = 'score-ok';
            scoreIcon = '😐';
        } else if (meal.score > 0) {
            scoreClass = 'score-low';
            scoreIcon = '😐';
        }
        
        return `
        <div class="meal-card">
            <div class="meal-img">
                <img src="${meal.image}" alt="${meal.name}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                <div class="badge-diet">${dietName}</div>
                <div class="prot-circle">${meal.protein}g <span>PROT</span></div>
                ${meal.score > 0 ? `<div class="score-badge ${scoreClass}">
                    <div class="score-value">${meal.score.toFixed(1)}</div>
                    <div class="score-label">Score</div>
                    <div class="score-icon">${scoreIcon}</div>
                </div>` : ''}
            </div>
            <div class="meal-body">
                <h3>${meal.name}</h3>
                <div class="nutri-table">
                    <div class="nutri-item">
                        <span>🔥 Calories</span>
                        ${meal.calories} kcal
                    </div>
                    <div class="nutri-item">
                        <span>💪 Protéines</span>
                        ${meal.protein}g
                    </div>
                    <div class="nutri-item">
                        <span>🍚 Glucides</span>
                        ${meal.carbs}g
                    </div>
                </div>
            </div>
        </div>
    `}).join('');
}

// ========== GESTION DES CATÉGORIES DIET ==========
if (dietCards.length > 0) {
    dietCards.forEach(card => {
        card.addEventListener('click', () => {
            // Mettre à jour la classe active
            dietCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            // Mettre à jour le régime actuel
            currentDiet = card.dataset.diet;
            
            // Animation de transition
            if (dietGrid) {
                dietGrid.style.opacity = '0';
                setTimeout(() => {
                    displayDietMeals();
                    dietGrid.style.opacity = '1';
                }, 200);
            } else {
                displayDietMeals();
            }
        });
    });
}

// ========== MENU MOBILE ==========
const mobileMenu = document.getElementById('mobileMenu');
const navLinks = document.querySelector('.nav-links');

if (mobileMenu && navLinks) {
    mobileMenu.addEventListener('click', () => {
        navLinks.classList.toggle('show');
    });
}

// ========== FERMER LE MENU MOBILE AU CLIC SUR UN LIEN ==========
const navItems = document.querySelectorAll('.nav-links a');
navItems.forEach(item => {
    item.addEventListener('click', () => {
        if (window.innerWidth <= 768 && navLinks) {
            navLinks.classList.remove('show');
        }
    });
});

// ========== CHARGEMENT INITIAL ==========
document.addEventListener('DOMContentLoaded', () => {
    chargerDietMeals();
    console.log('🌿 Special Diet Fresh & Greens chargé avec succès !');
});
