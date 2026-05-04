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
let platId = null;

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

function getPlatIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// ========== PRÉVISUALISATION IMAGE ==========
function previsualiserImage(event) {
    const file = event.target.files[0];
    const fileNameSpan = document.getElementById('fileName');
    
    if (file) {
        fileNameSpan.textContent = file.name;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        fileNameSpan.textContent = 'Aucun fichier sélectionné';
        document.getElementById('imagePreview').style.display = 'none';
    }
}

// ========== AFFICHER MESSAGE ==========
function afficherMessage(message, type) {
    const messageSucces = document.getElementById('messageSucces');
    const messageErreur = document.getElementById('messageErreur');
    
    if (type === 'success') {
        messageSucces.querySelector('span').textContent = message;
        messageSucces.style.display = 'flex';
        messageErreur.style.display = 'none';
        
        setTimeout(() => {
            messageSucces.style.display = 'none';
        }, 3000);
    } else {
        messageErreur.querySelector('span').textContent = message;
        messageErreur.style.display = 'flex';
        messageSucces.style.display = 'none';
    }
}

// ========== CHARGER LE PLAT ==========
function chargerPlat() {
    platId = getPlatIdFromUrl();
    
    if (!platId) {
        afficherMessage('Erreur: ID du plat manquant', 'error');
        return;
    }

    const csrftoken = getCookie('csrftoken');

    fetch(`/plat/api/plats/${platId}/`, {
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
        remplirFormulaire(data);
    })
    .catch(error => {
        console.error('Erreur:', error);
        afficherMessage('Erreur lors du chargement du plat', 'error');
    });
}

// ========== REMPLIR LE FORMULAIRE ==========
function remplirFormulaire(plat) {
    document.getElementById('nom').value = plat.nom || '';
    document.getElementById('description').value = plat.description || '';
    document.getElementById('prix').value = plat.prix || '';
    document.getElementById('calorie').value = plat.calorie || '';
    document.getElementById('proteine').value = plat.proteine || '';
    document.getElementById('glucides').value = plat.glucides || 0;
    document.getElementById('lipides').value = plat.lipides || 0;
    document.getElementById('fibres').value = plat.fibres || 0;
    document.getElementById('estDisponible').checked = plat.est_disponible || false;
    document.getElementById('isNew').checked = plat.isNew || false;

    // Afficher l'image actuelle
    const currentImage = document.getElementById('currentImage');
    const noImageDiv = document.getElementById('noImage');
    
    if (plat.image) {
        currentImage.src = plat.image;
        currentImage.style.display = 'block';
        noImageDiv.style.display = 'none';
    } else {
        currentImage.style.display = 'none';
        noImageDiv.style.display = 'block';
    }
}

// ========== SAUVEGARDER LE PLAT ==========
function sauvegarderPlat(event) {
    event.preventDefault();
    
    const loading = document.getElementById('loading');
    loading.style.display = 'block';
    
    const formData = new FormData();
    formData.append('nom', document.getElementById('nom').value);
    formData.append('description', document.getElementById('description').value);
    formData.append('prix', parseFloat(document.getElementById('prix').value));
    formData.append('calorie', parseFloat(document.getElementById('calorie').value));
    formData.append('proteine', parseFloat(document.getElementById('proteine').value));
    formData.append('glucides', parseFloat(document.getElementById('glucides').value));
    formData.append('lipides', parseFloat(document.getElementById('lipides').value));
    formData.append('fibres', parseFloat(document.getElementById('fibres').value));
    formData.append('est_disponible', document.getElementById('estDisponible').checked);
    formData.append('isNew', document.getElementById('isNew').checked);
    
    const imageFile = document.getElementById('image').files[0];
    if (imageFile) {
        formData.append('image', imageFile);
    }

    const csrftoken = getCookie('csrftoken');

    fetch(`/plat/api/plats/${platId}/`, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrftoken,
            'Authorization': `Bearer ${getAuthToken()}`
        },
        body: formData
    })
    .then(response => {
        loading.style.display = 'none';
        
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        return response.json();
    })
    .then(data => {
        afficherMessage('✓ Plat modifié avec succès !', 'success');
        
        setTimeout(() => {
            window.location.href = '/plat/list_plats/?action=modified';
        }, 2000);
    })
    .catch(error => {
        console.error('Erreur:', error);
        loading.style.display = 'none';
        
        let messageErreur = 'Erreur lors de la modification du plat.';
        if (error.detail) {
            messageErreur = error.detail;
        } else if (error.nom) {
            messageErreur = 'Nom: ' + error.nom.join(', ');
        } else if (error.prix) {
            messageErreur = 'Prix: ' + error.prix.join(', ');
        }
        
        afficherMessage('✗ ' + messageErreur, 'error');
    });
}

// ========== SUPPRESSION ERREUR AU TYPAGE ==========
const inputs = document.querySelectorAll('input, textarea');
inputs.forEach(input => {
    input.addEventListener('input', () => {
        input.classList.remove('error');
    });
});

// ========== INITIALISATION ==========
document.addEventListener('DOMContentLoaded', () => {
    chargerPlat();
    console.log('🌿 Page de modification de plat chargée avec succès !');
    
    // Écouter le changement de fichier
    const fileInput = document.getElementById('image');
    if (fileInput) {
        fileInput.addEventListener('change', previsualiserImage);
    }
});