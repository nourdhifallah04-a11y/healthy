// Variables globales
let platsDisponibles = [];
let platsSelectionnes = [];

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    chargerPlats();
    
    // Event listeners
    document.getElementById('searchPlats').addEventListener('input', filtrerPlats);

    document.getElementById('loading').classList.remove('active');

});

// Charger les plats disponibles
async function chargerPlats() {
    try {
        const response = await fetch('/plat/api/plats/', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            platsDisponibles = data.results || data;
            afficherPlats(platsDisponibles);
        }
    } catch (error) {
        console.error('Erreur lors du chargement des plats:', error);
        document.getElementById('platsContainer').innerHTML = '<p class="empty-text">Erreur lors du chargement des plats</p>';
    }
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
                <div class="plat-info">€${parseFloat(plat.prix).toFixed(2)}</div>
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

        const response = await fetch('/menu/api/menus/', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token'),
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(menuData)
        });

        if (response.ok) {
            const newMenu = await response.json();
            alert('Menu créé avec succès!');
            window.location.href = '/menu/list-menus/';
        } else {
            const errors = await response.json();
            let errorMessages = 'Erreur lors de la création du menu:\n';
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
        alert('Erreur lors de la création du menu');
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
