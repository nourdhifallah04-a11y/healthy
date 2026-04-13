// Initialize Bootstrap dropdowns
document.addEventListener('DOMContentLoaded', function() {
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(function(element) {
        new bootstrap.Dropdown(element);
    });
});

// ========== DONNÉES DES PLATS (MENU COMPLET) - CHARGÉ DYNAMIQUEMENT ==========
let meals = [];

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
        isNew: false,
        prix: plat.prix,
        description: plat.description,
        est_disponible: plat.est_disponible
    };
}

/**
 * Charge les plats depuis l'API et les affiche
 */
function chargerPlats() {
    fetch('/api/plats/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Données brutes reçues de l\'API:', data);
            
            // Adapter les données de l'API au format attendu par displayMeals
            const platsArray = Array.isArray(data) ? data : (data.results || []);
            meals = platsArray.map(plat => transformerPlatEnMeal(plat));
            
            // Afficher les plats après le chargement
            displayMeals();
            console.log('✓ Plats chargés avec succès !', meals);
        })
        .catch(error => {
            console.error('Erreur lors du chargement des plats:', error);
            // Fallback: afficher un message d'erreur
            if (menuGrid) {
                menuGrid.innerHTML = `<div class="no-results">⚠️ Erreur lors du chargement des plats</div>`;
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

// ========== FONCTION POUR AFFICHER LES PLATS ==========
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

    // Affichage des résultats
    if (filteredMeals.length === 0) {
        menuGrid.innerHTML = `<div class="no-results">🍽️ Aucun plat ne correspond à votre recherche</div>`;
        return;
    }

    menuGrid.innerHTML = filteredMeals.map(meal => `
        <div class="meal-card" data-id="${meal.id}" data-category="${meal.category}">
            <div class="meal-img">
                <img src="${meal.image}" alt="${meal.name}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                ${meal.isNew ? '<span class="badge-new">NEW</span>' : ''}
                <div class="prot-circle">${meal.protein}g <span>PROT</span></div>
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
                </div>
            </div>
        </div>
    `).join('');
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
    chargerPlats();
    console.log('🌿 Menu Fresh & Greens chargé avec succès !');
});