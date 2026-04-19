// Initialize Bootstrap dropdowns
document.addEventListener('DOMContentLoaded', function() {
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(function(element) {
        new bootstrap.Dropdown(element);
    });
});

// ========== DONNÉES DES PLATS (MENU COMPLET) ==========
const meals = [
    { id: 1, name: "Soupe Thaï Épicée", calories: 605, protein: 45, category: "nouveau", image: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500", isNew: true },
    { id: 2, name: "Poulet haché épicé à l'indienne", calories: 605, protein: 36, category: "proteine", image: "https://i.pinimg.com/736x/37/92/c6/3792c648a719ed62cd6e5a953f0d7b9f.jpg", isNew: true },
    { id: 3, name: "Poulet au curry rouge", calories: 649, protein: 43, category: "nouveau", image: "https://i.pinimg.com/736x/a8/b2/9a/a8b29abc90e533e4031abb73168cce31.jpg", isNew: true },
    { id: 4, name: "Couscous Rouge Poulet", calories: 512, protein: 46, category: "nouveau", image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500", isNew: true },
    { id: 5, name: "Emincé de bœuf sauce tomate", calories: 562, protein: 27, category: "proteine", image: "https://i.pinimg.com/1200x/32/07/d3/3207d311e5c745f61518597e33d86d1b.jpg", isNew: false },
    { id: 6, name: "Poulet enrobé de noix de coco", calories: 465, protein: 45, category: "proteine", image: "https://i.pinimg.com/736x/69/34/ba/6934ba3ec7f9de248de860f6e4830b38.jpg", isNew: false },
    { id: 7, name: "Burrito Bowl", calories: 625, protein: 37, category: "proteine", image: "https://i.pinimg.com/1200x/16/1a/3c/161a3ce313f3e627e0bfabcb374bcbaa.jpg", isNew: false },
    { id: 8, name: "Poulet & chou fleur curry rouge", calories: 619, protein: 49, category: "proteine", image: "https://i.pinimg.com/736x/8f/69/7e/8f697ef82a1f3f791f2de4fa583b404e.jpg", isNew: false },
    { id: 9, name: "Gratin d'aubergines à la viande hachée", calories: 970, protein: 43, category: "proteine", image: "https://i.pinimg.com/1200x/de/d3/26/ded326e6df44a397bab496b5b3c0790b.jpg", isNew: false },
    { id: 10, name: "Thai Ginger & Sea Bass Soup", calories: 500, protein: 50, category: "proteine", image: "https://i.pinimg.com/1200x/b9/90/77/b99077d3680bdce5367fcb5e5139b858.jpg", isNew: false },
    { id: 11, name: "Mediterranean Sea Bream Papillote", calories: 650, protein: 48, category: "proteine", image: "https://i.pinimg.com/1200x/00/af/0d/00af0de81b6508251c77fe24c9f5fbec.jpg", isNew: false },
    { id: 12, name: "Quinoa Harvest Salad", calories: 450, protein: 43, category: "proteine", image: "https://i.pinimg.com/1200x/44/62/67/446267fca26bb55c174375e9a4d19371.jpg", isNew: false },
    { id: 13, name: "Chili con carne", calories: 360, protein: 25, category: "proteine", image: "https://i.pinimg.com/736x/97/93/f5/9793f58edd246306b8a7a02be2752313.jpg", isNew: false },
    { id: 14, name: "Tuna Tataki with Sesame Crust", calories: 970, protein: 43, category: "proteine", image: "https://i.pinimg.com/1200x/0f/08/8f/0f088fb40e5965304501cd76556ed459.jpg", isNew: false },
    { id: 15, name: "Creamy Salmon & Dill Soup", calories: 550, protein: 25, category: "proteine", image: "https://i.pinimg.com/1200x/e0/22/6d/e0226dfb0fafb39b21cbc2de2a8fa938.jpg", isNew: false },
    { id: 16, name: "Poulet au chou rouge & spätzle", calories: 545, protein: 43, category: "proteine", image: "https://i.pinimg.com/736x/4b/bc/97/4bbc975325e237e40a9e0c21b05db5fa.jpg", isNew: false },
    { id: 17, name: "Filet de colin et riz", calories: 725, protein: 36, category: "proteine", image: "https://i.pinimg.com/1200x/0a/de/79/0ade7984202f9a1b1b47f18d91548336.jpg", isNew: false }
];

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
    displayMeals();
    console.log('🌿 Menu Fresh & Greens chargé avec succès !');
});