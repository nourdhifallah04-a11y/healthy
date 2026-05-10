// ========== VARIABLES GLOBALES ==========
let menus = [];
let menuIdEnSuppression = null;

// ========== UTILITAIRES ==========
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

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== TOAST NOTIFICATIONS ==========
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

// ========== GESTION DES MENUS ==========
function modifierMenu(id) {
    showToast('Redirection vers la modification...', 'success');
    setTimeout(() => {
        window.location.href = `/menu/modifier-menu/?id=${id}`;
    }, 500);
}

function supprimerMenu(id) {
    menuIdEnSuppression = id;
    document.getElementById('modalSuppression').classList.add('active');
}

function fermerModalSuppression() {
    document.getElementById('modalSuppression').classList.remove('active');
    menuIdEnSuppression = null;
}

function confirmerSuppression() {
    if (!menuIdEnSuppression) return;

    const csrftoken = getCookie('csrftoken');
    
    fetch(`/menu/api/menus/${menuIdEnSuppression}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
            'Authorization': `Bearer ${getAuthToken()}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // Supprimer le menu de la liste locale
        menus = menus.filter(m => (m.id_menu || m.id) !== menuIdEnSuppression);
        afficherMenus();
        fermerModalSuppression();
        showToast('✓ Menu supprimé avec succès', 'success');
    })
    .catch(error => {
        console.error('Erreur:', error);
        showToast('✗ Erreur lors de la suppression du menu', 'error');
    });
}

// ========== AFFICHER LES MENUS ==========
function afficherMenus() {
    const tbody = document.getElementById('menusList');
    
    if (menus.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="8">
                    <div class="empty-state">
                        <i class="fas fa-layer-group"></i>
                        <p>Aucun menu pour le moment</p>
                        <a href="/ajouter-menu/" class="btn-add-small">
                            <i class="fas fa-plus"></i> Créer votre premier menu
                        </a>
                    </div>
                </td>
            </tr>
        `;
    } else {
        tbody.innerHTML = menus.map(menu => {
            const menuId = menu.id_menu || menu.id;
            const dateDebut = menu.date_debut ? new Date(menu.date_debut).toLocaleDateString('fr-FR') : '-';
            const dateFin = menu.date_fin ? new Date(menu.date_fin).toLocaleDateString('fr-FR') : '-';
            const estActif = menu.est_actif !== false;
            const nbPlats = (menu.plats && Array.isArray(menu.plats)) ? menu.plats.length : 0;
            const category = getCategoryLabel(menu.diet_category);
            
            return `
                <tr>
                    <td><strong>${escapeHtml(menu.nom || '')}</strong></td>
                    <td>${escapeHtml((menu.description || '').substring(0, 50))}${(menu.description || '').length > 50 ? '...' : ''}</td>
                    <td>${dateDebut}</td>
                    <td>${dateFin}</td>
                    <td><span class="badge badge-category">${category}</span></td>
                    <td>
                        ${menu.plats && menu.plats.length > 0 
                            ? `<div class="plats-list">
                                ${menu.plats.map(plat => `
                                    -<a href="/plat/modifier-plat/?id=${plat.id || plat.id_plat}" class="plat-link">
                                        ${escapeHtml(plat.nom || 'Plat sans nom')}
                                    </a><br>
                                `).join('')}
                            </div>`
                            : '<span class="badge">Aucun plat</span>'}
                    </td>
                    <td>
                        ${estActif 
                            ? '<span class="badge badge-active"><i class="fas fa-check"></i> Actif</span>' 
                            : '<span class="badge badge-inactive"><i class="fas fa-times"></i> Inactif</span>'}
                    </td>
                    <td>
                        <div class="actions">
                            <button class="btn-edit" onclick="modifierMenu(${menuId})">
                                <i class="fas fa-edit"></i> Modifier
                            </button>
                            <button class="btn-delete" onclick="supprimerMenu(${menuId})">
                                <i class="fas fa-trash"></i> Supprimer
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }
}

function getCategoryLabel(category) {
    const labels = {
        'high-protein': 'High Protein',
        'low-carb': 'Low Carb',
        'vegan': 'Vegan',
        'gluten-free': 'Sans Gluten',
        'autre': 'Autre'
    };
    return labels[category] || category;
}

// ========== CHARGER LES MENUS ==========
function chargerMenus() {
    const csrftoken = getCookie('csrftoken');
    
    fetch('/menu/api/menus/', {
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
        menus = Array.isArray(data) ? data : (data.results || []);
        afficherMenus();
        console.log(`🌿 ${menus.length} menus chargés avec succès`);
    })
    .catch(error => {
        console.error('Erreur lors du chargement des menus:', error);
        const tbody = document.getElementById('menusList');
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="8">
                    <div class="empty-state">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erreur lors du chargement des menus</p>
                    </div>
                </td>
            </tr>
        `;
    });
}

// ========== INITIALISATION ==========
document.addEventListener('DOMContentLoaded', () => {
    chargerMenus();
    
    // Fermer le modal si on clique en dehors
    const modal = document.getElementById('modalSuppression');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                fermerModalSuppression();
            }
        });
    }
});
