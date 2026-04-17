/**
 * Unified Browse - Combined Menus and Dishes
 * Handles both Plat and Menu items with filtering by diet category
 */

// ========== GLOBAL STATE ==========
let allItems = [];
let filteredItems = [];
let currentDietFilter = 'all';
let currentViewFilter = 'all';
let currentSearchQuery = '';
let selectedItemId = null;
let selectedItemType = null;

// ========== DOM REFERENCES ==========
const itemsGrid = document.getElementById('itemsGrid');
const noResults = document.getElementById('noResults');
const searchInput = document.getElementById('searchInput');
const dietFilterButtons = document.querySelectorAll('.diet-filter-btn');
const viewButtons = document.querySelectorAll('.view-btn');
const addToCartModal = document.getElementById('addToCartModal');
const addToCartForm = document.getElementById('addToCartForm');
const quantityInput = document.getElementById('quantity');
const itemInfoDisplay = document.getElementById('itemInfo');
const closeBtn = document.querySelector('.modal .close');

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap dropdowns
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(element => {
        new bootstrap.Dropdown(element);
    });

    // Load all items
    loadAllItems();
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('🌿 Unified Browse loaded successfully!');
});

// ========== API CALLS ==========
function loadAllItems() {
    fetch('/api/menus-and-plats/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Items loaded from API:', data);
            allItems = Array.isArray(data) ? data : (data.results || []);
            filteredItems = [...allItems];
            displayItems();
        })
        .catch(error => {
            console.error('❌ Error loading items:', error);
            itemsGrid.innerHTML = `<div class="no-results">⚠️ Error loading items: ${error.message}</div>`;
        });
}

// ========== FILTERING & SEARCH ==========
function applyFilters() {
    let filtered = [...allItems];

    // Filter by diet category
    if (currentDietFilter !== 'all') {
        filtered = filtered.filter(item => {
            const categories = item.diet_categories || [];
            return categories.includes(currentDietFilter);
        });
    }

    // Filter by item type (menu or plat)
    if (currentViewFilter !== 'all') {
        filtered = filtered.filter(item => item.type === currentViewFilter);
    }

    // Filter by search query
    if (currentSearchQuery.trim()) {
        const query = currentSearchQuery.toLowerCase();
        filtered = filtered.filter(item => 
            item.nom.toLowerCase().includes(query) || 
            item.description.toLowerCase().includes(query)
        );
    }

    filteredItems = filtered;
    displayItems();
}

function displayItems() {
    if (filteredItems.length === 0) {
        itemsGrid.innerHTML = '';
        noResults.style.display = 'block';
        return;
    }

    noResults.style.display = 'none';
    itemsGrid.innerHTML = filteredItems.map(item => createItemCard(item)).join('');

    // Add event listeners to "Add to Cart" buttons
    document.querySelectorAll('.btn-add-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const itemId = btn.dataset.itemId;
            const itemType = btn.dataset.itemType;
            const itemName = btn.dataset.itemName;
            openAddToCartModal(itemId, itemType, itemName);
        });
    });
}

function createItemCard(item) {
    // Determine item type badge
    const typeLabel = item.type === 'menu' ? 'Menu' : 'Dish';
    const typeBadgeClass = item.type === 'menu' ? 'menu' : 'plat';

    // Create diet tags
    const dietTags = (item.diet_categories || [])
        .map(category => `<span class="diet-tag ${category}">${formatDietCategory(category)}</span>`)
        .join('');

    // Format price
    const price = parseFloat(item.prix || 0).toFixed(2);

    // Get image URL or fallback
    const imageUrl = item.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500';

    return `
        <div class="item-card">
            <div class="item-image">
                <img src="${imageUrl}" alt="${item.nom}" onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'">
                <span class="item-type-badge ${typeBadgeClass}">${typeLabel}</span>
            </div>
            <div class="item-body">
                <h3>${item.nom}</h3>
                <p class="description">${item.description}</p>
                
                ${dietTags ? `<div class="diet-tags">${dietTags}</div>` : ''}
                
                <div class="nutrition-info">
                    <div class="nutrition-item">
                        <span class="label">🔥 Calories</span>
                        <span class="value">${Math.round(item.calories)}</span>
                    </div>
                    <div class="nutrition-item">
                        <span class="label">💪 Protein</span>
                        <span class="value">${item.proteines.toFixed(1)}g</span>
                    </div>
                    <div class="nutrition-item">
                        <span class="label">🍚 Carbs</span>
                        <span class="value">${item.glucides.toFixed(1)}g</span>
                    </div>
                    <div class="nutrition-item">
                        <span class="label">🌾 Fat</span>
                        <span class="value">${item.lipides.toFixed(1)}g</span>
                    </div>
                </div>

                <div class="item-footer">
                    <span class="item-price">€${price}</span>
                    <button class="btn-add-cart" 
                            data-item-id="${item.item_id}"
                            data-item-type="${item.type}"
                            data-item-name="${item.nom}">
                        <i class="fas fa-shopping-cart"></i> Add
                    </button>
                </div>
            </div>
        </div>
    `;
}

function formatDietCategory(category) {
    const categoryMap = {
        'high-protein': 'High Protein',
        'low-carb': 'Low Carb',
        'vegan': 'Vegan',
        'gluten-free': 'Gluten-Free',
        'autre': 'Other'
    };
    return categoryMap[category] || category;
}

// ========== EVENT LISTENERS SETUP ==========
function setupEventListeners() {
    // Diet filter buttons
    dietFilterButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            dietFilterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentDietFilter = btn.dataset.diet;
            applyFilters();
        });
    });

    // View filter buttons
    viewButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            viewButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentViewFilter = btn.dataset.view;
            applyFilters();
        });
    });

    // Search input
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearchQuery = e.target.value;
            applyFilters();
        });
    }

    // Modal close button
    if (closeBtn) {
        closeBtn.addEventListener('click', closeAddToCartModal);
    }

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === addToCartModal) {
            closeAddToCartModal();
        }
    });

    // Add to cart form submission
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', handleAddToCart);
    }
}

// ========== MODAL MANAGEMENT ==========
function openAddToCartModal(itemId, itemType, itemName) {
    selectedItemId = itemId;
    selectedItemType = itemType;
    
    itemInfoDisplay.textContent = itemName;
    quantityInput.value = 1;
    addToCartModal.classList.add('show');
    addToCartModal.style.display = 'block';
    
    console.log(`Opening modal for ${itemType} #${itemId}`);
}

function closeAddToCartModal() {
    addToCartModal.classList.remove('show');
    addToCartModal.style.display = 'none';
    selectedItemId = null;
    selectedItemType = null;
}

// ========== ADD TO CART ==========
async function handleAddToCart(e) {
    e.preventDefault();

    if (!selectedItemId || !selectedItemType) {
        console.error('No item selected');
        return;
    }

    const quantity = parseInt(quantityInput.value) || 1;

    try {
        console.log(`Adding to cart: ${selectedItemType} #${selectedItemId}, qty: ${quantity}`);

        // Prepare request body based on item type
        const body = {
            quantite: quantity
        };

        if (selectedItemType === 'menu') {
            body.menu_id = selectedItemId;
        } else if (selectedItemType === 'plat') {
            body.plat_id = selectedItemId;
        }

        const response = await fetch('/api/ligne-commande/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin',
            body: JSON.stringify(body)
        });

        console.log('Response status:', response.status);

        // Handle authentication errors
        if (response.status === 401 || response.status === 403) {
            const errorMsg = '❌ You must be logged in to add items to cart. Redirecting to login...';
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

        const data = await response.json();
        console.log('Response data:', data);

        // Handle item not found
        if (response.status === 404) {
            const errorMsg = `❌ ${data.error || 'Item not found'}`;
            if (typeof PanierManager !== 'undefined') {
                PanierManager.showError(errorMsg);
            } else {
                alert(errorMsg);
            }
            return;
        }

        // Handle validation errors
        if (response.status === 400) {
            const errorMsg = `❌ ${data.error || 'Validation error'}`;
            if (typeof PanierManager !== 'undefined') {
                PanierManager.showError(errorMsg);
            } else {
                alert(errorMsg);
            }
            return;
        }

        // Handle general errors
        if (!response.ok) {
            throw new Error(data.error || 'Error adding to cart');
        }

        // Success
        console.log('✅ Item added to cart:', data);
        if (typeof PanierManager !== 'undefined') {
            PanierManager.showSuccess('✓ Item added to cart!');
        } else {
            alert('✓ Item added to cart!');
        }
        closeAddToCartModal();

    } catch (error) {
        console.error('❌ Error adding to cart:', error);
        const errorMsg = `❌ ${error.message}`;
        if (typeof PanierManager !== 'undefined') {
            PanierManager.showError(errorMsg);
        } else {
            alert(errorMsg);
        }
    }
}

// ========== UTILITY FUNCTIONS ==========
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

// ========== MOBILE MENU (if needed) ==========
const mobileMenu = document.getElementById('mobileMenu');
const navLinks = document.querySelector('.nav-links');

if (mobileMenu && navLinks) {
    mobileMenu.addEventListener('click', () => {
        navLinks.classList.toggle('show');
    });
}

// Close mobile menu on nav link click
const navItems = document.querySelectorAll('.nav-links a');
navItems.forEach(item => {
    item.addEventListener('click', () => {
        if (window.innerWidth <= 768 && navLinks) {
            navLinks.classList.remove('show');
        }
    });
});
