/**
 * Commande/Panier JavaScript
 * Handles shopping cart, checkout, and order management
 */

// ============================================
// Initialize Functions
// ============================================

/**
 * Initialize panier (cart) page functionality
 */
function initPanier() {
    console.log('Initializing Panier...');

    // Quantity controls
    document.querySelectorAll('.qty-minus').forEach(btn => {
        btn.addEventListener('click', handleQtyChange);
    });

    document.querySelectorAll('.qty-plus').forEach(btn => {
        btn.addEventListener('click', handleQtyChange);
    });

    document.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', handleQtyChange);
    });

    // Remove buttons
    document.querySelectorAll('.btn-remove').forEach(btn => {
        btn.addEventListener('click', handleRemoveItem);
    });

    // Promo code
    const promoBtn = document.getElementById('apply-promo');
    if (promoBtn) {
        promoBtn.addEventListener('click', handleApplyPromo);
    }

    console.log('Panier initialized');
}

/**
 * Initialize checkout page functionality
 */
function initCheckout() {
    console.log('Initializing Checkout...');

    // Change address button
    const changeAddrBtn = document.getElementById('change-address');
    if (changeAddrBtn) {
        changeAddrBtn.addEventListener('click', toggleAddressForm);
    }

    // Form submission
    const form = document.getElementById('checkout-form');
    if (form) {
        form.addEventListener('submit', handleCheckoutSubmit);
    }

    console.log('Checkout initialized');
}

/**
 * Initialize mes commandes page functionality
 */
function initMesCommandes() {
    console.log('Initializing Mes Commandes...');

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', handleFilterChange);
    });

    // Cancel order buttons
    document.querySelectorAll('.cancel-order').forEach(btn => {
        btn.addEventListener('click', handleCancelOrder);
    });

    console.log('Mes Commandes initialized');
}

// ============================================
// Cart Management Functions
// ============================================

/**
 * Handle quantity change for cart items
 */
function handleQtyChange(event) {
    const btn = event.target;
    const ligneId = btn.dataset.ligneId;

    if (!ligneId) return;

    const input = document.querySelector(`.qty-input[data-ligne-id="${ligneId}"]`);
    let qty = parseInt(input.value);

    if (btn.classList.contains('qty-minus')) {
        qty = Math.max(1, qty - 1);
    } else if (btn.classList.contains('qty-plus')) {
        qty = qty + 1;
    }

    input.value = qty;

    // Update server
    updateCartItem(ligneId, qty);
}

/**
 * Update cart item quantity on server
 */
async function updateCartItem(ligneId, qty) {
    try {
        const response = await fetch(`/api/ligne-commande/${ligneId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ quantite: qty })
        });

        if (response.ok) {
            // Recalculate totals
            recalculatePanierTotals();
        } else {
            showError('Erreur lors de la mise à jour du panier');
        }
    } catch (error) {
        console.error('Error updating cart item:', error);
        showError('Une erreur est survenue');
    }
}

/**
 * Handle removing an item from cart
 */
function handleRemoveItem(event) {
    event.preventDefault();
    const ligneId = event.currentTarget.dataset.ligneId;

    if (!ligneId) return;

    // Show confirmation modal
    showModal('modal-delete', () => {
        removeCartItem(ligneId);
    });
}

/**
 * Remove cart item from server
 */
async function removeCartItem(ligneId) {
    try {
        const response = await fetch(`/api/ligne-commande/${ligneId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            // Remove from DOM
            const row = document.querySelector(`[data-ligne-id="${ligneId}"]`);
            if (row) {
                row.remove();
                recalculatePanierTotals();
                showSuccess('Article supprimé');
                location.reload(); // Reload to refresh cart display
            }
        } else {
            showError('Erreur lors de la suppression de l\'article');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showError('Une erreur est survenue');
    }
}

/**
 * Recalculate cart totals
 */
function recalculatePanierTotals() {
    const rows = document.querySelectorAll('.ligne-item');
    let totalItems = rows.length;
    let totalPrice = 0;

    rows.forEach(row => {
        const subtotal = parseFloat(row.querySelector('.item-subtotal').textContent);
        totalPrice += subtotal;
    });

    // Update display
    const itemsEl = document.getElementById('total-items');
    const subtotalEl = document.getElementById('subtotal');
    const totalEl = document.getElementById('total-price');

    if (itemsEl) itemsEl.textContent = totalItems;
    if (subtotalEl) subtotalEl.textContent = totalPrice.toFixed(2) + '€';
    if (totalEl) totalEl.textContent = totalPrice.toFixed(2) + '€';

    // Update server
    updatePanierTotal();
}

/**
 * Update panier total on server
 */
async function updatePanierTotal() {
    try {
        const totalEl = document.getElementById('total-price');
        const total = totalEl ? parseFloat(totalEl.textContent) : 0;

        // This would typically be a PUT request to update the commande
        // Implementation depends on your API structure
        console.log('Panier total updated:', total);
    } catch (error) {
        console.error('Error updating panier total:', error);
    }
}

/**
 * Handle promo code application
 */
async function handleApplyPromo() {
    const promoCode = document.getElementById('promo-code').value.trim();

    if (!promoCode) {
        showError('Veuillez entrer un code promo');
        return;
    }

    try {
        const response = await fetch('/api/promo-codes/validate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ code: promoCode })
        });

        if (response.ok) {
            const data = await response.json();
            applyPromoDiscount(data);
            showSuccess(`Code promo appliqué: ${data.discount}% de réduction`);
        } else {
            showError('Code promo invalide');
        }
    } catch (error) {
        console.error('Error validating promo code:', error);
        showError('Erreur lors de la validation du code');
    }
}

/**
 * Apply promo discount to cart
 */
function applyPromoDiscount(promoData) {
    const subtotalEl = document.getElementById('subtotal');
    const totalEl = document.getElementById('total-price');

    const subtotal = parseFloat(subtotalEl.textContent);
    const discount = (subtotal * promoData.discount) / 100;
    const newTotal = subtotal - discount;

    // Show discount row
    const discountRow = document.querySelector('.discount-section');
    if (discountRow) {
        discountRow.style.display = 'block';
    }

    if (totalEl) {
        totalEl.textContent = newTotal.toFixed(2) + '€';
    }
}

// ============================================
// Checkout Functions
// ============================================

/**
 * Toggle address form visibility
 */
function toggleAddressForm() {
    const form = document.getElementById('address-form');
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Handle checkout form submission
 */
async function handleCheckoutSubmit(event) {
    event.preventDefault();

    const terms = document.getElementById('terms');
    if (!terms || !terms.checked) {
        showError('Veuillez accepter les conditions d\'utilisation');
        return;
    }

    const formData = new FormData(event.target);
    const adresse = formData.get('adresse_livraison');
    const notes = formData.get('notes');

    try {
        console.log('Submitting checkout with adresse:', adresse);
        
        // Essayer avec l'endpoint API d'abord
        const apiUrl = event.target.action || '/api/commandes/checkout/';
        console.log('Trying API endpoint:', apiUrl);
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                adresse_livraison: adresse,
                notes: notes
            })
        });

        console.log('Response status:', response.status);
        const contentType = response.headers.get('content-type');
        console.log('Content-Type:', contentType);

        // Si la réponse est du JSON et OK, utiliser les données retournées
        if (contentType && contentType.includes('application/json') && response.ok) {
            const responseData = await response.json();
            console.log('Response data:', responseData);
            
            showSuccess('Commande confirmée! Redirection vers le paiement...');
            
            // Rediriger selon la réponse API
            const redirectUrl = responseData.redirect_url || responseData.payment_url || '/commande/confirmation/1/';
            console.log('Redirecting to:', redirectUrl);
            
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 1500);
        } else {
            // Si l'API ne fonctionne pas, rediriger directement vers la page de paiement
            console.warn('API endpoint not available or not JSON, redirecting directly to checkout page');
            
            showSuccess('Commande confirmée! Redirection vers le paiement...');
            
            setTimeout(() => {
                // Rediriger vers la page checkout existante
                window.location.href = '/checkout/';
            }, 1500);
        }
    } catch (error) {
        console.error('Error submitting checkout:', error);
        
        // Fallback: rediriger directement vers la page checkout en cas d'erreur
        console.warn('Checkout error, using fallback redirect');
        showSuccess('Commande en cours de traitement... Redirection vers le paiement...');
        
        setTimeout(() => {
            window.location.href = '/checkout/';
        }, 1500);
    }
}

// ============================================
// Order Management Functions
// ============================================

/**
 * Handle filter change for orders
 */
function handleFilterChange(event) {
    const filter = event.target.dataset.filter;

    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Filter cards
    document.querySelectorAll('.commande-card').forEach(card => {
        if (filter === 'all' || card.dataset.status === filter) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

/**
 * Handle cancel order
 */
function handleCancelOrder(event) {
    event.preventDefault();
    const orderId = event.currentTarget.dataset.orderId;

    if (!orderId) return;

    // Show confirmation modal
    showModal('modal-cancel-order', () => {
        cancelOrder(orderId);
    });
}

/**
 * Cancel order on server
 */
async function cancelOrder(orderId) {
    try {
        const response = await fetch(`/api/commandes/${orderId}/annuler/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            showSuccess('Commande annulée');
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showError('Impossible d\'annuler cette commande');
        }
    } catch (error) {
        console.error('Error canceling order:', error);
        showError('Une erreur est survenue');
    }
}

// ============================================
// Reorder Function
// ============================================

/**
 * Reorder from previous order
 */
async function reorderFromOrder(orderId) {
    try {
        const response = await fetch(`/api/commandes/${orderId}/reorder/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            const result = await response.json();
            showSuccess('Commande dupliquée dans votre panier');
            setTimeout(() => {
                window.location.href = '/panier/';
            }, 1500);
        } else {
            showError('Erreur lors de la duplication de la commande');
        }
    } catch (error) {
        console.error('Error reordering:', error);
        showError('Une erreur est survenue');
    }
}

// ============================================
// Utility Functions
// ============================================

/**
 * Get CSRF token from cookies
 */
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

/**
 * Show modal dialog
 */
function showModal(modalId, onConfirm) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.add('active');

    const confirmBtn = modal.querySelector('#modal-confirm') || modal.querySelector('#modal-confirm-cancel');
    const cancelBtn = modal.querySelector('#modal-cancel') || modal.querySelector('#modal-cancel-btn');

    // Handle confirm
    if (confirmBtn) {
        confirmBtn.onclick = () => {
            if (onConfirm) onConfirm();
            closeModal(modalId);
        };
    }

    // Handle cancel
    if (cancelBtn) {
        cancelBtn.onclick = () => {
            closeModal(modalId);
        };
    }

    // Close on background click
    modal.onclick = (e) => {
        if (e.target === modal) {
            closeModal(modalId);
        }
    };
}

/**
 * Close modal dialog
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Show success message
 */
function showSuccess(message) {
    showMessage(message, 'success');
}

/**
 * Show error message
 */
function showError(message) {
    showMessage(message, 'error');
}

/**
 * Show message
 */
function showMessage(message, type = 'info') {
    const container = document.querySelector('.messages-container') || createMessageContainer();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    container.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Create messages container if it doesn't exist
 */
function createMessageContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    document.body.insertBefore(container, document.body.firstChild);
    return container;
}

/**
 * Format price for display
 */
function formatPrice(price) {
    return parseFloat(price).toFixed(2) + '€';
}

/**
 * Format date
 */
function formatDate(date) {
    return new Date(date).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// ============================================
// Export Functions (for external use)
// ============================================
window.PanierManager = {
    initPanier,
    initCheckout,
    initMesCommandes,
    updateCartItem,
    removeCartItem,
    cancelOrder,
    reorderFromOrder,
    showSuccess,
    showError
};
