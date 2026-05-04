// Main script for accueil/home page
/**
 * Configuration centralisée des critères nutritionnels
 * 👉 Facile à modifier / étendre
 */
const NUTRITION_CRITERIA = [
    { key: 'calories', targetKey: 'calories_cibles', tolerance: 0.2, weight: 1 },
    { key: 'proteines', targetKey: 'proteine_cibles', tolerance: 0.25, weight: 1.2 },
    { key: 'glucides', targetKey: 'glucides_cibles', tolerance: 0.25, weight: 1 },
    { key: 'lipides', targetKey: 'lipides_cibles', tolerance: 0.25, weight: 1 },
    { key: 'fibres', targetKey: 'fibres_cibles', tolerance: 0.3, weight: 0.8 }
];
// Initialize Bootstrap dropdowns
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all dropdown toggles
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(function(element) {
        new bootstrap.Dropdown(element);
    });

    // Gestionnaire pour les recommandations N8N
    const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
    if (getRecommendationsBtn) {
        getRecommendationsBtn.addEventListener('click', function() {
            // Passer le profil_id si disponible en attribut data
            const profilId = this.dataset.profilId || null;
            getRecommendationsFromN8n(profilId);
        });
    }
});

// Fonction pour obtenir les recommandations du webhook N8N
// Support du mode synchrone et asynchrone
async function getRecommendationsFromN8n(profilId = null) {
    const btn = document.getElementById('getRecommendationsBtn');
    const loader = document.getElementById('recommendationsLoader');
    const resultDiv = document.getElementById('recommendationsResult');
    const contentDiv = document.getElementById('recommendationsContent');

    // Afficher le loader et désactiver le bouton
    btn.disabled = true;
    loader.style.display = 'block';
    resultDiv.style.display = 'none';

    try {
        // Obtenir le token CSRF de plusieurs sources possibles
        let token = null;
        
        // Essayer d'abord le meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            token = metaTag.getAttribute('content');
        }
        
        // Puis le formulaire
        if (!token) {
            const formInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (formInput) {
                token = formInput.value;
            }
        }
        
        // Puis le cookie
        if (!token) {
            token = getCookie('csrftoken');
        }
        
        // Puis le cookie Django
        if (!token) {
            token = getCookie('csrf');
        }
        
        // Construire le payload avec mode ASYNC
        const payload = {
            async: true  // Mode asynchrone - retourne immédiatement avec job_id
        };
        
        // Chercher profil_id de plusieurs sources
        if (profilId) {
            payload.profil_id = profilId;
        } else if (document.getElementById('getRecommendationsBtn')?.dataset?.profilId) {
            payload.profil_id = document.getElementById('getRecommendationsBtn').dataset.profilId;
        } else if (localStorage.getItem('profil_id')) {
            payload.profil_id = localStorage.getItem('profil_id');
        }
        
        console.log('Token CSRF obtenu:', !!token);
        console.log('Payload envoyé:', JSON.stringify(payload));
        console.log('Appel de l\'endpoint recommandations en mode ASYNC...');

        // Appeler l'endpoint
        const response = await fetch('/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': token || '',
                'Accept': 'application/json'
            },
            credentials: 'same-origin',  // Inclure les cookies
            body: JSON.stringify(payload)
        });

        console.log('Réponse reçue - Status:', response.status, 'Content-Type:', response.headers.get('content-type'));
        
        // Vérifier si la réponse est du JSON valide
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            try {
                data = await response.json();
            } catch (jsonError) {
                console.error('Erreur parsing JSON:', jsonError);
                // Si le JSON est invalide, afficher le texte brut
                const textResponse = await response.text();
                console.error('Réponse brute:', textResponse.substring(0, 500));
                throw new Error(`Réponse invalide du serveur: ${textResponse.substring(0, 200)}`);
            }
        } else {
            // Pas du JSON, lire comme texte
            const textResponse = await response.text();
            console.error('Réponse non-JSON reçue:', textResponse.substring(0, 500));
            throw new Error(`Réponse serveur invalide (${contentType || 'unknown'}). Vérifiez si l'endpoint API existe.`);
        }

        loader.style.display = 'none';
        resultDiv.style.display = 'block';

        if (!response.ok) {
            // Erreur HTTP
            console.error('Erreur HTTP:', response.status, data);
            contentDiv.innerHTML = `
                <div style="color: #ff6b6b; padding: 10px;">
                    <i class="fas fa-exclamation-circle"></i> 
                    <strong>Erreur ${response.status}:</strong> ${data.error || data.detail || 'Erreur inconnue'}
                </div>
            `;
            return;
        }

        // Mode ASYNC: réponse 202 Accepted avec job_id
        if (response.status === 202 || data.job_id) {
            console.log('Mode ASYNC - Job ID:', data.job_id);
            console.log('Statut:', data.status);
            
            contentDiv.innerHTML = `
                <div style="color: #ffd700; padding: 10px;">
                    <i class="fas fa-hourglass-half fa-spin"></i> 
                    <strong>Traitement en cours...</strong>
                    <br><small style="opacity: 0.8;">Veuillez patienter, les recommandations arrivent...</small>
                </div>
            `;
            
            // Lancer le polling pour récupérer les résultats
            pollJobStatus(data.job_id, contentDiv);
            return;
        }

        // Mode synchrone: affichage direct des recommandations
        if (data.success) {
            // Afficher les recommandations
            displayRecommendations(data, contentDiv);
        } else {
            contentDiv.innerHTML = `
                <div style="color: #ff6b6b; padding: 10px;">
                    <i class="fas fa-exclamation-circle"></i> ${data.error || 'Erreur lors du chargement'}
                </div>
            `;
        }
    } catch (error) {
        loader.style.display = 'none';
        resultDiv.style.display = 'block';
        
        console.error('Erreur complète:', error);
        console.error('Stack trace:', error.stack);
        
        let errorMessage = error.message || 'Erreur inconnue';
        let errorDetails = '';
        
        if (error instanceof SyntaxError) {
            errorMessage = 'Erreur de parsing JSON: La réponse du serveur n\'est pas du JSON valide';
            errorDetails = 'Cela peut signifier une erreur 500 ou un problème de serveur';
        } else if (error instanceof TypeError) {
            errorMessage = 'Erreur réseau: Impossible de se connecter au serveur';
            errorDetails = 'Vérifiez que le serveur est en cours d\'exécution et accessible';
        } else if (error.message.includes('Réponse invalide') || error.message.includes('Réponse non-JSON')) {
            errorMessage = error.message;
            errorDetails = 'Vérifiez les logs du serveur pour plus de détails';
        }
        
        contentDiv.innerHTML = `
            <div style="color: #ff6b6b; padding: 15px; border-radius: 8px; background: rgba(255,107,107,0.1); border-left: 4px solid #ff6b6b;">
                <i class="fas fa-exclamation-circle"></i> 
                <strong>Erreur:</strong> ${errorMessage}
                <br><small style="opacity: 0.9; display: block; margin-top: 8px;">${errorDetails}</small>
                <small style="opacity: 0.7; display: block; margin-top: 5px;">Message technique: ${error.message}</small>
            </div>
        `;
    } finally {
        btn.disabled = false;
    }
}

// ===== SECTION: Calcul des calories par repas =====

/**
 * Multiplicateurs d'activité (Harris-Benedict modifié)
 */
const ACTIVITY_MULTIPLIERS = {
    sedentaire: 1.2,
    peu_actif: 1.375,
    moderement_actif: 1.55,
    tres_actif: 1.725,
    extremement_actif: 1.9
};

/**
 * Distribution des calories par type de repas
 */
const MEAL_DISTRIBUTION = {
    petit_dejeuner: 0.25,      // 25%
    dejeuner: 0.40,            // 40%
    diner: 0.25,               // 25%
    collations: 0.10           // 10%
};

/**
 * Calcule les calories journalières totales (TDEE) à partir du BMR et du niveau d'activité
 * @param {number} bmr - Basal Metabolic Rate (calories de repos)
 * @param {string} niveauActivite - Niveau d'activité (sedentaire, peu_actif, moderement_actif, tres_actif, extremement_actif)
 * @returns {number} TDEE (Total Daily Energy Expenditure) en calories
 */
function calculateTDEE(bmr, niveauActivite) {
    if (!bmr || bmr <= 0) return 0;
    
    // Obtenir le multiplicateur d'activité (défaut: modérément actif)
    const multiplier = ACTIVITY_MULTIPLIERS[niveauActivite] || ACTIVITY_MULTIPLIERS.moderement_actif;
    
    return Math.round(bmr * multiplier);
}

/**
 * Calcule les calories par repas en fonction du TDEE
 * @param {number} tdee - Total Daily Energy Expenditure
 * @returns {Object} Distribution des calories {petit_dejeuner, dejeuner, diner, collations}
 */
function calculateCaloriesByMeal(tdee) {
    if (!tdee || tdee <= 0) {
        return {
            petit_dejeuner: 0,
            dejeuner: 0,
            diner: 0,
            collations: 0,
            total: 0
        };
    }
    
    return {
        petit_dejeuner: Math.round(tdee * MEAL_DISTRIBUTION.petit_dejeuner),
        dejeuner: Math.round(tdee * MEAL_DISTRIBUTION.dejeuner),
        diner: Math.round(tdee * MEAL_DISTRIBUTION.diner),
        collations: Math.round(tdee * MEAL_DISTRIBUTION.collations),
        total: tdee
    };
}

/**
 * Calcule les calories par repas à partir du BMR et du niveau d'activité
 * @param {number} bmr - Basal Metabolic Rate
 * @param {string} niveauActivite - Niveau d'activité
 * @param {Object} objectif - Objectif (perte_poids, maintien, prise_muscle, performance)
 * @returns {Object} Résultat complet {tdee, calories_par_repas, ajustement}
 */
function calculateMealCalories(bmr, niveauActivite, objectif = 'maintien') {
    // Étape 1: Calculer le TDEE
    const tdee = calculateTDEE(bmr, niveauActivite);
    
    // Étape 2: Appliquer un ajustement selon l'objectif
    let tdeeAdjuste = tdee;
    let ajustement = {
        facteur: 1,
        deficit_surplus: 0,
        raison: ''
    };
    
    switch(objectif) {
        case 'perte_poids':
            // Déficit calorique: -500 kcal/jour (-0.5 kg/semaine) ou -750 kcal/jour (-0.75 kg/semaine)
            ajustement.facteur = 0.85;  // 15% de déficit
            ajustement.deficit_surplus = Math.round(tdee * -0.15);
            ajustement.raison = 'Déficit calorique pour la perte de poids';
            tdeeAdjuste = tdee + ajustement.deficit_surplus;
            break;
            
        case 'prise_muscle':
            // Surplus calorique: +300-500 kcal/jour pour favoriser la prise de muscle
            ajustement.facteur = 1.10;  // 10% de surplus
            ajustement.deficit_surplus = Math.round(tdee * 0.10);
            ajustement.raison = 'Surplus calorique pour la prise de muscle';
            tdeeAdjuste = tdee + ajustement.deficit_surplus;
            break;
            
        case 'performance':
            // Ajustement modéré: +5-10% selon l'intensité d'entraînement
            ajustement.facteur = 1.08;
            ajustement.deficit_surplus = Math.round(tdee * 0.08);
            ajustement.raison = 'Apport calorique pour la performance sportive';
            tdeeAdjuste = tdee + ajustement.deficit_surplus;
            break;
            
        case 'maintien':
        default:
            ajustement.raison = 'Maintien du poids (pas d\'ajustement)';
            break;
    }
    
    // Étape 3: Calculer les calories par repas
    const caloriesParRepas = calculateCaloriesByMeal(tdeeAdjuste);
    
    return {
        bmr: bmr,
        niveau_activite: niveauActivite,
        objectif: objectif,
        tdee: tdee,
        tdee_ajuste: tdeeAdjuste,
        ajustement: ajustement,
        calories_par_repas: caloriesParRepas,
        calories_cibles: Math.round(tdeeAdjuste / 3)  // Moyenne par repas (pour compatibilité)
    };
}

/**
 * Détaille les calories par repas avec pourcentages
 * @param {Object} mealCalories - Résultat de calculateMealCalories()
 * @returns {Object} Détails formatés
 */
function detailMealCalories(mealCalories) {
    const repas = mealCalories.calories_par_repas;
    const total = repas.total;
    
    return {
        petit_dejeuner: {
            calories: repas.petit_dejeuner,
            pourcentage: `${Math.round((repas.petit_dejeuner / total) * 100)}%`
        },
        dejeuner: {
            calories: repas.dejeuner,
            pourcentage: `${Math.round((repas.dejeuner / total) * 100)}%`
        },
        diner: {
            calories: repas.diner,
            pourcentage: `${Math.round((repas.diner / total) * 100)}%`
        },
        collations: {
            calories: repas.collations,
            pourcentage: `${Math.round((repas.collations / total) * 100)}%`
        },
        total_journalier: total
    };
}

// ===== NOUVELLE SECTION: Calcul des recommandations basées sur les macronutriments (OPTIMISÉ) =====

// Cache pour optimiser les calculs répétés
const nutritionScoreCache = new Map();
const nutritionTotalsCache = new Map();

/**
 * Calcule le score du menu en faisant la moyenne des scores des plats (optimisé)
 * @param {Object} menu - Le menu
 * @returns {number} Score total du menu
 */
function calculateMenuScore(menu) {
    // Clé de cache basée sur l'ID du menu
    const cacheKey = `menu_score_${menu.id || menu.id_menu}`;
    if (nutritionScoreCache.has(cacheKey)) {
        return nutritionScoreCache.get(cacheKey);
    }
    
    const plates = menu.plats || menu.dishes || menu.items || [];
    
    let score = 0;
    if (Array.isArray(plates) && plates.length > 0) {
        const totalScore = plates.reduce((sum, plat) => 
            sum + (plat.score !== undefined ? plat.score : (plat.score_nutritionnel || 0)), 0);
        score = Math.round(totalScore / plates.length);
    } else {
        score = menu.score !== undefined ? menu.score : (menu.score_nutritionnel || 0);
    }
    
    nutritionScoreCache.set(cacheKey, score);
    return score;
}

/**
 * Calcule les totaux nutritionnels en faisant la somme des plats (optimisé)
 * @param {Object} item - Le plat ou menu
 * @returns {Object} Totaux {calories, proteines, glucides, lipides, fibres}
 */
function calculateNutritionTotals(item) {
    const cacheKey = `nutrition_${item.id || item.id_plat || item.id_menu}`;
    if (nutritionTotalsCache.has(cacheKey)) {
        return nutritionTotalsCache.get(cacheKey);
    }
    
    const totals = {
        calories: 0,
        proteines: 0,
        glucides: 0,
        lipides: 0,
        fibres: 0
    };
    
    // Extraire les plats selon le format
    const plates = item.plats || item.dishes || item.items || [];
    
    if (Array.isArray(plates) && plates.length > 0) {
        plates.forEach(plat => {
            totals.calories += (plat.calories || plat.calorie || 0);
            totals.proteines += (plat.proteines || plat.proteine || 0);
            totals.glucides += (plat.glucides || 0);
            totals.lipides += (plat.lipides || 0);
            totals.fibres += (plat.fibres || 0);
        });
    } else {
        // Utiliser les valeurs directes
        totals.calories = item.calories || item.calorie || 0;
        totals.proteines = item.proteines || item.proteine || 0;
        totals.glucides = item.glucides || 0;
        totals.lipides = item.lipides || 0;
        totals.fibres = item.fibres || 0;
    }
    
    nutritionTotalsCache.set(cacheKey, totals);
    return totals;
}

/**
 * Calcule le score pour un critère donné (optimisé)
 */
function computeCriterionScore(value, target, tolerance) {
    if (target === 0 || !target) return 0;
    
    const diffRatio = Math.abs(value - target) / target;
    
    // Utiliser une formule plus rapide
    if (diffRatio <= tolerance) {
        return 1 - (diffRatio / tolerance);
    }
    return Math.max(0, 1 - diffRatio);
}

/**
 * Calcule un score nutritionnel global (0 → 100) - OPTIMISÉ
 */
function calculateNutritionalScore(item, targets) {
    let totalScore = 0;
    let totalWeight = 0;
    
    // Parcourir directement sans chercher dynamiquement les clés
    for (let i = 0; i < NUTRITION_CRITERIA.length; i++) {
        const criterion = NUTRITION_CRITERIA[i];
        const value = item[criterion.key];
        const target = targets[criterion.targetKey];
        
        if (value != null && target != null) {
            totalScore += computeCriterionScore(value, target, criterion.tolerance) * criterion.weight;
            totalWeight += criterion.weight;
        }
    }
    
    return totalWeight === 0 ? 0 : Math.round((totalScore / totalWeight) * 100);
}

/**
 * Vider les caches nutritionnels
 */
function clearNutritionCaches() {
    nutritionScoreCache.clear();
    nutritionTotalsCache.clear();
}

/**
 * Version optimisée pour récupérer seulement les meilleurs éléments
 * 👉 Évite un tri complet si beaucoup de données
 */
function getTopK(items, k) {
    if (k >= items.length) {
        return items.slice().sort((a, b) => b.score - a.score);
    }
    
    // Pour petits k, utilisé une approche plus efficace
    return items
        .sort((a, b) => b.score - a.score)
        .slice(0, k);
}

/**
 * Filtre et recommande les plats/menus basés sur les critères nutritionnels
 * @param {Array} items - Liste des plats ou menus
 * @param {Object} targets - Les valeurs cibles nutritionnelles
 * @param {number} limit - Nombre d'éléments à retourner
 * @returns {Array} Éléments triés par score de recommandation
 */
function filterRecommendations(items, targets, limit = 6) {
    if (!items?.length) return [];

    const scoredItems = new Array(items.length);

    for (let i = 0; i < items.length; i++) {
        const item = items[i];

        scoredItems[i] = {
            ...item,
            score: calculateNutritionalScore(item, targets)
        };
    }

    return getTopK(scoredItems, limit);
}

/**
 * Génère les recommandations de menus et plats basés sur l'analyse nutritionnelle
 * @param {Object} platsList - Liste complète des plats disponibles
 * @param {Object} menusList - Liste complète des menus disponibles
 * @param {Object} profilAnalyse - Profil analysé avec les valeurs cibles
 * @returns {Object} Recommandations {plats: [], menus: []} - TRIÉS PAR SCORE DÉCROISSANT
 */
function generateNutritionalRecommendations(platsList, menusList, profilAnalyse) {
    const targets = {
        calories_cibles: profilAnalyse.calories_cibles,
        proteine_cibles: profilAnalyse.proteine_cibles,
        glucides_cibles: profilAnalyse.glucides_cibles,
        lipides_cibles: profilAnalyse.lipides_cibles,
        fibres_cibles: profilAnalyse.fibres_cibles
    };

    const recommendedPlats = filterRecommendations(platsList, targets, 100);
    let recommendedMenus = filterRecommendations(menusList, targets, 50);
    
    // Trier explicitement les menus par score décroissant
    recommendedMenus = recommendedMenus.sort((a, b) => {
        const scoreA = a.score !== undefined ? a.score : 0;
        const scoreB = b.score !== undefined ? b.score : 0;
        return scoreB - scoreA;  // Ordre décroissant (meilleur score d'abord)
    });

    return {
        recommandations: {
            plats: recommendedPlats,
            menus: recommendedMenus
        }
    };
}

// Fonction pour vérifier le statut du job async
// maxAttempts = 10 (5 minutes / 30 secondes par tentative)
// pollInterval = 30000ms (30 secondes)
async function pollJobStatus(jobId, contentDiv, maxAttempts = 10, pollInterval = 10000) {
    let attempts = 0;
    
    const poll = async () => {
        attempts++;
        
        try {
            const response = await fetch(
                `/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/job-status/?job_id=${jobId}`,
                {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    },
                    credentials: 'same-origin'
                }
            );
            
            console.log(`[Poll ${attempts}] Status:`, response.status, 'Content-Type:', response.headers.get('content-type'));
            
            // Vérifier si la réponse est du JSON valide
            const contentType = response.headers.get('content-type');
            let data;
            
            if (contentType && contentType.includes('application/json')) {
                try {
                    data = await response.json();
                } catch (jsonError) {
                    console.error(`[Poll ${attempts}] Erreur parsing JSON:`, jsonError);
                    const textResponse = await response.text();
                    console.error(`[Poll ${attempts}] Réponse brute (premier 500 chars):`, textResponse.substring(0, 500));
                    
                    // Si c'est une page HTML d'erreur (404 ou 500)
                    if (textResponse.includes('<!DOCTYPE') || textResponse.includes('<html')) {
                        console.error(`[Poll ${attempts}] Django error page détecté! Status: ${response.status}`);
                        throw new Error(`Erreur serveur (${response.status}): L'endpoint job-status n'est peut-être pas trouvé`);
                    }
                    
                    throw new Error(`Réponse JSON invalide: ${textResponse.substring(0, 100)}`);
                }
            } else {
                const textResponse = await response.text();
                console.error(`[Poll ${attempts}] Réponse non-JSON (Content-Type: ${contentType}):`, textResponse.substring(0, 500));
                
                // Si c'est une page HTML d'erreur
                if (textResponse.includes('<!DOCTYPE') || textResponse.includes('<html')) {
                    console.error(`[Poll ${attempts}] Django error page détecté!`);
                    throw new Error(`Erreur serveur Django (${response.status}): Vérifiez les logs du serveur`);
                }
                
                throw new Error(`Réponse non-JSON: ${contentType || 'unknown'}`);
            }
            
            console.log(`[Poll ${attempts}] Statut du job ${jobId}:`, data.status);
            
            if (data.status === 'completed') {
                console.log('Job complété avec succès');
                displayRecommendations(data, contentDiv);
                return;
            } else if (data.status === 'failed') {
                console.error('Job échoué');
                contentDiv.innerHTML = `
                    <div style="color: #ff6b6b; padding: 10px;">
                        <i class="fas fa-exclamation-circle"></i> 
                        <strong>Erreur:</strong> ${data.error || 'Erreur lors du traitement'}
                        <br><small style="opacity: 0.8;">${data.details || ''}</small>
                    </div>
                `;
                return;
            } else if (data.status === 'pending') {
                // Continuer le polling
                if (attempts < maxAttempts) {
                    console.log(`Polling... (${attempts}/${maxAttempts})`);
                    setTimeout(poll, pollInterval);
                } else {
                    console.error('Timeout - trop de tentatives');
                    contentDiv.innerHTML = `
                        <div style="color: #ff6b6b; padding: 10px;">
                            <i class="fas fa-exclamation-circle"></i> 
                            <strong>Timeout:</strong> Le traitement a pris trop longtemps
                            <br><small style="opacity: 0.8;">Réessayez plus tard</small>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error(`[Poll ${attempts}] Erreur lors du polling:`, error.message);
            console.error(`[Poll ${attempts}] Stack:`, error.stack);
            
            if (attempts < maxAttempts) {
                console.log(`Nouvelle tentative dans ${pollInterval}ms...`);
                setTimeout(poll, pollInterval);
            } else {
                contentDiv.innerHTML = `
                    <div style="color: #ff6b6b; padding: 15px; border-radius: 8px; background: rgba(255,107,107,0.1); border-left: 4px solid #ff6b6b;">
                        <i class="fas fa-exclamation-circle"></i> 
                        <strong>Erreur réseau:</strong> ${error.message}
                        <br><small style="opacity: 0.8;">Vérifiez la console pour plus de détails</small>
                        <br><small style="opacity: 0.7; margin-top: 5px; display: block;">Tentatives: ${attempts}/${maxAttempts}</small>
                    </div>
                `;
            }
        }
    };
    
    // Commencer le polling
    poll();
}

// Fonction pour afficher les recommandations
async function displayRecommendations(data, container) {
    console.log('Affichage des recommandations - données reçues:', data);
    
    // Extraire le profil analysé
    const profilAnalyse = data.recommendations?.profil_analyse;
    
    // Si on a un profil analysé, générer les recommandations côté client
    if (profilAnalyse) {
        try {
            console.log('Récupération des listes de plats et menus disponibles...');
            
            // Récupérer les listes complètes de plats et menus
            const [platsRes, menusRes] = await Promise.all([
                fetch('/plat/api/plats/', { credentials: 'same-origin' }),
                fetch('/menu/api/menus/', { credentials: 'same-origin' })
            ]);
            
            // Parser les réponses
            const platsData = await platsRes.json();
            const menusData = await menusRes.json();
            
            // Extraire les listes (gérer différents formats de réponse)
            const platsList = platsData.results || platsData.data || platsData || [];
            const menusList = menusData.results || menusData.data || menusData || [];
            
            console.log(`${platsList.length} plats disponibles, ${menusList.length} menus disponibles`);
            
            // Générer les recommandations nutritionnelles côté client
            const nutritionalRecommendations = generateNutritionalRecommendations(
                platsList,
                menusList,
                profilAnalyse
            );
            
            // Enrichir les données avec les recommandations calculées
            if (!data.recommendations) data.recommendations = {};
            if (!data.recommendations.recommandations) data.recommendations.recommandations = {};
            
            // Fusionner ou remplacer les recommandations
            data.recommendations.recommandations.plats = nutritionalRecommendations.recommandations.plats;
            data.recommendations.recommandations.menus = nutritionalRecommendations.recommandations.menus;
            
            console.log('Recommandations générées et intégrées');
        } catch (err) {
            console.warn('Impossible de générer les recommandations côté client:', err);
            console.warn('Les recommandations de N8N seront affichées si disponibles');
        }
    }
    
    // Afficher les recommandations (N8N enrichies ou seules)
    displayUnifiedRecommendations(data, container);
}

// Fonction unifiée pour afficher les recommandations (remplace les 3 anciennes fonctions)
function displayUnifiedRecommendations(data, container) {
    console.log('displayUnifiedRecommendations - données complètes:', data);
    
    // Extraire les données correctement de la structure imbriquée
    const profil = data.profil;
    const profil_analyse = data.recommendations?.profil_analyse;
    const recommendations = data.recommendations;
    
    let html = `<div>`;
    
    // ===== EN-TÊTE: Job ID, Message et Timestamp =====
    if (data.job_id || data.message || data.timestamp) {
        html += `
            <div style="margin-bottom: 15px; padding: 12px; background: rgba(76,175,80,0.15); border-left: 4px solid #4caf50; border-radius: 8px; font-size: 0.9em;">
        `;
        if (data.message) {
            html += `<div style="color: #4caf50; font-weight: 500; margin-bottom: 5px;"><i class="fas fa-check-circle"></i> ${data.message}</div>`;
        }
        if (data.timestamp) {
            const dateFormatted = new Date(data.timestamp).toLocaleString('fr-FR');
            html += `<small style="opacity: 0.7;">🕐 ${dateFormatted}</small>`;
        }
        html += `</div>`;
    }
    
    // ===== SECTION 1: Indicateurs nutritionnels (Profil vs Analyse) =====
    if (profil || profil_analyse) {
        html += `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #ffd700; margin-bottom: 10px;">📊 Analyse de votre profil nutritionnel:</h4>
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
        `;
        
        // IMC: Profil vs Analyse
        if (profil?.imc !== undefined || profil_analyse?.imc !== undefined) {
            const imcProfil = profil?.imc !== undefined ? parseFloat(profil.imc).toFixed(2) : null;
            const imcAnalyse = profil_analyse?.imc !== undefined ? parseFloat(profil_analyse.imc).toFixed(2) : imcProfil;
            const imcChanged = imcProfil && imcAnalyse && imcProfil !== imcAnalyse;
            
            html += `
                <div style="background: rgba(69,183,209,0.2); padding: 12px; border-radius: 8px; border-left: 4px solid #45b7d1;">
                    <div style="font-size: 22px; font-weight: bold; color: #45b7d1; text-align: center;">${imcAnalyse}</div>
                    <small style="text-align: center; display: block;">IMC</small>
                    ${imcChanged ? `<small style="opacity: 0.6; font-size: 0.75em; display: block; margin-top: 5px; text-align: center;">avant: ${imcProfil}</small>` : ''}
                </div>
            `;
        }
        
        // BMR: Profil vs Analyse
        if (profil?.bmr !== undefined || profil_analyse?.bmr !== undefined) {
            const bmrProfil = profil?.bmr !== undefined ? Math.round(profil.bmr) : null;
            const bmrAnalyse = profil_analyse?.bmr !== undefined ? Math.round(profil_analyse.bmr) : bmrProfil;
            const bmrChanged = bmrProfil && bmrAnalyse && bmrProfil !== bmrAnalyse;
            
            html += `
                <div style="background: rgba(78,205,196,0.2); padding: 12px; border-radius: 8px; border-left: 4px solid #4ecdc4;">
                    <div style="font-size: 22px; font-weight: bold; color: #4ecdc4; text-align: center;">${bmrAnalyse}</div>
                    <small style="text-align: center; display: block;">BMR (kcal/j)</small>
                    ${bmrChanged ? `<small style="opacity: 0.6; font-size: 0.75em; display: block; margin-top: 5px; text-align: center;">avant: ${bmrProfil}</small>` : ''}
                </div>
            `;
        }
        
        // Calories par repas: Profil vs Analyse (calculées avec calculateMealCalories)
        if (profil?.bmr !== undefined || profil_analyse?.bmr !== undefined) {
            const bmr = profil_analyse?.bmr !== undefined ? profil_analyse.bmr : profil?.bmr;
            const niveauActivite = profil?.niveau_activite || 'moderement_actif';
            const objectif = profil?.objectif || 'maintien';
            
            // Calculer les calories par repas
            const mealCalories = calculateMealCalories(bmr, niveauActivite, objectif);
            const caloriesParRepas = mealCalories.calories_cibles;
            
            html += `
                <div style="background: rgba(255,215,0,0.2); padding: 12px; border-radius: 8px; border-left: 4px solid #ffd700;">
                    <div style="font-size: 22px; font-weight: bold; color: #ffd700; text-align: center;">${caloriesParRepas}</div>
                    <small style="text-align: center; display: block;">Calories par repas</small>
                    <small style="opacity: 0.6; font-size: 0.75em; display: block; margin-top: 5px; text-align: center;">TDEE: ${mealCalories.tdee} kcal/j</small>
                </div>
            `;
        }
        
        html += `</div></div></div>`;
    }
    
    // ===== SECTION 2: Informations de base du profil =====
    if (profil) {
        html += `
            <div style="margin-bottom: 20px; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 8px; font-size: 0.95em;">
                <h5 style="color: #b0bec5; margin-bottom: 10px; font-weight: 500;">ℹ️ Profil</h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 10px;">
        `;
        
        if (profil.age !== undefined) {
            html += `<div><strong>Âge:</strong> ${profil.age} ans</div>`;
        }
        if (profil.sexe) {
            const sexeLabel = profil.sexe === 'femme' ? '👩' : '👨';
            html += `<div><strong>Sexe:</strong> ${sexeLabel} ${profil.sexe}</div>`;
        }
        if (profil.poids !== undefined && profil.taille !== undefined) {
            html += `<div><strong>Mesures:</strong> ${profil.poids}kg / ${profil.taille}cm</div>`;
        }
        if (profil.niveau_activite) {
            html += `<div><strong>Activité:</strong> ${profil.niveau_activite.replace(/_/g, ' ')}</div>`;
        }
        if (profil.objectif) {
            html += `<div><strong>Objectif:</strong> ${getObjectifLabel(profil.objectif)}</div>`;
        }
        if (profil.categorie_imc) {
            html += `<div><strong>Catégorie IMC:</strong> ${profil.categorie_imc}</div>`;
        }
        
        html += `</div>`;
        
        // Restrictions alimentaires
        if (profil.allergies || profil.restrictions_alimentaires) {
            html += `<div style="padding: 10px; background: rgba(255,152,0,0.1); border-radius: 6px; margin-top: 10px;">`;
            if (profil.allergies) {
                html += `<div><strong style="color: #ff9800;">⚠️ Allergies:</strong> ${profil.allergies}</div>`;
            }
            if (profil.restrictions_alimentaires) {
                html += `<div><strong style="color: #ff9800;">🚫 Restrictions:</strong> ${profil.restrictions_alimentaires}</div>`;
            }
            html += `</div>`;
        }
        
        html += `</div>`;
    }
    
    // ===== SECTION 3: Macronutriments cibles (de profil_analyse) =====
    if (profil_analyse) {
        const hasProteines = profil_analyse.proteine_cibles !== undefined;
        const hasGlucides = profil_analyse.glucides_cibles !== undefined;
        const hasLipides = profil_analyse.lipides_cibles !== undefined;
        const hasFibres = profil_analyse.fibres_cibles !== undefined;
        
        if (hasProteines || hasGlucides || hasLipides || hasFibres) {
            html += `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #4ecdc4; margin-bottom: 10px;">🥗 Macronutriments cibles (g/plat):</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px;">
            `;
            
            if (hasProteines) {
                html += `
                    <div style="background: rgba(255,107,107,0.2); padding: 12px; border-radius: 8px; border-left: 4px solid #ff6b6b; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #ff6b6b;">${parseFloat(profil_analyse.proteine_cibles).toFixed(1)}</div>
                        <small>Protéines</small>
                    </div>
                `;
            }
            
            if (hasGlucides) {
                html += `
                    <div style="background: rgba(255,193,7,0.2); padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #ffc107;">${parseFloat(profil_analyse.glucides_cibles).toFixed(1)}</div>
                        <small>Glucides</small>
                    </div>
                `;
            }
            
            if (hasLipides) {
                html += `
                    <div style="background: rgba(76,175,80,0.2); padding: 12px; border-radius: 8px; border-left: 4px solid #4caf50; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #4caf50;">${parseFloat(profil_analyse.lipides_cibles).toFixed(1)}</div>
                        <small>Lipides</small>
                    </div>
                `;
            }
            
            if (hasFibres) {
                html += `
                    <div style="background: rgba(156,39,176,0.2); padding: 12px; border-radius: 8px; border-left: 4px solid #9c27b0; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold; color: #9c27b0;">${parseFloat(profil_analyse.fibres_cibles).toFixed(1)}</div>
                        <small>Fibres</small>
                    </div>
                `;
            }
            
            html += `</div></div>`;
        }
    }
    
    // ===== SECTION 4: Recommandations de plats et menus =====
    if (recommendations && recommendations.recommandations) {
        const recs = recommendations.recommandations;
        
        // Affichage des plats en grille (style specialdiet)
        if (recs.plats && recs.plats.length > 0) {
            html += `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #ff9800; margin-bottom: 15px; font-size: 1.5rem;">🍽️ Plats recommandés pour vous</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem;">
            `;
            
            recs.plats.slice(0, 100).forEach(plat => {
                // Récupérer les propriétés du plat
                const platId = plat.id !== undefined ? plat.id : plat.id_plat;
                const platNom = plat.nom || plat.name || `Plat #${platId}`;
                const platScore = plat.score !== undefined ? plat.score : plat.score_nutritionnel || 0;
                
                // Calculer les totaux nutritionnels
                const nutrition = calculateNutritionTotals(plat);
                const calories = nutrition.calories;
                const proteines = nutrition.proteines;
                const glucides = nutrition.glucides;
                const lipides = nutrition.lipides;
                const fibres = nutrition.fibres;
                const platImage = plat.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500';
                
                // Déterminer la couleur du score
                let scoreClass = 'score-low';
                let scoreIcon = '😐';
                let scoreColor = '#C67C4E';
                
                if (platScore >= 80) {
                    scoreClass = 'score-excellent';
                    scoreIcon = '⭐';
                    scoreColor = '#FFD700';
                } else if (platScore >= 60) {
                    scoreClass = 'score-good';
                    scoreIcon = '👍';
                    scoreColor = '#9BBF8F';
                } else if (platScore >= 40) {
                    scoreClass = 'score-ok';
                    scoreIcon = '😊';
                    scoreColor = '#E8DCC6';
                }
                
                html += `
                    <div style="background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 10px 25px rgba(46,74,47,0.08); transition: all 0.3s ease; display: flex; flex-direction: column;">
                        <!-- Image section -->
                        <div style="position: relative; height: 180px; overflow: hidden;">
                            <img src="${platImage}" alt="${platNom}" style="width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s ease;" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                            
                            <!-- Badges nutritionnels -->
                            <div style="position: absolute; top: 12px; left: 12px; background: #9BBF8F; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.7rem; font-weight: bold;">Recommandé</div>
                            
                            <!-- Cercle protéines -->
                            <div style="position: absolute; bottom: 12px; right: 12px; background: white; width: 50px; height: 50px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: bold; font-size: 0.85rem; border: 2px solid #9BBF8F; box-shadow: 0 4px 10px rgba(0,0,0,0.1); z-index: 2;">
                                <span>${Math.round(proteines)}</span>
                                <span style="font-size: 0.6rem; font-weight: normal;">g PROT</span>
                            </div>
                            
                            <!-- Badge score -->
                            <div style="position: absolute; top: 12px; right: 12px; width: 55px; height: 55px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: bold; font-size: 0.7rem; box-shadow: 0 4px 10px rgba(0,0,0,0.15); z-index: 3; border: 3px solid white; background: linear-gradient(135deg, ${scoreColor}, ${scoreColor}80); color: white;">
                                <span style="font-size: 1rem; font-weight: bold;">${Math.round(platScore)}</span>
                                <span style="font-size: 0.5rem; opacity: 0.8;">Score</span>
                                <span style="font-size: 0.8rem;">${scoreIcon}</span>
                            </div>
                        </div>
                        
                        <!-- Contenu -->
                        <div style="padding: 1rem; flex: 1; display: flex; flex-direction: column;">
                            <h3 style="font-size: 1rem; margin-bottom: 0.8rem; color: #2E4A2F; margin: 0 0 0.8rem 0;">${platNom}</h3>
                            
                            <!-- Tableau nutritionnel -->
                            <div style="display: flex; gap: 0.6rem; background: #F5EDDA; padding: 0.6rem; border-radius: 12px; font-size: 0.7rem; margin-bottom: 1rem; flex: 1; align-items: center;">
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🔥 Cal</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(calories)}</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">💪 Prot</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(proteines)}g</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🍚 Gluc</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(glucides)}g</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🌾 Lip</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(lipides)}g</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🌿 Fib</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(fibres)}g</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `</div></div>`;
        }
        
        // Affichage des menus en grille (style specialdiet)
        if (recs.menus && recs.menus.length > 0) {
            html += `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #4caf50; margin-bottom: 15px; font-size: 1.5rem;">📋 Menus recommandés pour vous</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem;">
            `;
            
            // Trier les menus par score décroissant (meilleur score d'abord)
            const sortedMenus = recs.menus.slice().sort((a, b) => {
                const scoreA = calculateMenuScore(a);
                const scoreB = calculateMenuScore(b);
                return scoreB - scoreA;
            });
            
            sortedMenus.slice(0, 50).forEach(menu => {
                // Récupérer les propriétés du menu
                const menuId = menu.id !== undefined ? menu.id : menu.id_menu;
                const menuNom = menu.nom || menu.name || `Menu #${menuId}`;
                
                // Calculer le score du menu comme somme des scores des plats
                const menuScore = calculateMenuScore(menu);
                
                // Calculer les totaux nutritionnels en faisant la somme des plats
                const nutrition = calculateNutritionTotals(menu);
                const calories = nutrition.calories;
                const proteines = nutrition.proteines;
                const glucides = nutrition.glucides;
                const lipides = nutrition.lipides;
                const fibres = nutrition.fibres;
                const menuImage = menu.image || 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500';
                
                // Déterminer la couleur du score
                let scoreClass = 'score-low';
                let scoreIcon = '😐';
                let scoreColor = '#C67C4E';
                
                if (menuScore >= 80) {
                    scoreClass = 'score-excellent';
                    scoreIcon = '⭐';
                    scoreColor = '#FFD700';
                } else if (menuScore >= 60) {
                    scoreClass = 'score-good';
                    scoreIcon = '👍';
                    scoreColor = '#4caf50';
                } else if (menuScore >= 40) {
                    scoreClass = 'score-ok';
                    scoreIcon = '😊';
                    scoreColor = '#E8DCC6';
                }
                
                html += `
                    <div style="background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 10px 25px rgba(46,74,47,0.08); transition: all 0.3s ease; display: flex; flex-direction: column;">
                        <!-- Image section -->
                        <div style="position: relative; height: 180px; overflow: hidden;">
                            <img src="${menuImage}" alt="${menuNom}" style="width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s ease;" onerror="this.src='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500'">
                            
                            <!-- Badges nutritionnels -->
                            <div style="position: absolute; top: 12px; left: 12px; background: #4caf50; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.7rem; font-weight: bold;">Menu</div>
                            
                            <!-- Cercle protéines -->
                            <div style="position: absolute; bottom: 12px; right: 12px; background: white; width: 50px; height: 50px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: bold; font-size: 0.85rem; border: 2px solid #4caf50; box-shadow: 0 4px 10px rgba(0,0,0,0.1); z-index: 2;">
                                <span>${Math.round(proteines)}</span>
                                <span style="font-size: 0.6rem; font-weight: normal;">g PROT</span>
                            </div>
                            
                            <!-- Badge score -->
                            <div style="position: absolute; top: 12px; right: 12px; width: 55px; height: 55px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; font-weight: bold; font-size: 0.7rem; box-shadow: 0 4px 10px rgba(0,0,0,0.15); z-index: 3; border: 3px solid white; background: linear-gradient(135deg, ${scoreColor}, ${scoreColor}80); color: white;">
                                <span style="font-size: 1rem; font-weight: bold;">${Math.round(menuScore)}</span>
                                <span style="font-size: 0.5rem; opacity: 0.8;">Score</span>
                                <span style="font-size: 0.8rem;">${scoreIcon}</span>
                            </div>
                        </div>
                        
                        <!-- Contenu -->
                        <div style="padding: 1rem; flex: 1; display: flex; flex-direction: column;">
                            <h3 style="font-size: 1rem; margin-bottom: 0.8rem; color: #2E4A2F; margin: 0 0 0.8rem 0;">${menuNom}</h3>
                            
                            <!-- Tableau nutritionnel -->
                            <div style="display: flex; gap: 0.6rem; background: #F5EDDA; padding: 0.6rem; border-radius: 12px; font-size: 0.7rem; margin-bottom: 1rem; flex: 1; align-items: center;">
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🔥 Cal</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(calories)}</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">💪 Prot</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(proteines)}g</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🍚 Gluc</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(glucides)}g</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🌾 Lip</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(lipides)}g</strong>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="font-size: 0.6rem; color: #6C7A6A; margin-bottom: 0.2rem;">🌿 Fib</div>
                                    <strong style="font-size: 0.8rem;">${Math.round(fibres)}g</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += `</div></div>`;
        }
    }
    
    html += `</div>`;
    container.innerHTML = html;
}

// Fonction utilitaire pour convertir l'objectif en label lisible
function getObjectifLabel(objectif) {
    const labels = {
        'perte_poids': 'Perte de poids',
        'maintien': 'Maintien',
        'prise_muscle': 'Prise de muscle',
        'performance': 'Performance sportive'
    };
    return labels[objectif] || objectif;
}

// Fonction pour obtenir le cookie CSRF
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

