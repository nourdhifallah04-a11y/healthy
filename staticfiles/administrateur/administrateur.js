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

// ========== TOGGLE PASSWORD ==========
function togglePassword(inputId, element) {
    const input = document.getElementById(inputId);
    const icon = element.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// ========== NOTIFICATION TOAST ==========
function showToast(message, type = 'success') {
    // Supprimer les notifications existantes
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Créer la notification
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);

    // Animation d'entrée
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Disparition après 4 secondes
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// ========== IDENTIFIANTS ADMIN (simulation) ==========
const ADMIN_CREDENTIALS = {
    username: "admin",
    password: "admin123"
};

// ========== FORMULAIRE DE CONNEXION ADMIN ==========
const adminForm = document.getElementById('adminLoginForm');

if (adminForm) {
    adminForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        // Validation des champs
        if (!username || !password) {
            showToast('Veuillez remplir tous les champs', 'error');
            return;
        }
        
        if (username.length < 3) {
            showToast('Identifiant trop court (minimum 3 caractères)', 'error');
            return;
        }
        
        if (password.length < 4) {
            showToast('Mot de passe trop court (minimum 4 caractères)', 'error');
            return;
        }
        
        // Vérification des identifiants
        if (username === ADMIN_CREDENTIALS.username && password === ADMIN_CREDENTIALS.password) {
            // Connexion réussie
            localStorage.setItem('adminLoggedIn', 'true');
            localStorage.setItem('adminName', username);
            localStorage.setItem('adminLoginTime', new Date().toISOString());
            
            showToast('Connexion administrateur réussie ! Redirection...', 'success');
            
            setTimeout(() => {
                window.location.href = "/dashboard/";
            }, 1500);
        } else {
            // Échec de connexion
            showToast('Identifiant ou mot de passe incorrect', 'error');
            
            // Animation d'erreur sur les champs
            const inputs = document.querySelectorAll('.input-wrapper input');
            inputs.forEach(input => {
                input.classList.add('error');
                setTimeout(() => {
                    input.classList.remove('error');
                }, 500);
            });
        }
    });
}

// ========== MOT DE PASSE OUBLIÉ ==========
const forgotLink = document.getElementById('forgotPassword');
if (forgotLink) {
    forgotLink.addEventListener('click', (e) => {
        e.preventDefault();
        showToast('Contactez l\'administrateur principal pour réinitialiser votre mot de passe', 'success');
    });
}

// ========== SUPPRESSION DES ERREURS AU TYPAGE ==========
const inputs = document.querySelectorAll('.input-wrapper input');
inputs.forEach(input => {
    input.addEventListener('input', () => {
        input.classList.remove('error');
    });
});

// ========== VÉRIFICATION DE SESSION ADMIN ==========
function checkAdminSession() {
    const isLoggedIn = localStorage.getItem('adminLoggedIn');
    if (isLoggedIn === 'true') {
        console.log('🔐 Session administrateur active');
        // Optionnel: rediriger vers dashboard si déjà connecté
        // window.location.href = "/dashboard/";
    }
}

// ========== CHARGEMENT ==========
document.addEventListener('DOMContentLoaded', () => {
    checkAdminSession();
    console.log('🌿 Page d\'administration chargée avec succès !');
});