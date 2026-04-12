// ========== DONNÉES DES PLATS PAR CATÉGORIE DIET ==========
const dietMeals = {
    "high-protein": [
        { name: "Poulet grillé aux herbes", calories: 380, protein: 42, carbs: 15, image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500", description: "Poulet fermier grillé, herbes de Provence" },
        { name: "Saumon à la vapeur", calories: 420, protein: 38, carbs: 8, image: "https://i.pinimg.com/1200x/b9/90/77/b99077d3680bdce5367fcb5e5139b858.jpg", description: "Saumon frais, asperges, citron" },
        { name: "Bœuf aux légumes", calories: 480, protein: 45, carbs: 20, image: "https://i.pinimg.com/1200x/32/07/d3/3207d311e5c745f61518597e33d86d1b.jpg", description: "Emincé de bœuf, légumes croquants" },
        { name: "Omelette protéinée", calories: 320, protein: 30, carbs: 10, image: "https://i.pinimg.com/736x/69/34/ba/6934ba3ec7f9de248de860f6e4830b38.jpg", description: "3 œufs, fromage, épinards" },
        { name: "Thon albacore", calories: 350, protein: 40, carbs: 5, image: "https://i.pinimg.com/1200x/0f/08/8f/0f088fb40e5965304501cd76556ed459.jpg", description: "Thon mi-cuit, sésame, sauce soja" }
    ],
    "low-carb": [
        { name: "Salade César poulet", calories: 320, protein: 35, carbs: 12, image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500", description: "Poulet, parmesan, sauce légère" },
        { name: "Poisson aux légumes verts", calories: 280, protein: 32, carbs: 10, image: "https://i.pinimg.com/1200x/00/af/0d/00af0de81b6508251c77fe24c9f5fbec.jpg", description: "Daurade, brocoli, courgettes" },
        { name: "Bowl méditerranéen", calories: 350, protein: 28, carbs: 18, image: "https://i.pinimg.com/1200x/44/62/67/446267fca26bb55c174375e9a4d19371.jpg", description: "Concombre, tomates, feta, olives" },
        { name: "Œufs brouillés avocat", calories: 290, protein: 22, carbs: 9, image: "https://i.pinimg.com/736x/8f/69/7e/8f697ef82a1f3f791f2de4fa583b404e.jpg", description: "Œufs frais, avocat, pain complet" }
    ],
    "vegan": [
        { name: "Bowl Quinoa & Légumes", calories: 420, protein: 15, carbs: 55, image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500", description: "Quinoa, légumes rôtis, tahini" },
        { name: "Curry de pois chiches", calories: 380, protein: 14, carbs: 48, image: "https://i.pinimg.com/736x/a8/b2/9a/a8b29abc90e533e4031abb73168cce31.jpg", description: "Pois chiches, lait de coco, épices" },
        { name: "Salade d'été", calories: 250, protein: 8, carbs: 30, image: "https://i.pinimg.com/1200x/e9/19/ef/e919effd2e1970f9f81db84f785c0ade.jpg", description: "Tomates, concombres, avocat, citron" },
        { name: "Buddha Bowl", calories: 450, protein: 18, carbs: 52, image: "https://i.pinimg.com/1200x/44/62/67/446267fca26bb55c174375e9a4d19371.jpg", description: "Riz complet, edamame, patate douce" }
    ],
    "gluten-free": [
        { name: "Soupe de lentilles", calories: 280, protein: 15, carbs: 35, image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500", description: "Lentilles corail, légumes doux" },
        { name: "Filet de poulet rôti", calories: 350, protein: 38, carbs: 8, image: "https://i.pinimg.com/736x/37/92/c6/3792c648a719ed62cd6e5a953f0d7b9f.jpg", description: "Poulet fermier, romarin, ail" },
        { name: "Saumon au four", calories: 420, protein: 40, carbs: 5, image: "https://i.pinimg.com/1200x/b9/90/77/b99077d3680bdce5367fcb5e5139b858.jpg", description: "Saumon, citron, aneth" },
        { name: "Gratin de chou-fleur", calories: 310, protein: 12, carbs: 18, image: "https://i.pinimg.com/736x/8f/69/7e/8f697ef82a1f3f791f2de4fa583b404e.jpg", description: "Chou-fleur, crème végétale" }
    ]
};

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
    "gluten-free": "Sans Gluten"
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

    dietGrid.innerHTML = meals.map(meal => `
        <div class="meal-card">
            <div class="meal-img">
                <img src="${meal.image}" alt="${meal.name}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                <div class="badge-diet">${dietName}</div>
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
                    <div class="nutri-item">
                        <span>🍚 Glucides</span>
                        ${meal.carbs}g
                    </div>
                </div>
            </div>
        </div>
    `).join('');
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
    displayDietMeals();
    console.log('🌿 Special Diet Fresh & Greens chargé avec succès !');
});