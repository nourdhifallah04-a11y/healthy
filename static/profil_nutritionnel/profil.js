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

// ========== NOTIFICATION TOAST ==========
function showToast(message, type = 'success') {
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// ========== CALCUL IMC ==========
function calculateIMC(weight, height) {
    if (weight && height && height > 0) {
        const heightInMeters = height / 100;
        const imc = weight / (heightInMeters * heightInMeters);
        return Math.round(imc * 10) / 10;
    }
    return null;
}

function getIMCStatus(imc) {
    if (imc === null) return { text: "Entrez votre poids et taille", class: "" };
    if (imc < 18.5) return { text: "Insuffisance pondérale", class: "underweight" };
    if (imc >= 18.5 && imc < 25) return { text: "Poids normal", class: "normal" };
    if (imc >= 25 && imc < 30) return { text: "Surpoids", class: "overweight" };
    return { text: "Obésité", class: "obese" };
}

// ========== MISE À JOUR IMC ==========
function updateIMC() {
    const weight = parseFloat(document.getElementById('weight').value);
    const height = parseFloat(document.getElementById('height').value);
    
    const imc = calculateIMC(weight, height);
    const imcValueSpan = document.getElementById('imcValue');
    const imcStatusDiv = document.getElementById('imcStatus');
    
    if (imc !== null && !isNaN(imc)) {
        imcValueSpan.textContent = imc;
        const status = getIMCStatus(imc);
        imcStatusDiv.innerHTML = `<span style="color: ${status.class === 'normal' ? '#27ae60' : status.class === 'underweight' ? '#3498db' : status.class === 'overweight' ? '#f39c12' : '#e74c3c'}; font-weight: 600;">${status.text}</span>`;
    } else {
        imcValueSpan.textContent = '--';
        imcStatusDiv.innerHTML = '<span>Entrez votre poids et taille</span>';
    }
}

// ========== ÉCOUTEURS POUR IMC ==========
const weightInput = document.getElementById('weight');
const heightInput = document.getElementById('height');

if (weightInput && heightInput) {
    weightInput.addEventListener('input', updateIMC);
    heightInput.addEventListener('input', updateIMC);
}

// ========== SAUVEGARDE DU PROFIL ==========
const profilForm = document.getElementById('profilForm');

if (profilForm) {
    profilForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Récupération des valeurs
        const age = document.getElementById('age').value;
        const weight = document.getElementById('weight').value;
        const height = document.getElementById('height').value;
        const gender = document.getElementById('gender').value;
        const goal = document.getElementById('goal').value;
        const activity = document.getElementById('activity').value;
        
        // Validation
        if (!age || !weight || !height || !gender || !goal || !activity) {
            showToast('Veuillez remplir tous les champs obligatoires', 'error');
            return;
        }
        
        if (age < 10 || age > 120) {
            showToast('Âge invalide (10-120 ans)', 'error');
            return;
        }
        
        if (weight < 20 || weight > 300) {
            showToast('Poids invalide (20-300 kg)', 'error');
            return;
        }
        
        if (height < 100 || height > 250) {
            showToast('Taille invalide (100-250 cm)', 'error');
            return;
        }
        
        // Récupération des allergies et restrictions
        let allergies = [];
        let restrictions = [];
        
        // Récupération des consentements
        const donneesSanteSensibles = document.getElementById('sante-sensibles').checked;
        const learningCollectif = document.getElementById('learning-collectif').checked;
        
        // Trouver les sections par leur titre
        const sections = document.querySelectorAll('.form-section');
        sections.forEach(section => {
            const h3 = section.querySelector('h3');
            if (!h3) return;
            
            const title = h3.textContent.trim();
            const checkboxes = section.querySelectorAll('.checkbox-grid input[type="checkbox"]:checked');
            
            if (title.includes('Allergies')) {
                checkboxes.forEach(checkbox => {
                    allergies.push(checkbox.value);
                });
            } else if (title.includes('Restrictions alimentaires')) {
                checkboxes.forEach(checkbox => {
                    restrictions.push(checkbox.value);
                });
            }
        });
        
        // Mapper les valeurs du formulaire aux champs du modèle Django
        const profilData = {
            age: parseInt(age),
            poids: parseFloat(weight),
            taille: parseFloat(height),
            sexe: gender,
            objectif: mapGoal(goal),  // Mapper les valeurs
            niveau_activite: mapActivity(activity),  // Mapper les valeurs
            allergies: allergies.join(', '),  // Joindre avec des virgules
            restrictions_alimentaires: restrictions.join(', '),  // Joindre avec des virgules
            donnees_sante_sensibles: donneesSanteSensibles,  // Ajouter le consentement
            learning_collectif: learningCollectif  // Ajouter le consentement
        };
        
        // Envoyer les données à Django
        sendProfilToServer(profilData);
    });
}

// ========== FONCTION POUR MAPPER LES OBJECTIFS ==========
function mapGoal(goal) {
    const goalMap = {
        'perte': 'perte_poids',
        'maintien': 'maintien',
        'muscle': 'prise_muscle',
        'bien-etre': 'performance'
    };
    return goalMap[goal] || goal;
}

// ========== FONCTION POUR MAPPER LES NIVEAUX D'ACTIVITÉ ==========
function mapActivity(activity) {
    const activityMap = {
        'sedentaire': 'sedentaire',
        'leger': 'leger',
        'modere': 'modere',
        'actif': 'actif',
        'tres-actif': 'extremement_actif'
    };
    return activityMap[activity] || activity;
}

// ========== FONCTION POUR ENVOYER LES DONNÉES AU SERVEUR ==========
async function sendProfilToServer(profilData) {
    try {
        // Récupérer le CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         getCookie('csrftoken');
        
        const response = await fetch('/api/profil-nutritionnel/creer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify(profilData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('✅ Votre profil nutritionnel a été enregistré avec succès !', 'success');
            // Optionnel : redirection ou réinitialisation
            setTimeout(() => {
                // window.location.href = '/';
            }, 1500);
        } else {
            showToast(`❌ Erreur: ${data.error || 'Une erreur est survenue'}`, 'error');
            console.error('Erreur serveur:', data);
        }
    } catch (error) {
        showToast(`❌ Erreur de connexion: ${error.message}`, 'error');
        console.error('Erreur:', error);
    }
}

// ========== FONCTION POUR RÉCUPÉRER LE COOKIE CSRF ==========
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

// ========== RÉINITIALISATION DU FORMULAIRE ==========
const resetBtn = document.getElementById('resetBtn');
if (resetBtn) {
    resetBtn.addEventListener('click', () => {
        if (confirm('Êtes-vous sûr ? Cette action supprimera votre profil nutritionnel de la base de données.')) {
            deleteProfileFromServer();
        }
    });
}

// ========== FONCTION POUR SUPPRIMER LE PROFIL ==========
async function deleteProfileFromServer() {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         getCookie('csrftoken');
        
        const response = await fetch('/api/profil-nutritionnel/supprimer/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('✅ Profil nutritionnel supprimé avec succès', 'success');
            // Réinitialiser le formulaire après suppression
            setTimeout(() => {
                profilForm.reset();
                updateIMC();
            }, 500);
        } else {
            showToast(`❌ Erreur: ${data.error || data.message || 'Une erreur est survenue'}`, 'error');
            console.error('Erreur serveur:', data);
        }
    } catch (error) {
        showToast(`❌ Erreur de connexion: ${error.message}`, 'error');
        console.error('Erreur:', error);
    }
}

// ========== CHARGEMENT DES DONNÉES SAUVEGARDÉES ==========
function loadSavedProfile() {
    const savedProfile = localStorage.getItem('nutritionProfile');
    if (savedProfile) {
        try {
            const profile = JSON.parse(savedProfile);
            
            document.getElementById('age').value = profile.age || '';
            document.getElementById('weight').value = profile.weight || '';
            document.getElementById('height').value = profile.height || '';
            document.getElementById('gender').value = profile.gender || '';
            document.getElementById('goal').value = profile.goal || '';
            document.getElementById('activity').value = profile.activity || '';
            
            // Restaurer les allergies
            if (profile.allergies) {
                document.querySelectorAll('.checkbox-grid input[type="checkbox"]').forEach(checkbox => {
                    if (profile.allergies.includes(checkbox.value)) {
                        checkbox.checked = true;
                    }
                });
            }
            
            updateIMC();
            showToast('Profil chargé avec succès', 'success');
        } catch (e) {
            console.log('Erreur de chargement');
        }
    }
}

// ========== CHARGER LE PROFIL DEPUIS LE SERVEUR ==========
async function loadProfileFromServer() {
    try {
        const response = await fetch('/api/profil-nutritionnel/obtenir/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            fillFormWithProfileData(data);
            showToast('✅ Votre profil nutritionnel a été chargé', 'success');
        } else if (response.status === 404) {
            console.log('Aucun profil trouvé - formulaire vierge');
        }
    } catch (error) {
        console.error('Erreur lors du chargement du profil:', error);
    }
}

// ========== REMPLIR LE FORMULAIRE AVEC LES DONNÉES DU PROFIL ==========
function fillFormWithProfileData(profile) {
    // Remplir les champs de base
    if (profile.age) document.getElementById('age').value = profile.age;
    if (profile.poids) document.getElementById('weight').value = profile.poids;
    if (profile.taille) document.getElementById('height').value = profile.taille;
    if (profile.sexe) document.getElementById('gender').value = profile.sexe;
    
    // Mapper les objectifs
    const goalMap = {
        'perte_poids': 'perte',
        'maintien': 'maintien',
        'prise_muscle': 'muscle',
        'performance': 'bien-etre'
    };
    if (profile.objectif) document.getElementById('goal').value = goalMap[profile.objectif] || profile.objectif;
    
    // Remplir le niveau d'activité
    if (profile.niveau_activite) document.getElementById('activity').value = profile.niveau_activite;
    
    // Cocher les allergies
    if (profile.allergies) {
        const allergiesArray = profile.allergies.split(',').map(a => a.trim());
        document.querySelectorAll('h3').forEach(h3 => {
            if (h3.textContent.includes('Allergies')) {
                const section = h3.closest('.form-section');
                const checkboxes = section.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = allergiesArray.includes(checkbox.value);
                });
            }
        });
    }
    
    // Cocher les restrictions alimentaires
    if (profile.restrictions_alimentaires) {
        const restrictionsArray = profile.restrictions_alimentaires.split(',').map(r => r.trim());
        document.querySelectorAll('h3').forEach(h3 => {
            if (h3.textContent.includes('Restrictions alimentaires')) {
                const section = h3.closest('.form-section');
                const checkboxes = section.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = restrictionsArray.includes(checkbox.value);
                });
            }
        });
    }
    
    // Charger les consentements
    if (profile.donnees_sante_sensibles !== undefined) {
        document.getElementById('sante-sensibles').checked = profile.donnees_sante_sensibles;
    }
    if (profile.learning_collectif !== undefined) {
        document.getElementById('learning-collectif').checked = profile.learning_collectif;
    }
    
    // Mettre à jour l'IMC
    updateIMC();
}

// ========== SUPPRESSION DES ERREURS AU TYPAGE ==========
const inputs = document.querySelectorAll('.input-wrapper input, .input-wrapper select');
inputs.forEach(input => {
    input.addEventListener('input', () => {
        input.classList.remove('error');
    });
});

// ========== CHARGEMENT ==========
document.addEventListener('DOMContentLoaded', () => {
    loadProfileFromServer();  // Charger depuis le serveur Django
    console.log('🌿 Page Profil Nutritionnel chargée avec succès !');
});