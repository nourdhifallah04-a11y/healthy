// ========== DONNÉES DES PLATS (MENU COMPLET) - CHARGÉ DYNAMIQUEMENT ==========
let meals = [];
let menus = [];
let menusRecommandationIA = []; // Menus recommandés par IA
let isLoadingMenusIA = false; // Suivi du chargement des menus IA

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

function transformerMenuIAEnMeal(menu) {
    // Calculer les totaux nutritionnels depuis la structure retournée par le webhook
    console.log('Transformation du menu IA en meal:', menu);
    
    const totalProtein = menu.nutrition ? menu.nutrition.proteine : 0;
    const totalFiber = menu.nutrition ? menu.nutrition.fibres : 0;
    const totalCarbs = menu.nutrition ? menu.nutrition.glucides : 0;
    const totalFat = menu.nutrition ? menu.nutrition.lipides : 0;
    const totalCalories = menu.nutrition ? menu.nutrition.calorie : 0;
    const totalPrix = menu.prix ? parseFloat(menu.prix) : 0;
    const menuFromMeals = meals.filter(meal => Number(menu.menu_id) === meal.id)[0] || {};
    return {
        id: menu.menu_id || menu.id,
        name: menu.nom,
        calories: totalCalories,
        protein: totalProtein,
        carbs: totalCarbs,
        fat: totalFat,
        fiber: totalFiber,
        category: totalProtein >= 35 ? "proteine" : "autre",
        image: menu.image ? menu.image : "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        isNew: menu.isNew,
        prix: menuFromMeals.prix > 0 ? menuFromMeals.prix : null,
        description: menu.description,
        est_disponible: menu.est_disponible,
        type: 'menu',
        plats: menuFromMeals.plats || [],
        score: menu.score
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

/**
 * Appelle le webhook n8n asynchrone pour obtenir les menus recommandés par IA
 */
function chargerMenusRecommandationIA() {
    isLoadingMenusIA = true;
    if (currentFilter === "menu-recommandation-ia") {
        displayMeals();
    }
    
    console.log('🚀 Appel /profilNutritionnel/api/profil-nutritionnel/obtenir/');
    fetch('/profilNutritionnel/api/profil-nutritionnel/obtenir/')
        .then(response => {
            console.log('Response status from profil-nutritionnel:', response.status);
            if (response.status === 404 || response.status === 301) {
                console.log('ℹ️ Profil nutritionnel non trouvé, redirection vers la page de création du profil');
                window.location.href = '/profil-nutritionnel/';
                return;
            }
            if (response.status === 401) {
                console.log('ℹ️ Utilisateur non authentifié pour le webhook n8n');
                return null;
            }
            if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
            return response.json();
        })
        .then(profil => {
            if (!profil) return;
            
            const payload = {
                profil: {
                    age: profil.age || null,
                    poids: profil.poids || null,
                    taille: profil.taille || null,
                    sexe: profil.sexe || null,
                    objectif: profil.objectif_sante || null,
                    allergies: profil.allergies || null,
                    restrictions_alimentaires: profil.restrictions_alimentaires || null,
                    niveau_activite: profil.niveau_activite || null
                },
                consentements: {
                    donnees_sante_sensibles: profil.donnees_sante_sensibles || false,
                    learning_collectif: profil.learning_collectif || false
                }
            };
            
            console.log('🤖 Appel asynchrone webhook n8n pour menus:', payload);
            
            // Appel POST asynchrone au webhook
            fetch('http://192.168.1.184:5678/webhook/reco-top-plat-menu', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(response => {
                if (response.ok) {
                    console.log('✅ Webhook n8n appelé avec succès');
                    return response.json();
                } else {
                    console.error('⚠️ Erreur webhook n8n:', response.status);
                    return null;
                }
            })
            .then(data => {
                if (data) {
                    console.log('📊 Réponse du webhook n8n (menus):', data);
                    
                    // Adapter les données au format menu
                    const menusArray = Array.isArray(data) ? data : (data.top_menus || []);
                    menusRecommandationIA = menusArray
                        .map(menu => transformerMenuIAEnMeal(menu))
                        .filter(menu => menu);
                    console.log('Menus recommandés par IA transformés:', menusRecommandationIA);
                    if (currentFilter === "menu-recommandation-ia") {
                        displayMeals();
                    }
                }
            })
            .catch(error => console.error('❌ Erreur appel webhook n8n (menus):', error))
            .finally(() => {
                // Marquer la fin du chargement
                isLoadingMenusIA = false;
                // Rafraîchir l'affichage si c'est la catégorie active
                if (currentFilter === "menu-recommandation-ia") {
                    displayMeals();
                }
            });
        });
}

// ========== VARIABLES GLOBALES ==========
let currentFilter = "all";
let currentSearch = "";

// ========== PAGINATION STATE ==========
const INITIAL_DISPLAY = 8;
const ITEMS_PER_LOAD = 4;
let itemsDisplayed = 8;

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
    } else if (currentFilter === "menu-recommandation-ia") {
        filteredMeals = [...menusRecommandationIA];
    }

    // Filtre par recherche
    if (currentSearch.trim() !== "") {
        filteredMeals = filteredMeals.filter(meal =>
            meal.name.toLowerCase().includes(currentSearch.toLowerCase())
        );
    }

    // Tri par score nutritionnel (décroissant)
    filteredMeals.sort((a, b) => (b.score || 0) - (a.score || 0));

    // Affichage du loader pour recommandations IA si en cours de chargement
    if (currentFilter === "menu-recommandation-ia" && isLoadingMenusIA) {
        menuGrid.innerHTML = `
            <div class="loader-container" style="display: flex; justify-content: center; align-items: center; min-height: 400px; grid-column: 1 / -1;">
                <div class="spinner" style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #667eea;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                "></div>
                <div style="margin-left: 15px; font-size: 16px; color: #666;">
                    <p>⏳ Calcul de vos recommandations personnalisées...</p>
                    <p style="font-size: 12px; color: #999; margin-top: 5px;">Cela peut prendre quelques secondes</p>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        return;
    }

    // Affichage des résultats
    if (filteredMeals.length === 0) {
        menuGrid.innerHTML = `<div class="no-results">🍽️ Aucun menu ne correspond à votre recherche</div>`;
        return;
    }
    console.log('Menus à afficher après filtrage:', filteredMeals);
    
    // Déterminer combien d'éléments afficher initialement
    const displayCount = itemsDisplayed === 0 ? INITIAL_DISPLAY : itemsDisplayed;
    const mealsToDisplay = filteredMeals.slice(0, displayCount);
    const remainingMeals = filteredMeals.length - displayCount;
    
    // Créer le HTML des cartes de menu
    let gridHTML = mealsToDisplay.map(meal => {
        // Limiter à 4 plats max pour l'affichage
        const maxPlats = 4;
        const platsAfficher = meal.plats ? meal.plats.slice(0, maxPlats) : [];
        const platsRestants = meal.plats ? meal.plats.length - maxPlats : 0;

        return `
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
                
                ${meal.type === 'menu' && platsAfficher.length > 0 ? `
                    <div class="menu-plats" data-menu-id="${meal.id}">
                        <p class="plats-label">🍽️ Plats</p>
                        <ul class="plats-items plats-initial">
                            ${platsAfficher.map(plat => `<li>${plat.nom}</li>`).join('')}
                        </ul>
                        ${platsRestants > 0 ? `
                            <ul class="plats-items plats-hidden" style="display: none;">
                                ${meal.plats.slice(maxPlats).map(plat => `<li>${plat.nom}</li>`).join('')}
                            </ul>
                            <button class="btn-plats-more" data-menu-id="${meal.id}" style="cursor: pointer; background: none; border: none; color: #667eea; text-decoration: underline; padding: 8px 0; font-size: 14px; font-weight: 500;">
                                +${platsRestants} autres plats
                            </button>
                        ` : ''}
                    </div>
                ` : ''}
                
                <div class="nutrition-info">
                    <h4 class="nutrition-title">🔥 Valeurs nutritionnelles</h4>
                    <div class="nutrition-items-grid">
                        <div class="nutrition-item">
                            <span class="label">Calories</span>
                            <span class="value">${Math.round(meal.calories)} kcal</span>
                        </div>
                        <div class="nutrition-item">
                            <span class="label">Protéines</span>
                            <span class="value">${meal.protein.toFixed(1)}g</span>
                        </div>
                        <div class="nutrition-item">
                            <span class="label">Glucides</span>
                            <span class="value">${meal.carbs.toFixed(1)}g</span>
                        </div>
                        <div class="nutrition-item">
                            <span class="label">Lipides</span>
                            <span class="value">${meal.fat.toFixed(1)}g</span>
                        </div>
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
    `;
    }).join('');
    
    // Ajouter le bouton "Charger plus" si nécessaire
    if (remainingMeals > 0) {
        gridHTML += `
            <div class="load-more-container" style="grid-column: 1 / -1; text-align: center; padding: 20px;">
                <button class="btn-load-more" id="loadMoreBtn" style="padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold;">
                    <i class="fas fa-plus"></i> +${remainingMeals} autres plats
                </button>
            </div>
        `;
    }
    
    menuGrid.innerHTML = gridHTML;

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
    
    // Ajouter les événements aux boutons Comparer
    document.querySelectorAll('.btn-compare').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openCompareModal();
        });
    });
    
    // Ajouter l'événement au bouton "Charger plus"
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreItems);
    }
    
    // Ajouter l'événement aux boutons "plats-more" pour afficher tous les plats
    document.querySelectorAll('.btn-plats-more').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const menuId = btn.dataset.menuId;
            const menuContainer = btn.closest('.menu-plats');
            const initialPlats = menuContainer.querySelector('.plats-initial');
            const hiddenPlats = menuContainer.querySelector('.plats-hidden');
            
            if (hiddenPlats) {
                // Afficher tous les plats
                hiddenPlats.style.display = 'block';
                // Masquer le bouton
                btn.style.display = 'none';
            }
        });
    });
}

/**
 * Charge plus d'éléments lors du clic sur le bouton "Charger plus"
 */
function loadMoreItems() {
    itemsDisplayed += ITEMS_PER_LOAD;
    displayMeals();
}

// ========== GESTION DE LA COMPARAISON DES MENUS ==========

/**
 * État de la comparaison
 */
const comparisonState = {
    selectedMenus: new Map(),
    maxMenusToCompare: 3
};

/**
 * Ouvre le modal de comparaison
 */
function openCompareModal() {
    const modal = document.getElementById('compareModal');
    if (modal) {
        modal.style.display = 'block';
        populateCompareMenusList();
    }
}

/**
 * Ferme le modal de comparaison
 */
function closeCompareModal() {
    const modal = document.getElementById('compareModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Remplit la liste des menus pour la comparaison
 */
function populateCompareMenusList() {
    const compareMenusList = document.getElementById('compareMenusList');
    if (!compareMenusList) return;

    compareMenusList.innerHTML = meals.map(meal => {
        const isSelected = comparisonState.selectedMenus.has(meal.id);
        return `
            <div class="compare-menu-item ${isSelected ? 'selected' : ''}" data-menu-id="${meal.id}">
                <label style="display: flex; align-items: center; gap: 0.75rem; cursor: pointer; width: 100%;">
                    <input type="checkbox" 
                           class="compare-checkbox" 
                           data-menu-id="${meal.id}" 
                           ${isSelected ? 'checked' : ''}
                           ${comparisonState.selectedMenus.size >= comparisonState.maxMenusToCompare && !isSelected ? 'disabled' : ''}
                           onchange="toggleMenuSelection(${meal.id}, '${meal.name}', ${meal.calories}, ${meal.protein}, ${meal.carbs}, ${meal.fat}, ${meal.fiber}, ${meal.score})">
                    <div style="flex: 1;">
                        <div class="compare-menu-item-name">${meal.name}</div>
                        <div class="compare-menu-item-score">⭐ ${meal.score}/100</div>
                    </div>
                </label>
            </div>
        `;
    }).join('');
}

/**
 * Bascule la sélection d'un menu pour la comparaison
 */
function toggleMenuSelection(menuId, menuName, calories, protein, carbs, fat, fiber, score) {
    if (comparisonState.selectedMenus.has(menuId)) {
        // Déselection
        comparisonState.selectedMenus.delete(menuId);
    } else {
        // Selection
        if (comparisonState.selectedMenus.size < comparisonState.maxMenusToCompare) {
            comparisonState.selectedMenus.set(menuId, {
                id: menuId,
                name: menuName,
                calories: calories,
                protein: protein,
                carbs: carbs,
                fat: fat,
                fiber: fiber,
                score: score
            });
        }
    }

    updateComparisonUI();
}

/**
 * Met à jour l'affichage du modal de comparaison
 */
function updateComparisonUI() {
    // Mettre à jour le compteur de menus sélectionnés
    const compareCount = document.getElementById('compareCount');
    if (compareCount) {
        compareCount.textContent = comparisonState.selectedMenus.size;
    }

    // Mettre à jour les boutons de sélection
    document.querySelectorAll('.compare-menu-item').forEach(item => {
        const menuId = parseInt(item.dataset.menuId);
        if (comparisonState.selectedMenus.has(menuId)) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });

    // Montrer/masquer le tableau de comparaison
    const compareTable = document.getElementById('compareTable');
    if (comparisonState.selectedMenus.size >= 2 && compareTable) {
        compareTable.style.display = 'block';
        displayComparisonTable();
    } else if (compareTable) {
        compareTable.style.display = 'none';
    }
}

/**
 * Affiche le tableau de comparaison
 */
function displayComparisonTable() {
    const selectedMenusArray = Array.from(comparisonState.selectedMenus.values());
    
    // Mettre à jour les en-têtes
    const headers = ['menu1-header', 'menu2-header', 'menu3-header'];
    headers.forEach((headerId, index) => {
        const header = document.getElementById(headerId);
        const menuCol = document.querySelector(`#${headerId}`).closest('th');
        if (header && menuCol) {
            if (index < selectedMenusArray.length) {
                header.textContent = selectedMenusArray[index].name;
                menuCol.style.display = 'table-cell';
            } else {
                menuCol.style.display = 'none';
            }
        }
    });

    // Créer le contenu du tableau
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;

    const metrics = [
        { label: 'Calories', key: 'calories', unit: 'kcal' },
        { label: 'Protéines', key: 'protein', unit: 'g' },
        { label: 'Glucides', key: 'carbs', unit: 'g' },
        { label: 'Lipides', key: 'fat', unit: 'g' },
        { label: 'Fibres', key: 'fiber', unit: 'g' },
        { label: 'Score nutritionnel', key: 'score', unit: '/100' }
    ];

    tbody.innerHTML = metrics.map(metric => {
        let cells = `<td class="metric-col">${metric.label}</td>`;
        const values = selectedMenusArray.map(menu => menu[metric.key]);
        
        selectedMenusArray.forEach((menu, index) => {
            const value = menu[metric.key];
            const maxValue = Math.max(...values);
            const percentage = (value / maxValue) * 100;
            
            cells += `
                <td class="menu-col">
                    <div class="nutrient-value">${value.toFixed(1)} ${metric.unit}</div>
                    <div class="nutrient-bar">
                        <div class="nutrient-bar-fill" style="width: ${percentage}%"></div>
                    </div>
                </td>
            `;
        });

        // Masquer les colonnes vides
        const row = document.createElement('tr');
        row.innerHTML = cells;
        document.querySelectorAll(`td.menu-col`).forEach((td, index) => {
            if (index >= selectedMenusArray.length) {
                td.style.display = 'none';
            }
        });

        return cells;
    }).map(html => `<tr>${html}</tr>`).join('');

    // Afficher les graphiques
    displayComparisonCharts(selectedMenusArray);

    // Afficher la recommandation
    displayComparisonRecommendation(selectedMenusArray);
}

/**
 * Affiche les graphiques de comparaison
 */
function displayComparisonCharts(selectedMenus) {
    const metrics = [
        { id: 'caloriesChart', key: 'calories', unit: 'kcal' },
        { id: 'proteinChart', key: 'protein', unit: 'g' },
        { id: 'carbsChart', key: 'carbs', unit: 'g' },
        { id: 'fatChart', key: 'fat', unit: 'g' }
    ];

    metrics.forEach(metric => {
        const chartContainer = document.getElementById(metric.id);
        if (!chartContainer) return;

        const maxValue = Math.max(...selectedMenus.map(m => m[metric.key]));
        
        chartContainer.innerHTML = selectedMenus.map((menu, index) => {
            const value = menu[metric.key];
            const percentage = (value / maxValue) * 100;
            return `
                <div class="chart-bar">
                    <div class="chart-bar-fill" style="height: ${percentage}%">
                        <span class="chart-bar-value">${value.toFixed(1)}</span>
                    </div>
                    <div class="chart-bar-label">${menu.name}</div>
                </div>
            `;
        }).join('');
    });
}

/**
 * Affiche une recommandation basée sur la comparaison
 */
function displayComparisonRecommendation(selectedMenus) {
    const recommendationText = document.getElementById('recommendationText');
    if (!recommendationText) return;

    let recommendation = '';

    if (selectedMenus.length === 2) {
        const menu1 = selectedMenus[0];
        const menu2 = selectedMenus[1];

        if (menu1.protein > menu2.protein) {
            recommendation += `<strong>${menu1.name}</strong> est plus riche en protéines (${menu1.protein.toFixed(1)}g vs ${menu2.protein.toFixed(1)}g). `;
        } else if (menu2.protein > menu1.protein) {
            recommendation += `<strong>${menu2.name}</strong> est plus riche en protéines (${menu2.protein.toFixed(1)}g vs ${menu1.protein.toFixed(1)}g). `;
        }

        if (menu1.calories < menu2.calories) {
            recommendation += `${menu1.name} est plus léger en calories. `;
        } else if (menu2.calories < menu1.calories) {
            recommendation += `${menu2.name} est plus léger en calories. `;
        }

        if (menu1.score > menu2.score) {
            recommendation += `<strong>${menu1.name}</strong> a un meilleur score nutritionnel (${menu1.score}/100).`;
        } else if (menu2.score > menu1.score) {
            recommendation += `<strong>${menu2.name}</strong> a un meilleur score nutritionnel (${menu2.score}/100).`;
        }
    } else if (selectedMenus.length === 3) {
        const bestProtein = selectedMenus.reduce((max, m) => m.protein > max.protein ? m : max);
        const lowestCals = selectedMenus.reduce((min, m) => m.calories < min.calories ? m : min);
        const bestScore = selectedMenus.reduce((max, m) => m.score > max.score ? m : max);

        recommendation += `💪 <strong>${bestProtein.name}</strong> offre le plus de protéines. `;
        recommendation += `🔥 <strong>${lowestCals.name}</strong> est le plus léger. `;
        recommendation += `⭐ <strong>${bestScore.name}</strong> a le meilleur score nutritionnel.`;
    }

    recommendationText.innerHTML = recommendation || 'Sélectionnez au moins 2 menus pour obtenir une analyse.';
}

/**
 * Réinitialise la comparaison
 */
function resetComparison() {
    comparisonState.selectedMenus.clear();
    updateComparisonUI();
    populateCompareMenusList();
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
            itemsDisplayed = 0; // Réinitialiser la pagination
            displayMeals();
        });
    });
}

// ========== GESTION DE LA RECHERCHE ==========
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        itemsDisplayed = 0; // Réinitialiser la pagination
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
    
    // Charger les menus recommandés par IA
    chargerMenusRecommandationIA();
    
    console.log('🌿 Menu Fresh & Greens chargé avec succès !');

    // ========== GESTION MODAL COMPARAISON ==========
    // Fermer le modal de comparaison avec le bouton X
    const closeCompareBtn = document.querySelector('.close-compare');
    if (closeCompareBtn) {
        closeCompareBtn.addEventListener('click', closeCompareModal);
    }

    // Fermer le modal de comparaison en cliquant en dehors
    const compareModal = document.getElementById('compareModal');
    if (compareModal) {
        compareModal.addEventListener('click', (e) => {
            if (e.target === compareModal) {
                closeCompareModal();
            }
        });
    }

    // Bouton réinitialiser la comparaison
    const resetCompareBtn = document.getElementById('resetCompareBtn');
    if (resetCompareBtn) {
        resetCompareBtn.addEventListener('click', resetComparison);
    }
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
            const response = await fetch('/commande/api/ligne-commandes/', {
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