// ========== MENU MOBILE ==========
const mobileMenu = document.getElementById('mobileMenu');
const navLinks = document.querySelector('.nav-links');

if (mobileMenu && navLinks) {
    mobileMenu.addEventListener('click', () => {
        navLinks.classList.toggle('show');
    });
}

// Fermer le menu au clic sur un lien
const navItems = document.querySelectorAll('.nav-links a');
navItems.forEach(item => {
    item.addEventListener('click', () => {
        if (window.innerWidth <= 768 && navLinks) {
            navLinks.classList.remove('show');
        }
    });
});

// ========== FONCTIONS UTILITAIRES ==========
let plats = [];
let platIdEnSuppression = null;

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

function getAuthToken() {
    return localStorage.getItem('authToken') || '';
}

// ========== NOTIFICATION TOAST ==========
function showToast(message, type = 'success') {
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// ========== GESTION DES PLATS ==========
function modifierPlat(id) {
    showToast('Redirection vers la modification...', 'success');
    setTimeout(() => {
        window.location.href = `/modifier-plat/?id=${id}`;
    }, 500);
}

function supprimerPlat(id) {
    platIdEnSuppression = id;
    document.getElementById('modalSuppression').classList.add('active');
}

function fermerModalSuppression() {
    document.getElementById('modalSuppression').classList.remove('active');
    platIdEnSuppression = null;
}

function confirmerSuppression() {
    if (!platIdEnSuppression) return;

    const csrftoken = getCookie('csrftoken');
    
    fetch(`/api/plats/${platIdEnSuppression}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
            'Authorization': `Bearer ${getAuthToken()}`
        }
    })
    .then(response => {
        if (response.status === 409) {
            // Conflit : le plat est utilisé dans un menu ou une ligne de commande
            return response.json().then(data => {
                throw new Error(`CONFLICT: ${data.details || data.error}`);
            });
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
          // Supprimer le plat de la liste locale
        plats = plats.filter(p => (p.id_plat || p.id) !== platIdEnSuppression);
        afficherPlats();
        fermerModalSuppression();
        showToast('✓ Plat supprimé avec succès', 'success');
    })

    .catch(error => {
        console.error('Erreur:', error);
        
        // Gérer les différents types d'erreurs
        if (error.message.startsWith('CONFLICT:')) {
            const message = error.message.replace('CONFLICT: ', '');
            showToast(`✗ Impossible de supprimer: ${message}`, 'error');
        } else {
            showToast('✗ Erreur lors de la suppression du plat', 'error');
        }
    });
}

// ========== AFFICHER LES PLATS ==========
function afficherPlats() {
    const tbody = document.getElementById('platsList');
    
    if (plats.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="11">
                    <div class="empty-state">
                        <i class="fas fa-utensils"></i>
                        <p>Aucun plat pour le moment</p>
                        <a href="/ajouter-plat/" class="btn-add-small">
                            <i class="fas fa-plus"></i> Ajouter votre premier plat
                        </a>
                    </div>
                </td>
            </tr>
        `;
    } else {
        tbody.innerHTML = plats.map(plat => {
            const platId = plat.id_plat || plat.id;
            const isNew = plat.isNew || plat.is_new;
            const estDisponible = plat.est_disponible || plat.disponible;
            
            return `
                <tr>
                    <td><strong>${escapeHtml(plat.nom || '')}</strong></td>
                    <td>${escapeHtml((plat.description || '').substring(0, 50))}${(plat.description || '').length > 50 ? '...' : ''}</td>
                    <td>${plat.calorie || 0} kcal</td>
                    <td>${parseFloat(plat.proteine || 0).toFixed(1)}g</td>
                    <td>${parseFloat(plat.glucides || 0).toFixed(1)}g</td>
                    <td>${parseFloat(plat.lipides || 0).toFixed(1)}g</td>
                    <td>${parseFloat(plat.fibres || 0).toFixed(1)}g</td>
                    <td><strong>${parseFloat(plat.prix || 0).toFixed(2)}€</strong></td>
                    <td>
                        ${isNew 
                            ? '<span class="badge-new"><i class="fas fa-star"></i> Nouveau</span>' 
                            : '<span class="badge-not-new"><i class="far fa-star"></i> Normal</span>'}
                    </td>
                    <td>
                        ${estDisponible 
                            ? '<span class="badge-dispo"><i class="fas fa-check"></i> Dispo</span>' 
                            : '<span class="badge-indispo"><i class="fas fa-times"></i> Indispo</span>'}
                    </td>
                    <td>
                        <div class="actions">
                            <button class="btn-edit" onclick="modifierPlat(${platId})">
                                <i class="fas fa-edit"></i> Modifier
                            </button>
                            <button class="btn-delete" onclick="supprimerPlat(${platId})">
                                <i class="fas fa-trash"></i> Supprimer
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }
}

// ========== ÉCHAPPER LE HTML ==========
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== CHARGER LES PLATS ==========
function chargerPlats() {
    const csrftoken = getCookie('csrftoken');
    
    fetch('/api/plats/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'Authorization': `Bearer ${getAuthToken()}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        plats = Array.isArray(data) ? data : (data.results || []);
        afficherPlats();
        console.log(`🌿 ${plats.length} plats chargés avec succès`);
    })
    .catch(error => {
        console.error('Erreur lors du chargement des plats:', error);
        const tbody = document.getElementById('platsList');
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="11">
                    <div class="empty-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur lors du chargement des plats</p>
                    </div>
                </td>
            </tr>
        `;
    });
}

// ========== VÉRIFIER LES PARAMÈTRES D'URL POUR LES NOTIFICATIONS ==========
function verifierNotificationSucces() {
    const params = new URLSearchParams(window.location.search);
    const action = params.get('action');
    
    if (action === 'added') {
        showToast('✓ Plat ajouté avec succès !', 'success');
        // Nettoyer l'URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (action === 'modified') {
        showToast('✓ Plat modifié avec succès !', 'success');
        // Nettoyer l'URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ========== INITIALISATION ==========
document.addEventListener('DOMContentLoaded', () => {
    chargerPlats();
    verifierNotificationSucces();
    console.log('🌿 Page de gestion des plats chargée avec succès !');
});