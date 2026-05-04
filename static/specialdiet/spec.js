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
    "plat-recommander": [],
    "plat-recommandation-ia": []
};

/**
 * Transforme un objet Plat depuis l'API en objet meal pour l'affichage
 * @param {Object} plat - Objet plat reçu de l'API
 * @returns {Object} Objet meal formaté
 */
function transformerPlatEnMealDiet(plat) {
    // Extraire l'ID - essayer les différentes propriétés possibles
    const mealId = plat.id_plat || plat.id || null;
    
    if (!mealId) {
        console.warn('⚠️ Warning: Plat without ID detected', plat);
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
    fetch('//plat/api/plats/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Données brutes reçues de l\'API (plats):', data);
            
            // Adapter les données de l'API au format attendu
            const platsArray = Array.isArray(data) ? data : (data.results || []);
            console.log('Plats extraits:', platsArray);
            // Filtrer les plats actifs uniquement et transformer
            const mealsFormatted = platsArray
                .filter(plat => plat.est_disponible === true)
                .map(plat => transformerPlatEnMealDiet(plat));
            console.log('Plats formatés:', mealsFormatted);
            // Catégoriser les plats par type de régime
            dietMeals = categoriserPlatsByDiet(mealsFormatted);
            
            // Rafraîchir l'affichage de dietGrid
            displayDietMeals();
            
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
 * Appelle le webhook n8n asynchrone pour obtenir les recommandations IA
 */
function appelN8NRecommandationsAsync() {
    // Marquer le début du chargement
    isLoadingRecoIA = true;
    if (currentDiet === "plat-recommandation-ia") {
        displayDietMeals();
    }
    console.log('🚀 Appel /profilNutritionnel/api/profil-nutritionnel/obtenir/');
    // Récupérer le profil utilisateur
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
                    console.log('Plats recommandés par n8n extraits:', platsArray);
                    // Transformer les plats reçus du webhook
                    const mealsFormatted = platsArray.map(plat => transformerPlatEnMealDiet(plat));
                    console.log('Plats recommandés par n8n formatés:', mealsFormatted);
                    // Ajouter à la catégorie plat-recommandation-ia
                    dietMeals["plat-recommandation-ia"] = mealsFormatted;
                    console.log('Plats recommandés par n8n intégrés dans dietMeals:', dietMeals["plat-recommandation-ia"]);
                    
                    console.log('✅ Recommandations IA n8n reçues et intégrées !', mealsFormatted);
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
 * Charge les plats recommandés basés sur le profil nutritionnel de l'utilisateur
 */
function chargerPlatsRecommandes() {
    // Appeler le webhook n8n asynchrone (ne pas attendre)
    appelN8NRecommandationsAsync();
    
    fetch('/plat/api/profil-nutritionnel/recommander-plats/')
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
let isLoadingRecoIA = false; // Track si les recommandations IA sont en cours de chargement

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
    "plat-recommander": "Recommendation IA",
    "plat-recommandation-ia": "Recommendation IA"
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

    // Affichage du loader pour plat-recommandation-ia si en cours de chargement
    if (currentDiet === "plat-recommandation-ia" && isLoadingRecoIA) {
        dietGrid.innerHTML = `
            <div class="loader-container" style="display: flex; justify-content: center; align-items: center; min-height: 400px;">
                <div class="spinner" style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #3498db;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                "></div>
                <div style="margin-left: 15px; font-size: 16px; color: #666;">
                    <p>⏳ Chargement des recommandations IA...</p>
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
    if (meals.length === 0) {
        dietGrid.innerHTML = `<div class="no-results">🍽️ Aucun plat disponible pour cette catégorie</div>`;
        return;
    }
    console.log(`Affichage des plats pour ${dietName}:`, meals);
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
        
        // Générer le HTML des alertes s'il y en a
        const alertsHTML = meal.alerts && meal.alerts.length > 0 ? `
            <div class="meal-alerts">
                ${meal.alerts.map(alert => `<div class="alert-item">⚠️ ${alert}</div>`).join('')}
            </div>
        ` : '';
        
        return `
        <div class="meal-card">
            <div class="meal-img">
                <img src="${meal.image}" alt="${meal.name}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                <div class="badge-diet">${dietName}</div>
                ${meal.badge ? `<div class="badge-ia" title="Recommandation IA">${meal.badge}</div>` : ''}
                <div class="prot-circle">${meal.protein}g <span>PROT</span></div>
                ${meal.score > 0 ? `<div class="score-badge ${scoreClass}">
                    <div class="score-value">${Math.round(meal.score)}</div>
                    <div class="score-label">Score</div>
                    <div class="score-icon">${scoreIcon}</div>
                </div>` : ''}
                ${meal.scoreNutritionnel > 0 ? `<div class="nutrition-score-badge">
                    <div class="nutrition-score-value">${meal.scoreNutritionnel}</div>
                    <div class="nutrition-score-label">Nutrition</div>
                </div>` : ''}
            </div>
            <div class="meal-body">
                <h3>${meal.name}</h3>
                ${meal.interpretation ? `<div class="meal-interpretation">💬 ${meal.interpretation}</div>` : ''}
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
                    <div class="nutri-item">
                        <span>🌾 Lipides</span>
                        ${meal.fat}g
                    </div>
                    <div class="nutri-item">
                        <span>🌿 Fibres</span>
                        ${meal.fiber}g
                    </div>
                </div>
                ${alertsHTML}
                <div class="meal-footer">
                    <button class="btn-add-to-cart" data-id="${meal.id}" data-name="${meal.name}">
                        <Recommendation IAcart"></i> Ajouter
                    </button>
                </div>
            </div>
        </div>
    `}).join('');

    // Ajouter les événements aux boutons Ajouter au Panier
    document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const mealId = btn.dataset.id;
            const mealName = btn.dataset.name;
            
            // Vérifier que l'ID est valide
            if (!mealId || mealId === 'undefined') {
                console.error('❌ Error: Invalid meal ID', mealId);
                alert('❌ Erreur: L\'identifiant du plat est invalide. Veuillez recharger la page.');
                return;
            }
            
            openAddToCartModal(mealId, mealName, 0); // Prix sera récupéré de l'API
        });
    });
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
    // Afficher high-protein par défaut
    currentDiet = "high-protein";
    displayDietMeals();
    console.log('🌿 Special Diet Fresh & Greens chargé avec succès !');
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

