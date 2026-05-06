/**
 * NUTRIENTS VISUALIZATION - Générateur de graphiques
 * 
 * Cette fonction génère dynamiquement les barres de comparaison pour la section
 * "Visualisation des Nutriments" du modal de comparaison.
 */

/**
 * Données de structure des nutriments
 * À adapter selon votre API/base de données
 */
const NUTRIENT_CONFIG = {
    calories: {
        nutrient: 'calories',
        icon: '🔥',
        label: 'Calories',
        unit: 'kcal',
        color: 'var(--nutrient-calories)',
        chartId: 'caloriesChart',
    },
    proteins: {
        nutrient: 'proteins',
        icon: '💪',
        label: 'Protéines',
        unit: 'g',
        color: 'var(--nutrient-proteins)',
        chartId: 'proteinChart',
    },
    carbs: {
        nutrient: 'carbs',
        icon: '🌾',
        label: 'Glucides',
        unit: 'g',
        color: 'var(--nutrient-carbs)',
        chartId: 'carbsChart',
    },
    fats: {
        nutrient: 'fats',
        icon: '🧈',
        label: 'Lipides',
        unit: 'g',
        color: 'var(--nutrient-fats)',
        chartId: 'fatChart',
    }
};

/**
 * Exemple de données menus (à remplacer par vos vraies données)
 */
const MENU_DATA_EXAMPLE = [
    {
        id: 'menu1',
        name: 'Menu automatique 21',
        calories: 520,
        proteins: 28,
        carbs: 65,
        fats: 12
    },
    {
        id: 'menu2',
        name: 'Menu automatique 22',
        calories: 480,
        proteins: 35,
        carbs: 52,
        fats: 14
    },
    {
        id: 'menu3',
        name: 'Menu automatique 23',
        calories: 550,
        proteins: 25,
        carbs: 70,
        fats: 16
    }
];

/**
 * Génère les barres de comparaison pour un nutriment
 * @param {string} nutrientKey - Clé du nutriment (calories, proteins, carbs, fats)
 * @param {Array} selectedMenus - Tableau des menus sélectionnés avec leurs données nutritionnelles
 * @returns {void}
 */
function renderNutrientChart(nutrientKey, selectedMenus) {
    const config = NUTRIENT_CONFIG[nutrientKey];
    const chartContainer = document.getElementById(config.chartId);
    
    if (!chartContainer) {
        console.warn(`Chart container not found: ${config.chartId}`);
        return;
    }

    // Vider le conteneur
    chartContainer.innerHTML = '';

    // Trouver la valeur max pour normaliser les hauteurs des barres
    const maxValue = Math.max(
        ...selectedMenus.map(menu => menu[nutrientKey] || 0)
    );

    // Générer les barres
    selectedMenus.forEach((menu, index) => {
        const value = menu[nutrientKey] || 0;
        const percentage = (value / maxValue) * 100;

        const barGroup = document.createElement('div');
        barGroup.className = 'chart-bar-group';

        // Barre de valeur
        const barItem = document.createElement('div');
        barItem.className = 'chart-bar-item';

        const barFill = document.createElement('div');
        barFill.className = 'chart-bar-fill';
        barFill.setAttribute('tabindex', '0');
        barFill.setAttribute('role', 'button');
        barFill.setAttribute('aria-label', `${config.label}: ${value}${config.unit}`);
        barFill.style.height = `${percentage}%`;
        barFill.style.setProperty('--nutrient-color', getComputedStyle(document.documentElement).getPropertyValue(config.color.split('(')[1].split(')')[0]));

        // Valeur affichée au-dessus
        const valueLabel = document.createElement('div');
        valueLabel.className = 'chart-value';
        valueLabel.textContent = `${value}`;
        barFill.appendChild(valueLabel);

        barItem.appendChild(barFill);
        barGroup.appendChild(barItem);

        // Label du menu
        const label = document.createElement('div');
        label.className = 'chart-label';
        label.textContent = menu.name || `Menu ${index + 1}`;
        barGroup.appendChild(label);

        chartContainer.appendChild(barGroup);

        // Ajouter événement keyboard
        barFill.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                // Déclencher une action si nécessaire
            }
        });
    });
}

/**
 * Initialise tous les graphiques de nutriments
 * @param {Array} selectedMenus - Tableau des menus sélectionnés
 * @returns {void}
 */
function initializeNutrientCharts(selectedMenus) {
    if (!selectedMenus || selectedMenus.length === 0) {
        console.warn('No menus to display');
        return;
    }

    Object.keys(NUTRIENT_CONFIG).forEach(nutrientKey => {
        renderNutrientChart(nutrientKey, selectedMenus);
    });
}

/**
 * Exemple d'utilisation dans le contexte du modal
 * À intégrer dans votre logique de comparaison existante
 */
function exampleUsage() {
    // Simuler une sélection de menus
    const selectedMenus = MENU_DATA_EXAMPLE.slice(0, 2);
    
    // Initialiser les graphiques
    initializeNutrientCharts(selectedMenus);

    // Ajouter des écouteurs pour les interactions au hover
    document.querySelectorAll('.chart-bar-fill').forEach(bar => {
        bar.addEventListener('mouseenter', function() {
            // Animation au survol (géré par CSS)
        });

        bar.addEventListener('mouseleave', function() {
            // Fin d'animation
        });
    });
}

/**
 * Helper: Obtenir la couleur CSS d'une variable
 * @param {string} varName - Nom de la variable CSS
 * @returns {string}
 */
function getCSSVariableColor(varName) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(varName)
        .trim();
}

/**
 * Integration avec votre système de comparaison existant
 * À appeler après que l'utilisateur sélectionne ses menus
 */
function onComparisonMenusSelected(selectedMenuIds, allMenusData) {
    // Filtrer les données des menus sélectionnés
    const selectedMenus = allMenusData.filter(menu => 
        selectedMenuIds.includes(menu.id)
    );

    // Initialiser les graphiques
    initializeNutrientCharts(selectedMenus);

    // Optionnel: Afficher la section de visualisation
    const visualizationSection = document.querySelector('.nutrients-visualization');
    if (visualizationSection) {
        visualizationSection.style.display = 'block';
    }
}

/* ========================================
   EXPORT POUR UTILISATION EN MODULE
   ======================================== */

// Si vous utilisez ES6 modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        NUTRIENT_CONFIG,
        MENU_DATA_EXAMPLE,
        renderNutrientChart,
        initializeNutrientCharts,
        onComparisonMenusSelected,
        getCSSVariableColor
    };
}

// Sinon, exposer en global si nécessaire
window.NutrientVisualization = {
    NUTRIENT_CONFIG,
    MENU_DATA_EXAMPLE,
    renderNutrientChart,
    initializeNutrientCharts,
    onComparisonMenusSelected,
    getCSSVariableColor
};
