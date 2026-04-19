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

// ========== SAUVEGARDER PLAT ==========
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

    fetch('/api/plats/', {
        method: 'POST',
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
        afficherMessage('✓ Plat ajouté avec succès !', 'success');
        document.getElementById('formAjouterPlat').reset();
        document.getElementById('imagePreview').style.display = 'none';
        document.getElementById('fileName').textContent = 'Aucun fichier sélectionné';
        
        setTimeout(() => {
            window.location.href = '/liste_plats/';
        }, 2000);
    })
    .catch(error => {
        console.error('Erreur:', error);
        loading.style.display = 'none';
        
        let messageErreur = 'Erreur lors de l\'ajout du plat. Veuillez vérifier les données.';
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
    console.log('🌿 Page d\'ajout de plat chargée avec succès !');
    
    // Écouter le changement de fichier
    const fileInput = document.getElementById('image');
    if (fileInput) {
        fileInput.addEventListener('change', previsualiserImage);
    }
});