/* ============================================
   ADMIN COMMANDE DETAIL - JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminDetail();
});

/**
 * Initialise les fonctionnalités de la page
 */
function initializeAdminDetail() {
    // Ajouter des animations
    animateCards();
    
    // Configurer les événements
    setupEventListeners();
}

/**
 * Anime les cartes au chargement
 */
function animateCards() {
    const cards = document.querySelectorAll('.admin-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Configure les écouteurs d'événements
 */
function setupEventListeners() {
    // Validation du formulaire de statut
    const statusForm = document.querySelector('.status-form');
    if (statusForm) {
        statusForm.addEventListener('submit', function(e) {
            const select = this.querySelector('[name="statut"]');
            if (!select.value) {
                e.preventDefault();
                alert('Veuillez sélectionner un statut');
            }
        });
    }
}

/**
 * Exporte les données de la commande en JSON
 */
function exportToJSON() {
    const commandeId = document.querySelector('h1').textContent.match(/#(\d+)/)[1];
    const commande = {
        id: commandeId,
        date: new Date().toISOString(),
        articles: [],
        total: parseFloat(document.querySelector('.summary-row.total .value').textContent),
    };

    // Récupérer les articles
    document.querySelectorAll('.item-detail-card').forEach(card => {
        const title = card.querySelector('.item-title').textContent.trim();
        const price = card.querySelector('.price-value').textContent;
        const qty = card.querySelector('.qty-value').textContent;
        
        commande.articles.push({
            name: title,
            price: parseFloat(price),
            quantity: parseInt(qty),
        });
    });

    // Créer et télécharger le fichier
    const dataStr = JSON.stringify(commande, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `commande-${commandeId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Duplique la commande
 */
function duplicateCommande() {
    if (confirm('Êtes-vous sûr de vouloir dupliquer cette commande ?')) {
        // À implémenter: appel API pour dupliquer
        alert('Fonctionnalité à implémenter');
    }
}

/**
 * Édite la commande
 */
function editCommande() {
    // À implémenter: redirection vers page d'édition
    alert('Fonctionnalité à implémenter');
}

/**
 * Annule la commande
 */
function cancelCommande() {
    if (confirm('Êtes-vous sûr de vouloir annuler cette commande ? Cette action est irréversible.')) {
        // Sélectionner le statut "annulee"
        const select = document.querySelector('[name="statut"]');
        select.value = 'annulee';
        
        // Soumettre le formulaire
        const form = document.querySelector('.status-form');
        form.submit();
    }
}

/**
 * Envoie un email au client
 */
function sendEmail() {
    const email = document.querySelector('.info-value a[href^="mailto:"]');
    if (email) {
        const emailAddr = email.textContent;
        const subject = `Suivi de votre commande #${getCommandeId()}`;
        
        // Créer un modal pour composer l'email
        showEmailModal(emailAddr, subject);
    }
}

/**
 * Affiche un modal pour composer un email
 */
function showEmailModal(emailAddr, subject) {
    const modal = document.createElement('div');
    modal.className = 'email-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Envoyer un email</h2>
                <button class="close-btn" onclick="this.closest('.email-modal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>À:</label>
                    <input type="email" value="${emailAddr}" disabled>
                </div>
                <div class="form-group">
                    <label>Sujet:</label>
                    <input type="text" value="${subject}">
                </div>
                <div class="form-group">
                    <label>Message:</label>
                    <textarea rows="6" placeholder="Votre message..."></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-primary" onclick="sendEmailConfirm(this)">Envoyer</button>
                <button class="btn-secondary" onclick="this.closest('.email-modal').remove()">Annuler</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

/**
 * Confirme l'envoi de l'email
 */
function sendEmailConfirm(btn) {
    btn.disabled = true;
    btn.textContent = 'Envoi en cours...';
    
    // À implémenter: appel API
    setTimeout(() => {
        alert('Email envoyé avec succès');
        document.querySelector('.email-modal').remove();
    }, 1000);
}

/**
 * Récupère l'ID de la commande
 */
function getCommandeId() {
    return document.querySelector('h1').textContent.match(/#(\d+)/)[1];
}

/**
 * Copie du texte dans le presse-papiers
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copié !');
    }).catch(() => {
        alert('Erreur lors de la copie');
    });
}

/**
 * Filtre les articles par type
 */
function filterByType(type) {
    const items = document.querySelectorAll('.item-detail-card');
    items.forEach(item => {
        const itemType = item.querySelector('.type-badge').textContent.toLowerCase();
        if (type === 'all' || itemType === type.toLowerCase()) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Recherche dans les articles
 */
function searchItems(query) {
    const items = document.querySelectorAll('.item-detail-card');
    const q = query.toLowerCase();
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(q) ? '' : 'none';
    });
}

/**
 * Recalcule les totaux
 */
function recalculateTotals() {
    let total = 0;
    
    document.querySelectorAll('.total-value').forEach(el => {
        const match = el.textContent.match(/[\d.]+/);
        if (match) {
            total += parseFloat(match[0]);
        }
    });
    
    // Mettre à jour le total principal
    const totalElement = document.querySelector('.summary-row.total .value');
    if (totalElement) {
        totalElement.textContent = total.toFixed(2) + '€';
    }
}

/**
 * Formate les nombres en devise
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(value);
}

/**
 * Affiche une notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation' : 'info'}-circle"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

/**
 * Génère un reçu en PDF (à implémenter avec une librairie)
 */
function generatePDF() {
    alert('Génération PDF à implémenter');
    // À implémenter avec jsPDF ou similar
}

/**
 * Export en CSV
 */
function exportToCSV() {
    let csv = 'Article,Quantité,Prix unitaire,Sous-total\n';
    
    document.querySelectorAll('.item-detail-card').forEach(card => {
        const name = card.querySelector('.item-title').textContent.replace(/[^a-zA-Z0-9\s]/g, '').trim();
        const qty = card.querySelector('.qty-value').textContent;
        const price = card.querySelector('.price-value').textContent;
        const total = card.querySelector('.total-value').textContent;
        
        csv += `"${name}",${qty},${price},${total}\n`;
    });
    
    // Ajouter le total
    const mainTotal = document.querySelector('.summary-row.total .value').textContent;
    csv += `\nTOTAL COMMANDE,,,${mainTotal}`;
    
    // Télécharger
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `commande-${getCommandeId()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Styles pour le modal email (ajouter en CSS si besoin)
 */
const emailModalStyles = `
<style>
.email-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.email-modal .modal-content {
    background: white;
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.email-modal .modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.email-modal .modal-header h2 {
    margin: 0;
}

.email-modal .close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #999;
}

.email-modal .modal-body {
    padding: 1.5rem;
}

.email-modal .form-group {
    margin-bottom: 1rem;
}

.email-modal .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
}

.email-modal .form-group input,
.email-modal .form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-family: inherit;
}

.email-modal .modal-footer {
    padding: 1.5rem;
    border-top: 1px solid #eee;
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
}

.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 1rem;
    z-index: 999;
}

.notification-success {
    color: #28a745;
}

.notification-error {
    color: #dc3545;
}

.notification-info {
    color: #17a2b8;
}

@keyframes fadeOut {
    to {
        opacity: 0;
        transform: translateY(-10px);
    }
}
</style>
`;

// Injecter les styles
document.head.insertAdjacentHTML('beforeend', emailModalStyles);
