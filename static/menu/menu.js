// ========== DONNÉES DES PLATS (MENU COMPLET) - CHARGÉ DYNAMIQUEMENT ==========
let meals = [];
let menus = [];

// ========== CONSTANTES D'OPTIMISATION DU SCORE ==========
const SCORE_CONSTANTS = {
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

// Cache pour éviter les recalculs
const scoreCache = new Map();

/**
 * Calcule le score nutritionnel du menu (optimisé)
 * Score basé sur : protéines (priorité haute), fibres, équilibre macros
 * @param {number} protein - Protéines totales en grammes
 * @param {number} fiber - Fibres totales en grammes
 * @param {number} carbs - Glucides totaux en grammes
 * @param {number} fat - Lipides totaux en grammes
 * @returns {number} Score du menu (0-100)
 */
function calculerScoreMenu(protein, fiber, carbs, fat) {
    // Clé de cache
    const cacheKey = `${protein},${fiber},${carbs},${fat}`;
    if (scoreCache.has(cacheKey)) {
        return scoreCache.get(cacheKey);
    }
    
    // Score protéine (max 50 points)
    const scoreProtein = Math.min(SCORE_CONSTANTS.PROTEIN_MAX, protein * (SCORE_CONSTANTS.PROTEIN_MAX / SCORE_CONSTANTS.PROTEIN_REF));
    
    // Score fibre (max 20 points)
    const scoreFiber = Math.min(SCORE_CONSTANTS.FIBER_MAX, fiber * (SCORE_CONSTANTS.FIBER_MAX / SCORE_CONSTANTS.FIBER_REF));
    
    // Score d'équilibre macro (max 30 points)
    const totalCals = (carbs * SCORE_CONSTANTS.CALS_PER_CARB) + 
                      (protein * SCORE_CONSTANTS.CALS_PER_PROTEIN) + 
                      (fat * SCORE_CONSTANTS.CALS_PER_FAT);
    
    let scoreBalance = SCORE_CONSTANTS.BALANCE_MAX;
    if (totalCals > 0) {
        const carbsRatio = (carbs * SCORE_CONSTANTS.CALS_PER_CARB) / totalCals;
        const proteinRatio = (protein * SCORE_CONSTANTS.CALS_PER_PROTEIN) / totalCals;
        const fatRatio = (fat * SCORE_CONSTANTS.CALS_PER_FAT) / totalCals;
        
        const distance = Math.abs(carbsRatio - SCORE_CONSTANTS.IDEAL_RATIOS.carbs) + 
                         Math.abs(proteinRatio - SCORE_CONSTANTS.IDEAL_RATIOS.protein) + 
                         Math.abs(fatRatio - SCORE_CONSTANTS.IDEAL_RATIOS.fat);
        
        scoreBalance = Math.max(0, SCORE_CONSTANTS.BALANCE_MAX - (distance * SCORE_CONSTANTS.BALANCE_PENALTY));
    }
    
    // Score total (0-100)
    const totalScore = Math.min(100, Math.round(scoreProtein + scoreFiber + scoreBalance));
    
    // Mise en cache du résultat
    scoreCache.set(cacheKey, totalScore);
    return totalScore;
}

/**
 * Transforme un objet Plat depuis l'API en objet meal pour l'affichage
 * @param {Object} plat - Objet plat reçu de l'API
 * @returns {Object} Objet meal formaté
 */
function transformerPlatEnMeal(plat) {
    return {
        id: plat.id_plat || plat.id,
        name: plat.nom,
        calories: plat.calorie,
        protein: plat.proteine,
        carbs: plat.glucides,
        fat: plat.lipides,
        fiber: plat.fibres,
        category: plat.proteine >= 35 ? "proteine" : "autre",
        image: plat.image ? plat.image : "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        isNew: plat.isNew,
        prix: plat.prix ? parseFloat(plat.prix) : null,
        description: plat.description,
        est_disponible: plat.est_disponible,
        type: 'plat'
    };
}

/**
 * Transforme un objet Menu depuis l'API en objet meal pour l'affichage
 * @param {Object} menu - Objet menu reçu de l'API
 * @returns {Object} Objet meal formaté
 */
function transformerMenuEnMeal(menu) {
    // Calculer les totaux nutritionnels et le prix depuis les plats
    let totalCalories = 0, totalProtein = 0, totalCarbs = 0, totalFat = 0, totalFiber = 0, totalPrix = 0;
    
    if (menu.plats && menu.plats.length > 0) {
        menu.plats.forEach(plat => {
            totalCalories += plat.calorie || 0;
            totalProtein += plat.proteine || 0;
            totalCarbs += plat.glucides || 0;
            totalFat += plat.lipides || 0;
            totalFiber += plat.fibres || 0;
            totalPrix += plat.prix ? parseFloat(plat.prix) : 0;
        });
    }
    
    return {
        id: menu.id_menu || menu.id,
        name: menu.nom,
        calories: totalCalories,
        protein: totalProtein,
        carbs: totalCarbs,
        fat: totalFat,
        fiber: totalFiber,
        category: totalProtein >= 35 ? "proteine" : "autre",
        image: menu.image ? menu.image : "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        isNew: menu.isNew,
        prix: totalPrix > 0 ? totalPrix : (menu.prix ? parseFloat(menu.prix) : null),
        description: menu.description,
        est_disponible: menu.est_disponible,
        type: 'menu',
        plats: menu.plats || [],
        score: calculerScoreMenu(totalProtein, totalFiber, totalCarbs, totalFat)
    };
}

/**
 * Charge les menus depuis l'API et les affiche
 */
function chargerPlats() {
    fetch('/menu/api/menus/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(menusData => {
            console.log('Données brutes reçues de l\'API - Menus:', menusData);
            
            // Adapter les données de l'API au format attendu par displayMeals
            const menusArray = Array.isArray(menusData) ? menusData : (menusData.results || []);
                console.log('Données transformées - Menus:', menusArray);
            // Filtrer et transformer les menus disponibles
            meals = menusArray
                .filter(menu => menu.est_actif === true)
                .map(menu => transformerMenuEnMeal(menu));
            
            // Afficher les menus après le chargement
            displayMeals();
            console.log('✓ Menus chargés avec succès !', meals);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des menus:', error);
            // Fallback: afficher un message d'erreur
            if (menuGrid) {
                menuGrid.innerHTML = `<div class="no-results">⚠️ Erreur lors du chargement des menus</div>`;
            }
        });
}

// ========== VARIABLES GLOBALES ==========
let currentFilter = "all";
let currentSearch = "";

// ========== RÉFÉRENCES DOM ==========
const menuGrid = document.getElementById('menuGrid');
const searchInput = document.getElementById('searchInput');
const filterBtns = document.querySelectorAll('.filter-btn');

// ========== FONCTION POUR AFFICHER LES MENUS ==========
function displayMeals() {
    if (!menuGrid) return;

    let filteredMeals = [...meals];

    // Filtre par catégorie
    if (currentFilter === "nouveau") {
        filteredMeals = filteredMeals.filter(meal => meal.isNew === true);
    } else if (currentFilter === "proteine") {
        filteredMeals = filteredMeals.filter(meal => meal.protein >= 35);
    }

    // Filtre par recherche
    if (currentSearch.trim() !== "") {
        filteredMeals = filteredMeals.filter(meal =>
            meal.name.toLowerCase().includes(currentSearch.toLowerCase())
        );
    }

    // Tri par score nutritionnel (décroissant)
    filteredMeals.sort((a, b) => (b.score || 0) - (a.score || 0));

    // Affichage des résultats
    if (filteredMeals.length === 0) {
        menuGrid.innerHTML = `<div class="no-results">🍽️ Aucun menu ne correspond à votre recherche</div>`;
        return;
    }
    console.log('Menus à afficher après filtrage:', filteredMeals);
    menuGrid.innerHTML = filteredMeals.map(meal => `
        <div class="item-card">
            <div class="item-image">
                <img src="${meal.image}" alt="${meal.name}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                <span class="item-type-badge menu">Menu</span>
                <span class="item-score">⭐ ${meal.score}/100</span>
                ${meal.isNew ? '<span class="item-badge-new">NOUVEAU</span>' : ''}
            </div>
            <div class="item-body">
                <h3>${meal.name}</h3>
                <p class="description">${meal.description || 'Menu savoureux et équilibré'}</p>
                
                ${meal.type === 'menu' && meal.plats && meal.plats.length > 0 ? `
                    <div class="menu-plats">
                        <p class="plats-label">📋 Plats:</p>
                        <ul class="plats-items">
                            ${meal.plats.map(plat => `<li>${plat.nom}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="nutrition-info">
                    <div class="nutrition-item">
                        <span class="label">🔥 Calories</span>
                        <span class="value">${Math.round(meal.calories)} kcal</span>
                    </div>
                    <div class="nutrition-item">
                        <span class="label">💪 Protéines</span>
                        <span class="value">${meal.protein.toFixed(1)}g</span>
                    </div>
                    <div class="nutrition-item">
                        <span class="label">🌾 Glucides</span>
                        <span class="value">${meal.carbs.toFixed(1)}g</span>
                    </div>
                    <div class="nutrition-item">
                        <span class="label">🧈 Lipides</span>
                        <span class="value">${meal.fat.toFixed(1)}g</span>
                    </div>
                </div>

                <div class="item-footer">
                    <span class="item-price">${meal.prix !== null && meal.prix !== undefined && !isNaN(meal.prix) ? `€${parseFloat(meal.prix).toFixed(2)}` : 'Prix sur demande'}</span>
                    <button class="btn-add-cart" data-item-id="${meal.id}" data-item-type="${meal.type}" data-item-name="${meal.name}" data-item-price="${meal.prix || '0'}">
                        <i class="fas fa-shopping-cart"></i> Ajouter
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Ajouter les événements aux boutons Ajouter au Panier
    document.querySelectorAll('.btn-add-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const itemId = btn.dataset.itemId;
            const itemType = btn.dataset.itemType;
            const itemName = btn.dataset.itemName;
            const itemPrice = btn.dataset.itemPrice;
            openAddToCartModal(itemId, itemType, itemName, itemPrice);
        });
    });
}

// ========== GESTION DES FILTRES ==========
if (filterBtns.length > 0) {
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Mettre à jour la classe active
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Mettre à jour le filtre
            currentFilter = btn.dataset.filter;
            displayMeals();
        });
    });
}

// ========== GESTION DE LA RECHERCHE ==========
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        displayMeals();
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
    // Initialize Bootstrap dropdowns
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(function(element) {
        new bootstrap.Dropdown(element);
    });
    
    // Charger les plats et menus
    chargerPlats();
    console.log('🌿 Menu Fresh & Greens chargé avec succès !');
});

// ========== GESTION MODAL AJOUTER AU PANIER ==========
let selectedMealId = null;
let selectedMealPrice = null;
let selectedMealType = null;

function openAddToCartModal(mealId, mealName, mealPrice, mealType = 'plat') {
    selectedMealId = mealId;
    selectedMealPrice = mealPrice;
    selectedMealType = mealType;
    const modal = document.getElementById('addToCartModal');
    const itemInfo = document.getElementById('itemInfo');
    const quantity = document.getElementById('quantity');
    
    const priceDisplay = mealPrice && !isNaN(parseFloat(mealPrice)) 
        ? `€${parseFloat(mealPrice).toFixed(2)}` 
        : 'Prix non disponible';
    itemInfo.textContent = `${mealName} - ${priceDisplay}`;
    quantity.value = 1;
    modal.style.display = 'block';
}

function closeAddToCartModal() {
    const modal = document.getElementById('addToCartModal');
    modal.style.display = 'none';
}

// Fermer modal si on clique en dehors
window.addEventListener('click', (e) => {
    const modal = document.getElementById('addToCartModal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Fermer modal avec le bouton X
const closeBtn = document.querySelector('.modal .close');
if (closeBtn) {
    closeBtn.addEventListener('click', closeAddToCartModal);
}

// Soumettre le formulaire
const addToCartForm = document.getElementById('addToCartForm');
if (addToCartForm) {
    addToCartForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!selectedMealId) return;
        
        const quantity = parseInt(document.getElementById('quantity').value);
        
        try {
            // Préparer le body selon le type (plat ou menu)
            const body = selectedMealType === 'menu' 
                ? {
                    menu_id: selectedMealId,
                    quantite: quantity
                }
                : {
                    menu_id: selectedMealId,
                    quantite: quantity
                };
            
            // Appel API pour ajouter au panier
            const response = await fetch('/api/ligne-commande/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'same-origin',
                body: JSON.stringify(body)
            });
            
            const data = await response.json();
            
            // Handle authentication errors (401 or 403)
            if (response.status === 401 || response.status === 403) {
                PanierManager.showError('❌ Vous devez être connecté pour ajouter au panier. Veuillez vous connecter.');
                setTimeout(() => {
                    window.location.href = '/login/';
                }, 2000);
                return;
            }
            
            if (response.status === 404) {
                PanierManager.showError('❌ ' + (data.error || 'Le menu n\'a pas été trouvé'));
                return;
            }
            
            if (!response.ok) {
                throw new Error(data.error || 'Erreur lors de l\'ajout au panier');
            }
            
            PanierManager.showSuccess('✓ ' + (selectedMealType === 'menu' ? 'Menu' : 'Plat') + ' ajouté au panier !');
            closeAddToCartModal();
            // Actualiser le compteur du panier dans la navbar
            if (typeof updateCartCount === 'function') {
                updateCartCount();
            }
            
        } catch (error) {
            console.error('Erreur:', error);
            PanierManager.showError('❌ ' + error.message);
        }
    });
}

// Fonction pour récupérer le cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}