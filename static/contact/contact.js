// Initialize Bootstrap dropdowns
document.addEventListener('DOMContentLoaded', function() {
    const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElements.forEach(function(element) {
        new bootstrap.Dropdown(element);
    });
});

// ========== RÉFÉRENCES DOM ==========
const contactForm = document.getElementById('contactForm');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const subjectInput = document.getElementById('subject');
const messageInput = document.getElementById('message');

// ========== FONCTION POUR AFFICHER LES NOTIFICATIONS ==========
function showNotification(message, type = 'success') {
    // Supprimer les notifications existantes
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());

    // Créer la notification
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Animation d'entrée
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Disparition après 4 secondes
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 4000);
}

// ========== VALIDATION DE L'EMAIL ==========
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    return emailRegex.test(email);
}

// ========== VALIDATION DES CHAMPS ==========
function validateForm() {
    let isValid = true;

    // Supprimer les classes d'erreur existantes
    const errorInputs = document.querySelectorAll('.error');
    errorInputs.forEach(input => input.classList.remove('error'));

    // Validation du nom
    if (!nameInput.value.trim()) {
        nameInput.classList.add('error');
        showNotification('Veuillez entrer votre nom', 'error');
        isValid = false;
        return false;
    }

    if (nameInput.value.trim().length < 2) {
        nameInput.classList.add('error');
        showNotification('Le nom doit contenir au moins 2 caractères', 'error');
        isValid = false;
        return false;
    }

    // Validation de l'email
    if (!emailInput.value.trim()) {
        emailInput.classList.add('error');
        showNotification('Veuillez entrer votre email', 'error');
        isValid = false;
        return false;
    }

    if (!isValidEmail(emailInput.value.trim())) {
        emailInput.classList.add('error');
        showNotification('Veuillez entrer un email valide (ex: nom@domaine.com)', 'error');
        isValid = false;
        return false;
    }

    // Validation du message
    if (!messageInput.value.trim()) {
        messageInput.classList.add('error');
        showNotification('Veuillez écrire votre message', 'error');
        isValid = false;
        return false;
    }

    if (messageInput.value.trim().length < 10) {
        messageInput.classList.add('error');
        showNotification('Le message doit contenir au moins 10 caractères', 'error');
        isValid = false;
        return false;
    }

    return isValid;
}

// ========== RÉINITIALISATION DU FORMULAIRE ==========
function resetForm() {
    contactForm.reset();
    const errorInputs = document.querySelectorAll('.error');
    errorInputs.forEach(input => input.classList.remove('error'));
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function getCSRFToken() {
    return getCookie('csrftoken');
}

// ========== ENVOI DU FORMULAIRE ==========
async function handleSubmit(e) {
    e.preventDefault();

    if (!validateForm()) {
        return;
    }

    // Récupération des données
    const formData = new URLSearchParams();
    formData.append('name', nameInput.value.trim());
    formData.append('email', emailInput.value.trim());
    formData.append('subject', subjectInput.value.trim() || 'Sans sujet');
    formData.append('message', messageInput.value.trim());

    try {
        const response = await fetch(contactForm.action || window.location.pathname, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData,
            credentials: 'same-origin',
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            showNotification(result.error || 'Impossible d\'envoyer le message. Réessayez plus tard.', 'error');
            return;
        }

        showNotification(result.message || `Merci ${nameInput.value.trim()} ! Votre message a bien été envoyé.`, 'success');
        resetForm();
    } catch (error) {
        console.error('Erreur lors de l\'envoi du message :', error);
        showNotification('Une erreur est survenue. Veuillez réessayer plus tard.', 'error');
    }
}

// ========== VALIDATION EN TEMPS RÉEL ==========
function setupRealTimeValidation() {
    // Supprimer la classe d'erreur quand l'utilisateur commence à taper
    const inputs = [nameInput, emailInput, messageInput];
    
    inputs.forEach(input => {
        if (input) {
            input.addEventListener('input', () => {
                input.classList.remove('error');
            });
        }
    });

    // Validation spéciale pour l'email
    if (emailInput) {
        emailInput.addEventListener('blur', () => {
            if (emailInput.value.trim() && !isValidEmail(emailInput.value.trim())) {
                emailInput.classList.add('error');
            } else {
                emailInput.classList.remove('error');
            }
        });
    }
}

// ========== MENU MOBILE ==========
function setupMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenu && navLinks) {
        mobileMenu.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }

    // Fermer le menu mobile au clic sur un lien
    const navItems = document.querySelectorAll('.nav-links a');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            if (window.innerWidth <= 768 && navLinks) {
                navLinks.classList.remove('show');
            }
        });
    });
}

// ========== ANIMATION AU SCROLL ==========
function setupScrollAnimation() {
    const infoCards = document.querySelectorAll('.info-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    infoCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.5s ease';
        observer.observe(card);
    });
}

// ========== INITIALISATION ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌿 Page Contact Fresh & Greens chargée avec succès !');

    // Initialisation du formulaire
    if (contactForm) {
        contactForm.addEventListener('submit', handleSubmit);
    }

    // Validation en temps réel
    setupRealTimeValidation();

    // Menu mobile
    setupMobileMenu();

    // Animation au scroll
    setupScrollAnimation();
});