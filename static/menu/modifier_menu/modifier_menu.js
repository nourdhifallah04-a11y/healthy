// Variables globales
let menuId = null;
let platsDisponibles = [];
let platsSelectionnes = [];
let menuActuel = null;

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Récupérer l'ID du menu depuis l'URL
    const params = new URLSearchParams(window.location.search);
    menuId = params.get('id');

    if (!menuId) {
        alert('ID du menu manquant');
        window.location.href = '/menu/list-menus/';
        return;
    }

    chargerMenuEtPlats();
    
    // Event listeners
    document.getElementById('searchPlats').addEventListener('input', filtrerPlats);
});

// Charger le menu et les plats
async function chargerMenuEtPlats() {
    document.getElementById('loading').classList.add('active');
    
    try {
        // Charger le menu
        const menuResponse = await fetch(`/menu/api/menus/${menuId}/`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Content-Type': 'application/json'
            }
        });

        if (!menuResponse.ok) {
            throw new Error('Menu non trouvé');
        }

        menuActuel = await menuResponse.json();
        remplirFormulaire(menuActuel);

        // Charger les plats
        const platsResponse = await fetch('/plat/api/plats/', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Content-Type': 'application/json'
            }
        });

        if (platsResponse.ok) {
            const data = await platsResponse.json();
            platsDisponibles = data.results || data;
            // Initialiser les plats sélectionnés
            if (menuActuel.plats && Array.isArray(menuActuel.plats)) {
                console.log('menuActuel:', menuActuel);
                platsSelectionnes = menuActuel.plats.map(platFromDb => {
                    const plat = platsDisponibles.find(p => p.id === platFromDb.id_plat || p.id_plat === platFromDb.id_plat);
                    const platId = plat.id || plat.id_plat;
                    return {
                        id: platId,
                        nom: plat.nom,
                        prix: plat ? plat.prix : 0
                    }; 
                });
            }

            afficherPlats(platsDisponibles);
            afficherPlatsSelectionnes();
        }
    } catch (error) {
        console.error('Erreur:', error);
        //alert('Erreur lors du chargement des données');
       // window.location.href = '/menu/list-menus/';
    } finally {
        document.getElementById('loading').classList.remove('active');
    }
}

// Remplir le formulaire avec les données du menu
function remplirFormulaire(menu) {
    document.getElementById('nom').value = menu.nom || '';
    document.getElementById('description').value = menu.description || '';
    document.getElementById('dateDebut').value = menu.date_debut || '';
    document.getElementById('dateFin').value = menu.date_fin || '';
    document.getElementById('dietCategory').value = menu.diet_category || 'autre';
    document.getElementById('estActif').checked = menu.est_actif || false;
}

// Afficher les plats
function afficherPlats(plats) {
    const container = document.getElementById('platsContainer');
    
    if (!plats || plats.length === 0) {
        container.innerHTML = '<p class="empty-text">Aucun plat disponible</p>';
        return;
    }

    container.innerHTML = plats.map(plat => {
        const platId = plat.id || plat.id_plat;
        const estSelectionne = platsSelectionnes.some(p => p.id === platId);
        return `
            <div class="plat-item ${estSelectionne ? 'selected' : ''}" onclick="togglePlatSelection(${platId}, '${echapperHTML(plat.nom)}')">
                <input type="checkbox" class="plat-checkbox" ${estSelectionne ? 'checked' : ''} onchange="event.stopPropagation()">
                <div class="plat-name">${echapperHTML(plat.nom)}</div>
                <div class="plat-info">${plat.calorie || 0} kcal</div>
                <div class="plat-info">${parseFloat(plat.prix).toFixed(2)} DT</div>
            </div>
        `;
    }).join('');
}

// Basculer la sélection d'un plat
function togglePlatSelection(platId, platNom) {
    const index = platsSelectionnes.findIndex(p => p.id === platId);
    
    if (index > -1) {
        platsSelectionnes.splice(index, 1);
    } else {
        const plat = platsDisponibles.find(p => (p.id || p.id_plat) === platId);
        if (plat) {
            platsSelectionnes.push({
                id: platId,
                nom: plat.nom,
                prix: plat.prix
            });
        }
    }
    
    afficherPlats(platsDisponibles);
    afficherPlatsSelectionnes();
}

// Afficher les plats sélectionnés
function afficherPlatsSelectionnes() {
    const container = document.getElementById('platsSelectionnes');
    
    if (platsSelectionnes.length === 0) {
        container.innerHTML = '<p class="empty-text">Aucun plat sélectionné</p>';
        return;
    }
    console.log(platsSelectionnes);
    container.innerHTML = platsSelectionnes.map((plat, index) => `
        <div class="plat-tag"> 
            <span>${echapperHTML(plat.nom)}</span>
            <button type="button" onclick="retirerPlat(${index}); event.preventDefault();">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

// Retirer un plat de la sélection
function retirerPlat(index) {
    platsSelectionnes.splice(index, 1);
    afficherPlats(platsDisponibles);
    afficherPlatsSelectionnes();
}

// Filtrer les plats
function filtrerPlats(event) {
    const recherche = event.target.value.toLowerCase();
    const platsFiltres = platsDisponibles.filter(plat => 
        plat.nom.toLowerCase().includes(recherche) ||
        (plat.description && plat.description.toLowerCase().includes(recherche))
    );
    afficherPlats(platsFiltres);
}

// Sauvegarder le menu
async function sauvegarderMenu(event) {
    event.preventDefault();
    
    // Validation
    if (platsSelectionnes.length === 0) {
        alert('Veuillez sélectionner au moins un plat');
        return;
    }

    // Afficher le loader
    document.getElementById('loading').classList.add('active');

    try {
        const menuData = {
            nom: document.getElementById('nom').value,
            description: document.getElementById('description').value,
            date_debut: document.getElementById('dateDebut').value,
            date_fin: document.getElementById('dateFin').value,
            diet_category: document.getElementById('dietCategory').value,
            est_actif: document.getElementById('estActif').checked,
            plats: platsSelectionnes.map(p => p.id)
        };

        const response = await fetch(`/menu/api/menus/${menuId}/`, {
            method: 'PUT',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(menuData)
        });

        if (response.ok) {
            alert('Menu modifié avec succès!');
            window.location.href = '/menu/list-menus/';
        } else {
            const errors = await response.json();
            let errorMessages = 'Erreur lors de la modification du menu:\n';
            for (const [key, value] of Object.entries(errors)) {
                if (Array.isArray(value)) {
                    errorMessages += `${key}: ${value.join(', ')}\n`;
                } else {
                    errorMessages += `${key}: ${value}\n`;
                }
            }
            alert(errorMessages);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la modification du menu');
    } finally {
        document.getElementById('loading').classList.remove('active');
    }
}

// Supprimer le menu
function supprimerMenu() {
    const modal = document.getElementById('modalSuppression');
    modal.classList.add('active');
}

// Fermer le modal
function fermerModalSuppression() {
    const modal = document.getElementById('modalSuppression');
    modal.classList.remove('active');
}

// Confirmer la suppression
async function confirmerSuppression() {
    if (!menuId) return;

    document.getElementById('loading').classList.add('active');

    try {
        const response = await fetch(`/menu/api/menus/${menuId}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok || response.status === 204) {
            alert('Menu supprimé avec succès!');
            window.location.href = '/menu/list-menus/';
        } else {
            const error = await response.json();
            alert(error.error || 'Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression du menu');
    } finally {
        document.getElementById('loading').classList.remove('active');
    }
}

// Fonction pour échapper le HTML
function echapperHTML(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Fonction pour obtenir le token CSRF
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

// Fermer le modal si on clique en dehors
document.addEventListener('click', function(event) {
    const modal = document.getElementById('modalSuppression');
    if (event.target === modal) {
        fermerModalSuppression();
    }
});
