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

// ========== VALIDATION EMAIL ==========
function isValidEmail(email) {
    return /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/.test(email);
}

// ========== RÉSEAUX SOCIAUX ==========
function socialLogin(provider) {
    showToast(`Connexion avec ${provider} - Fonctionnalité à venir`, 'success');
}

// ========== GESTION DES TABS ==========
const tabBtns = document.querySelectorAll('.tab-btn');
const panels = {
    login: document.getElementById('loginPanel'),
    register: document.getElementById('registerPanel')
};

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        Object.values(panels).forEach(panel => panel.classList.remove('active'));
        panels[tab].classList.add('active');
    });
});

// ========== FORMULAIRE DE CONNEXION ==========
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        
        if (!email || !password) {
            showToast('Veuillez remplir tous les champs', 'error');
            return;
        }
        
        if (!isValidEmail(email)) {
            showToast('Email invalide', 'error');
            return;
        }
        
        if (password.length < 6) {
            showToast('Mot de passe trop court (minimum 6 caractères)', 'error');
            return;
        }
        
        // Simulation de connexion
        localStorage.setItem('userEmail', email);
        localStorage.setItem('isLoggedIn', 'true');
        
        showToast(`Bienvenue ${email} ! Connexion réussie.`, 'success');
        
        setTimeout(() => {
            window.location.href = 'profil.html';
        }, 1500);
    });
}

// ========== FORMULAIRE D'INSCRIPTION ==========
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const name = document.getElementById('regName').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const password = document.getElementById('regPassword').value;
        const confirmPassword = document.getElementById('regConfirmPassword').value;
        const acceptTerms = document.getElementById('acceptTerms').checked;
        
        if (!name || !email || !password || !confirmPassword) {
            showToast('Veuillez remplir tous les champs', 'error');
            return;
        }
        
        if (name.length < 2) {
            showToast('Nom trop court (minimum 2 caractères)', 'error');
            return;
        }
        
        if (!isValidEmail(email)) {
            showToast('Email invalide', 'error');
            return;
        }
        
        if (password.length < 6) {
            showToast('Mot de passe trop court (minimum 6 caractères)', 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showToast('Les mots de passe ne correspondent pas', 'error');
            return;
        }
        
        if (!acceptTerms) {
            showToast('Veuillez accepter les conditions d\'utilisation', 'error');
            return;
        }
        
        // Sauvegarde des données
        localStorage.setItem('userName', name);
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userPassword', password);
        localStorage.setItem('isLoggedIn', 'true');
        
        showToast(`Bienvenue ${name} ! Votre compte a été créé avec succès.`, 'success');
        
        setTimeout(() => {
            window.location.href = 'profil.html';
        }, 1500);
    });
}

// ========== SUPPRESSION DES ERREURS AU TYPAGE ==========
const inputs = document.querySelectorAll('input');
inputs.forEach(input => {
    input.addEventListener('input', () => {
        input.classList.remove('error');
    });
});

// ========== CHARGEMENT ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌿 Page de connexion chargée avec succès !');
});