// Initialize Bootstrap dropdowns
document.addEventListener('DOMContentLoaded', function() {
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(function(element) {
        new bootstrap.Dropdown(element);
    });

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
        //resetCompareBtn.addEventListener('click', resetComparison);
    }
});

// ========== DONNÉES DES PLATS PAR CATÉGORIE DIET ==========
let dietMeals = {
    "high-protein": [],
    "low-carb": [],
    "vegan": [],
    "gluten-free": [],
    "plat-recommander": [],
    "plat-recommandation-ia": []
};

/**
 * Transforme un objet Plat depuis l'API en objet meal pour l'affichage
 * @param {Object} plat - Objet plat reçu de l'API
 * @returns {Object} Objet meal formaté
 */
function transformerPlatEnMealDiet(plat) {
    const mealId = plat.id_plat || plat.id || null;
    
    if (!mealId) {
        console.warn('⚠️ Plat sans ID détecté', plat);
    }
    
    return {
        id: mealId,
        name: plat.nom,
        calories: plat.calorie || 0,
        protein: plat.proteine || 0,
        carbs: plat.glucides || 0,
        fat: plat.lipides || 0,
        fiber: plat.fibres || 0,
        image: plat.image ? plat.image : "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        description: plat.description,
        score: plat.score || 0,
        scoreNutritionnel: plat.score_nutritionnel || 0,
        prix: plat.prix || 0,
        badge: plat.badge || null,
        interpretation: plat.interpretation || null,
        alerts: plat.alerts || []
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
        "gluten-free": [],
        "plat-recommander": [],
        "plat-recommandation-ia": []
    };

    plats.forEach(meal => {
        if (meal.protein >= 35) {
            categorized["high-protein"].push(meal);
        }
        
        if (meal.carbs <= 20) {
            categorized["low-carb"].push(meal);
        }
        
        categorized["gluten-free"].push(meal);
        
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
    fetch('/plat/api/plats/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Données reçues de l\'API:', data);
            
            const platsArray = Array.isArray(data) ? data : (data.results || []);
            const mealsFormatted = platsArray
                .filter(plat => plat.est_disponible === true)
                .map(plat => transformerPlatEnMealDiet(plat));
            
            const baseDietMeals = categoriserPlatsByDiet(mealsFormatted);
            // Fusionner avec les clés existantes pour conserver plat-recommander et plat-recommandation-ia
            dietMeals = {
                ...baseDietMeals,
                "plat-recommander": dietMeals["plat-recommander"] || [],
                "plat-recommandation-ia": dietMeals["plat-recommandation-ia"] || []
            };
            
            displayDietMeals();
            chargerPlatsRecommandes();
            console.log('✅ Régimes spéciaux chargés avec succès !');
        })
        .catch(error => {
            console.error('❌ Erreur lors du chargement:', error);
            if (dietGrid) {
                dietGrid.innerHTML = `<div class="no-results">⚠️ Erreur lors du chargement des plats</div>`;
            }
        });
}

/**
 * Appelle le webhook n8n asynchrone pour obtenir les recommandations IA
 */
function appelN8NRecommandationsAsync() {
    isLoadingRecoIA = true;
    if (currentDiet === "plat-recommandation-ia") {
        displayDietMeals();
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
            
            console.log('🤖 Appel asynchrone webhook n8n:', payload);
            
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
                    console.log('📊 Réponse du webhook n8n:', data);
                    
                    // Adapter les données au format plat
                    const platsArray = Array.isArray(data) ? data : (data.top_plats || []);
                    const mealsFormatted = platsArray.map(plat => transformerPlatEnMealDiet(plat));
                    dietMeals["plat-recommandation-ia"] = mealsFormatted;
                    
                    if (currentDiet === "plat-recommandation-ia") {
                        displayDietMeals();
                    }
                }
            })
            .catch(error => console.error('❌ Erreur appel webhook n8n:', error))
            .finally(() => {
                // Marquer la fin du chargement
                isLoadingRecoIA = false;
                // Rafraîchir l'affichage si c'est la catégorie active
                if (currentDiet === "plat-recommandation-ia") {
                    displayDietMeals();
                }
            });
        });
}

/**
 * Charge les plats recommandés basés sur le profil nutritionnel
 */
function chargerPlatsRecommandes() {
    // Appeler le webhook n8n asynchrone (ne pas attendre)
    appelN8NRecommandationsAsync();
    
    fetch('/plat/api/profil-nutritionnel/recommander-plats/')
        .then(response => {
            if (response.status === 401) {
                console.log('ℹ️ Utilisateur non authentifié');
                dietMeals["plat-recommander"] = [];
                displayDietMeals();
                return;
            }
            if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (!data) return;
            
            console.log('Plats recommandés reçus:', data);
            
            const platsArray = Array.isArray(data) ? data : (data.results || []);
            const mealsFormatted = platsArray.map(plat => transformerPlatEnMealDiet(plat));
            dietMeals["plat-recommander"] = mealsFormatted;
            
            if (currentDiet === "plat-recommander") {
                displayDietMeals();
            }
            console.log('✅ Plats recommandés chargés');
        })
        .catch(error => {
            console.error('❌ Erreur plats recommandés:', error);
            dietMeals["plat-recommander"] = [];
        });
}

// ========== VARIABLES GLOBALES ==========
let currentDiet = "high-protein";
let isLoadingRecoIA = false;
let currentSearch = "";

// ========== GESTION COMPARAISON PLATS ==========
const compareState = {
    selectedMenus: [],
    maxMenus: 3
};

// ========== RÉFÉRENCES DOM ==========
const dietGrid = document.getElementById('dietGrid');
const searchInput = document.getElementById('searchInput');
const dietCards = document.querySelectorAll('.diet-card');
const selectedDietSpan = document.getElementById('selectedDiet');

// ========== DICTIONNAIRE DES NOMS DE RÉGIMES ==========
const dietNames = {
    "high-protein": "High Protein",
    "low-carb": "Low Carb",
    "vegan": "Vegan",
    "gluten-free": "Sans Gluten",
    "plat-recommander": "Plat recommander",
    "plat-recommandation-ia": "Recommendation IA"
};


// ========== GESTION DE LA RECHERCHE ==========
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        itemsDisplayed = 0; // Réinitialiser la pagination
        displayDietMeals();
    });
}

// ========== FONCTION POUR AFFICHER LES PLATS ==========
function displayDietMeals() {
    if (!dietGrid) return;

    let meals = dietMeals[currentDiet] || [];
    const dietName = dietNames[currentDiet] || currentDiet;
    // Filtre par recherche
    if (currentSearch.trim() !== "") {
        meals = meals.filter(meal =>
            meal.name.toLowerCase().includes(currentSearch.toLowerCase())
        );
    }
    if (selectedDietSpan) {
        selectedDietSpan.textContent = dietName;
    }

    // Loading state pour recommandations IA
    if (currentDiet === "plat-recommandation-ia" && isLoadingRecoIA) {
        dietGrid.innerHTML = `
            <div class="loader-container">
                <div class="spinner" aria-hidden="true"></div>
                <div class="loading-text">
                    <p>⏳ Calcul de vos recommandations personnalisées...</p>
                    <p>Cela peut prendre quelques secondes</p>
                </div>
            </div>
        `;
        dietGrid.setAttribute('aria-busy', 'true');
        return;
    }

    dietGrid.setAttribute('aria-busy', 'false');

    if (meals.length === 0) {
        dietGrid.innerHTML = `<div class="no-results">🍽️ Aucun plat disponible pour cette catégorie</div>`;
        return;
    }

    dietGrid.innerHTML = meals.map(meal => {
        // Déterminer la classe et le label du score
        let scoreClass = 'score-low';
        let scoreLabel = 'Faible';
        
        if (meal.score >= 80) {
            scoreClass = 'score-excellent';
            scoreLabel = 'Excellent';
        } else if (meal.score >= 60) {
            scoreClass = 'score-good';
            scoreLabel = 'Bon';
        } else if (meal.score >= 40) {
            scoreClass = 'score-ok';
            scoreLabel = 'Moyen';
        }
        
        const alertsHTML = meal.alerts && meal.alerts.length > 0 ? `
            <div class="meal-alerts" role="alert" aria-live="assertive">
                ${meal.alerts.map(alert => `<div class="alert-item">⚠️ ${alert}</div>`).join('')}
            </div>
        ` : '';
        
        return `
        <article class="meal-card">
            <div class="meal-img" role="img" aria-label="${meal.name} - ${meal.calories} kcal">
                <img src="${meal.image}" alt="${meal.name}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                <div class="badge-diet" aria-label="Catégorie: ${dietName}">${dietName.split(' ')[0]}</div>
                <div class="prot-circle" aria-label="Protéines: ${meal.protein}g">
                    ${meal.protein}g <span>PROT</span>
                </div>
                ${meal.score > 0 ? `<div class="score-badge ${scoreClass}" aria-label="Score nutritionnel: ${Math.round(meal.score)} sur 100 - ${scoreLabel}">
                    <div class="score-value">${Math.round(meal.score)}</div>
                    <div class="score-label">Score</div>
                    <div class="score-icon" aria-hidden="true">${scoreLabel === 'Excellent' ? '⭐' : scoreLabel === 'Bon' ? '👍' : '😐'}</div>
                </div>` : ''}
            </div>
            <div class="meal-body">
                <h3>${meal.name}</h3>
                ${meal.interpretation ? `<div class="meal-interpretation">💬 ${meal.interpretation}</div>` : ''}
                <div class="nutri-table" role="table" aria-label="Informations nutritionnelles">
                    <div class="nutri-item">
                        <span>Calories</span>
                        <strong>${meal.calories} kcal</strong>
                    </div>
                    <div class="nutri-item">
                        <span>Protéines</span>
                        <strong>${meal.protein}g</strong>
                    </div>
                    <div class="nutri-item">
                        <span>Glucides</span>
                        <strong>${meal.carbs}g</strong>
                    </div>
                    <div class="nutri-item">
                        <span>Lipides</span>
                        <strong>${meal.fat}g</strong>
                    </div>
                    <div class="nutri-item">
                        <span>Fibres</span>
                        <strong>${meal.fiber}g</strong>
                    </div>
                </div>
                ${alertsHTML}
                <div class="meal-footer">
                    <button class="btn-add-to-cart" data-id="${meal.id}" data-name="${meal.name}" aria-label="Ajouter ${meal.name} au panier">
                        🛒 Ajouter
                    </button>
                </div>
            </div>
        </article>
    `}).join('');

    // Ajouter les événements aux boutons
    document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const mealId = btn.dataset.id;
            const mealName = btn.dataset.name;
            
            if (!mealId || mealId === 'undefined') {
                console.error('❌ ID de plat invalide');
                alert('❌ Erreur: Identifiant invalide. Veuillez recharger la page.');
                return;
            }
            
            openAddToCartModal(mealId, mealName, 0);
        });
    });
}

// ========== GESTION DES CATÉGORIES DIET ==========
if (dietCards.length > 0) {
    dietCards.forEach(card => {
        card.addEventListener('click', () => {
            dietCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            currentDiet = card.dataset.diet;
            
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

        // Accessibilité: supporter les touches Enter/Space
        card.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });
}

// ========== CHARGEMENT INITIAL ==========
document.addEventListener('DOMContentLoaded', () => {
    chargerDietMeals();
    currentDiet = "high-protein";
    displayDietMeals();
    
    // Marquer le premier diet-card comme actif
    if (dietCards.length > 0) {
        dietCards[0].classList.add('active');
    }
    
    // Ajouter les événements aux boutons Comparer
    document.querySelectorAll('.btn-compare').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openCompareModal();
        });
    });
    
    console.log('✅ Module Special Diet chargé avec succès !');
});

// ========== GESTION MODAL AJOUTER AU PANIER ==========
let selectedMealId = null;

function openAddToCartModal(mealId, mealName, mealPrice) {
    // Validation de l'ID
    if (!mealId || mealId === 'undefined') {
        console.error('❌ Error in openAddToCartModal: Invalid mealId', mealId);
        alert('❌ Erreur: L\'identifiant du plat est invalide.');
        return;
    }
    
    selectedMealId = mealId;
    const modal = document.getElementById('addToCartModal');
    const itemInfo = document.getElementById('itemInfo');
    const quantity = document.getElementById('quantity');
    
    let priceText = mealName;
    if (mealPrice && mealPrice > 0) {
        priceText += ` - €${parseFloat(mealPrice).toFixed(2)}`;
    }
    itemInfo.textContent = priceText;
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
        
        if (!selectedMealId) {
            console.error('No plat selected');
            return;
        }
        
        const quantity = parseInt(document.getElementById('quantity').value);
        
        try {
            console.log('Envoi POST avec plat_id:', selectedMealId, 'quantite:', quantity);
            
            // Appel API pour ajouter au panier
            const response = await fetch('/commande/api/ligne-commandes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    plat_id: selectedMealId,
                    quantite: quantity
                })
            });
            
            console.log('Response status:', response.status);
            
            // Vérifier d'abord le statut avant de parser JSON
            if (response.status === 401 || response.status === 403) {
                const errorMsg = '❌ Vous devez être connecté pour ajouter au panier. Veuillez vous connecter.';
                if (typeof PanierManager !== 'undefined') {
                    PanierManager.showError(errorMsg);
                } else {
                    alert(errorMsg);
                }
                setTimeout(() => {
                    window.location.href = '/login/';
                }, 2000);
                return;
            }
            
            // Parser la réponse JSON
            const data = await response.json();
            console.log('Response data:', data);
            
            if (response.status === 404) {
                const errorMsg = '❌ ' + (data.error || 'Le plat n\'a pas été trouvé (ID: ' + selectedMealId + ')');
                if (typeof PanierManager !== 'undefined') {
                    PanierManager.showError(errorMsg);
                } else {
                    alert(errorMsg);
                }
                return;
            }
            
            if (response.status === 400) {
                const errorMsg = '❌ ' + (data.error || 'Erreur de validation');
                if (typeof PanierManager !== 'undefined') {
                    PanierManager.showError(errorMsg);
                } else {
                    alert(errorMsg);
                }
                return;
            }
            
            if (!response.ok) {
                throw new Error(data.error || 'Erreur lors de l\'ajout au panier');
            }
            
            // Succès: 201 Created
            console.log('✅ Ligne commande créée avec succès:', data);
            if (typeof PanierManager !== 'undefined') {
                PanierManager.showSuccess('✓ Plat ajouté au panier !');
            } else {
                alert('✓ Plat ajouté au panier !');
            }
            closeAddToCartModal();
            // Actualiser le compteur du panier dans la navbar
            if (typeof updateCartCount === 'function') {
                updateCartCount();
            }
            
        } catch (error) {
            console.error('Erreur lors du POST:', error);
            const errorMsg = '❌ ' + error.message;
            if (typeof PanierManager !== 'undefined') {
                PanierManager.showError(errorMsg);
            } else {
                alert(errorMsg);
            }
        }
    });
}

// ========== GESTION MODAL COMPARAISON ==========
/**
 * Ouvre le modal de comparaison
 */
function openCompareModal() {
    const modal = document.getElementById('compareModal');
    if (modal) {
        modal.style.display = 'block';
        populateComparePlasList();
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
 * Remplit la liste des plats pour la comparaison
 */
function populateComparePlasList() {
    const comparePlatsList = document.getElementById('comparePlatsList');
    if (!comparePlatsList) return;

    const currentMeals = dietMeals[currentDiet] || [];
    
    comparePlatsList.innerHTML = currentMeals.map(meal => {
        const isSelected = compareState.selectedMenus.some(m => m.id === meal.id);
        return `
            <div class="compare-menu-item ${isSelected ? 'selected' : ''}" data-menu-id="${meal.id}">
                <label style="display: flex; align-items: center; gap: 0.75rem; cursor: pointer; width: 100%;">
                    <input type="checkbox" 
                           class="compare-checkbox" 
                           data-menu-id="${meal.id}" 
                           ${isSelected ? 'checked' : ''}
                           ${compareState.selectedMenus.length >= compareState.maxMenus && !isSelected ? 'disabled' : ''}
                           onchange="toggleMenuSelection(${meal.id}, '${meal.name}', ${meal.calories}, ${meal.protein}, ${meal.carbs}, ${meal.fat}, ${meal.fiber}, ${meal.score})">
                    <div style="flex: 1;">
                        <div class="compare-menu-item-name">${meal.name}</div>
                        <div class="compare-menu-item-score">⭐ ${Math.round(meal.score)}/100</div>
                    </div>
                </label>
            </div>
        `;
    }).join('');
}

/**
 * Bascule la sélection d'un plat pour la comparaison
 */
function toggleMenuSelection(menuId, menuName, calories, protein, carbs, fat, fiber, score) {
    const existingIndex = compareState.selectedMenus.findIndex(m => m.id === menuId);
    
    if (existingIndex !== -1) {
        // Déselection
        compareState.selectedMenus.splice(existingIndex, 1);
    } else {
        // Selection
        if (compareState.selectedMenus.length < compareState.maxMenus) {
            compareState.selectedMenus.push({
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
    // Mettre à jour le compteur de plats sélectionnés
    const compareCount = document.getElementById('compareCount');
    if (compareCount) {
        compareCount.textContent = compareState.selectedMenus.length;
    }
    
    // Mettre à jour la visibilité du tableau
    const compareTable = document.getElementById('compareTable');
    if (compareTable) {
        if (compareState.selectedMenus.length >= 2) {
            compareTable.style.display = 'block';
            populateComparisonTable();
        } else {
            compareTable.style.display = 'none';
        }
    }
    
    // Mettre à jour le texte d'aide
    const selectionHelper = document.getElementById('selectionHelper');
    if (selectionHelper) {
        const messageMap = {
            0: 'Sélectionnez 2 à 3 plats pour commencer',
            1: 'Sélectionnez 1 plat supplémentaire minimum',
            2: 'Parfait ! Vous pouvez ajouter 1 plat de plus',
            3: 'Maximum atteint (3 plats)'
        };
        
        const message = messageMap[compareState.selectedMenus.length];
        const icon = compareState.selectedMenus.length >= 2 ? '✓' : 'ℹ';
        selectionHelper.textContent = `${icon} ${message}`;
    }
    
    // Mettre à jour la liste pour refléter l'état
    populateComparePlasList();
}

/**
 * Remplit le tableau de comparaison des nutriments
 */
function populateComparisonTable() {
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;
    
    if (compareState.selectedMenus.length < 2) return;
    
    // Afficher les en-têtes des colonnes
    const headers = ['menu1-header', 'menu2-header', 'menu3-header'];
    headers.forEach((headerId, index) => {
        const header = document.getElementById(headerId);
        if (header) {
            if (index < compareState.selectedMenus.length) {
                header.style.display = '';
                const menuName = compareState.selectedMenus[index].name;
                header.querySelector('.menu-number').textContent = `${menuName}`;
            } else {
                header.style.display = 'none';
            }
        }
    });
    
    // Nutriments à afficher
    const nutrients = [
        { key: 'calories', label: 'Calories', unit: 'kcal' },
        { key: 'protein', label: 'Protéines', unit: 'g' },
        { key: 'carbs', label: 'Glucides', unit: 'g' },
        { key: 'fat', label: 'Lipides', unit: 'g' },
        { key: 'fiber', label: 'Fibres', unit: 'g' }
    ];
    
    tbody.innerHTML = nutrients.map(nutrient => {
        const values = compareState.selectedMenus.map(menu => menu[nutrient.key]);

        const cells = compareState.selectedMenus.map(menu => {
        const value = menu[nutrient.key];
        const maxValue = Math.max(...values);
        const percentage = (value / maxValue) * 100;
            return `<td class="compare-cell">${Math.round(menu[nutrient.key])} 
            <div class="nutrient-bar">
                        <div class="nutrient-bar-fill" style="width: ${percentage}%"></div>
                    </div></td>`   
        }
        ).join('');
        
        return `
            <tr>
                <td class="metric-col"><strong>${nutrient.label}</strong></td>
                ${cells}
            </tr>
        `;
    }).join('');

        // Afficher les graphiques
    displayComparisonCharts(compareState.selectedMenus);

    // Afficher la recommandation
    displayComparisonRecommendation(compareState.selectedMenus);
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
        
        renderComparisonChart({ selectedMenus, metric, maxValue, chartContainer });
    });
}

function renderComparisonChart({ selectedMenus, metric, maxValue, chartContainer }) {
    if (!selectedMenus || !selectedMenus.length || !metric || !maxValue) return;

    const colorClass = {
        calories: "bar-calories",
        protein: "bar-proteines",
        carbs: "bar-glucides",
        fat: "bar-lipides"
    }[metric.key] || "bar-default";

    chartContainer.innerHTML = `
        <div class="comparison-chart-wrapper">
            <div class="chart-legend">
                <span><span class="legend-dot bar-calories"></span>Calories</span>
                <span><span class="legend-dot bar-proteines"></span>Protéines</span>
                <span><span class="legend-dot bar-glucides"></span>Glucides</span>
                <span><span class="legend-dot bar-lipides"></span>Lipides</span>
            </div>
            <div class="comparison-chart">
                <div class="chart-bars-wrapper">
                    ${selectedMenus.map((menu, index) => {
                        const rawValue = Number(menu[metric.key]) || 0;
                        const safeValue = rawValue > 0 ? rawValue : 0.1;
                        const percentage = (safeValue / maxValue) * 100;
                        const displayValue = rawValue > 0 ? rawValue.toFixed(1) : "0";

                        return `
                            <div class="chart-bar" data-index="${index}">
                                <div class="chart-bar-fill ${colorClass}" data-target="${percentage}">
                                    <span class="chart-bar-value">${displayValue}</span>
                                </div>
                                <div class="chart-bar-label" data-full="${menu.name}">
                                    ${menu.name}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `;

    const bars = chartContainer.querySelectorAll(".chart-bar-fill");

    function animateHeight(el, target, delay) {
        let current = 0;
        const step = () => {
            current += (target - current) * 0.08;
            el.style.height = current + "%";
            if (Math.abs(current - target) > 0.5) {
                requestAnimationFrame(step);
            } else {
                el.style.height = target + "%";
            }
        };
        setTimeout(() => requestAnimationFrame(step), delay);
    }

    bars.forEach((bar, index) => {
        const target = parseFloat(bar.getAttribute("data-target")) || 0;
        animateHeight(bar, target, index * 120);
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

