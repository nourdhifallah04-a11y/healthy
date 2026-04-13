// ========== GESTION DU COOKIE CSRF ==========
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

// ========== GESTION DE L'IMAGE ==========
function previsualiserImage(event) {
    const file = event.target.files[0];
    const fileNameSpan = document.getElementById('fileName');
    
    if (file) {
        // Afficher le nom du fichier
        fileNameSpan.textContent = file.name;
        
        // Afficher l'aperçu
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('imagePreview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        fileNameSpan.textContent = 'Aucun fichier sélectionné';
        const preview = document.getElementById('imagePreview');
        preview.style.display = 'none';
    }
}

// ========== SAUVEGARDE DU PLAT ==========
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
    
    // Ajouter l'image si elle est sélectionnée
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
    .then(data => {
        console.log('Données brutes reçues de l\'API:', data);
        loading.style.display = 'none';
        
        if (!data.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        document.getElementById('formAjouterPlat').reset();
        document.getElementById('imagePreview').style.display = 'none';
        document.getElementById('fileName').textContent = 'Aucun fichier sélectionné';
        
        // Rediriger vers la liste des plats après 2 secondes
        setTimeout(() => {
            console.log('Redirection vers la liste des plats...');
            window.location.href = '/list_plats/?action=added';
        }, 2000);
    })
    .catch(error => {
        loading.style.display = 'none';
        console.error('Erreur:', error);
        const errorMessage = error.detail || error.message || 'Erreur lors de l\'ajout du plat';
    });
}

// ========== TOGGLE MENU MOBILE ==========
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenu && navLinks) {
        mobileMenu.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }
    
    console.log('🌿 Page d\'ajout de plat chargée avec succès !');
});
