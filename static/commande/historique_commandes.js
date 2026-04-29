/* ============================================
   HISTORIQUE DES COMMANDES - JAVASCRIPT
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Ajouter des interactions et animations
    initializeHistoriqueCommandes();
});

/**
 * Initialise les fonctionnalités de la page d'historique des commandes
 */
function initializeHistoriqueCommandes() {
    // Ajouter des animations aux cartes de statistiques
    animateStatisticCards();
    
    // Ajouter des animations au tableau
    animateTableRows();
    
    // Ajouter des actions au formulaire de filtrage
    setupFilterForm();
    
    // Ajouter des tooltips et infobulles
    setupTooltips();
}

/**
 * Anime les cartes de statistiques au chargement
 */
function animateStatisticCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Anime les lignes du tableau
 */
function animateTableRows() {
    const tableRows = document.querySelectorAll('.commandes-table tbody tr');
    
    tableRows.forEach((row, index) => {
        row.style.opacity = '0';
        
        setTimeout(() => {
            row.style.transition = 'opacity 0.3s ease-out';
            row.style.opacity = '1';
        }, index * 50);
    });
}

/**
 * Configure le formulaire de filtrage
 */
function setupFilterForm() {
    const filterForm = document.querySelector('.filters-form');
    const filterInputs = filterForm.querySelectorAll('input, select');
    
    filterInputs.forEach(input => {
        // Ajouter un effet visuel quand on tape
        input.addEventListener('focus', function() {
            this.closest('.filter-group').classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.closest('.filter-group').classList.remove('focused');
        });
    });
}

/**
 * Configure les tooltips et infobulles
 */
function setupTooltips() {
    // Ajouter des tooltips Bootstrap si disponible
    const tooltipElements = document.querySelectorAll('[title]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this);
        });
    });
}

/**
 * Affiche un tooltip pour un élément
 */
function showTooltip(element) {
    const tooltip = element.getAttribute('title');
    if (!tooltip) return;
    
    const tooltipEl = document.createElement('div');
    tooltipEl.className = 'custom-tooltip';
    tooltipEl.textContent = tooltip;
    
    document.body.appendChild(tooltipEl);
    
    const rect = element.getBoundingClientRect();
    tooltipEl.style.position = 'fixed';
    tooltipEl.style.top = (rect.top - 40) + 'px';
    tooltipEl.style.left = (rect.left + rect.width / 2 - tooltipEl.offsetWidth / 2) + 'px';
    
    setTimeout(() => {
        tooltipEl.remove();
    }, 3000);
}

/**
 * Gère la sélection/désélection des commandes
 */
function toggleCommandeSelection(checkbox, commandeId) {
    const row = checkbox.closest('tr');
    
    if (checkbox.checked) {
        row.classList.add('selected');
    } else {
        row.classList.remove('selected');
    }
    
    updateBulkActions();
}

/**
 * Met à jour les actions en masse (si implémentées)
 */
function updateBulkActions() {
    const selectedCheckboxes = document.querySelectorAll('.commande-checkbox:checked');
    const bulkActionsSection = document.querySelector('.bulk-actions');
    
    if (bulkActionsSection) {
        if (selectedCheckboxes.length > 0) {
            bulkActionsSection.style.display = 'block';
            bulkActionsSection.textContent = `${selectedCheckboxes.length} commande(s) sélectionnée(s)`;
        } else {
            bulkActionsSection.style.display = 'none';
        }
    }
}

/**
 * Exporte les données du tableau en CSV
 */
function exportTableToCSV(filename = 'commandes.csv') {
    const table = document.querySelector('.commandes-table');
    let csv = [];
    
    // En-têtes
    const headers = [];
    table.querySelectorAll('th').forEach(th => {
        headers.push('"' + th.textContent.trim() + '"');
    });
    csv.push(headers.join(','));
    
    // Lignes
    table.querySelectorAll('tbody tr:not(.empty-row)').forEach(row => {
        const rowData = [];
        row.querySelectorAll('td').forEach(td => {
            rowData.push('"' + td.textContent.trim() + '"');
        });
        csv.push(rowData.join(','));
    });
    
    // Créer un blob et télécharger
    const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv.join('\n'));
    const link = document.createElement('a');
    link.setAttribute('href', csvContent);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Imprime la page
 */
function printCommandes() {
    window.print();
}

/**
 * Filtre la table en temps réel
 */
function filterTable(searchTerm) {
    const tableRows = document.querySelectorAll('.commandes-table tbody tr:not(.empty-row)');
    let visibleCount = 0;
    
    tableRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Afficher le message "aucun résultat" si nécessaire
    if (visibleCount === 0) {
        const emptyRow = document.querySelector('.commandes-table tbody .empty-row');
        if (!emptyRow) {
            const tbody = document.querySelector('.commandes-table tbody');
            const newEmptyRow = document.createElement('tr');
            newEmptyRow.className = 'empty-row';
            newEmptyRow.innerHTML = '<td colspan="8"><div class="empty-state"><i class="fas fa-inbox"></i><p>Aucun résultat</p></div></td>';
            tbody.appendChild(newEmptyRow);
        }
    }
    
    return visibleCount;
}

/**
 * Réinitialise les filtres
 */
function resetFilters() {
    const form = document.querySelector('.filters-form');
    form.reset();
    form.submit();
}

/**
 * Change le statut d'une commande
 */
function changeCommandeStatus(commandeId, newStatus) {
    if (!confirm('Êtes-vous sûr de vouloir changer le statut de cette commande ?')) {
        return;
    }
    
    // Faire une requête AJAX pour mettre à jour le statut
    fetch(`/api/commandes/${commandeId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ statut: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.id_commande) {
            // Recharger la page ou mettre à jour la ligne
            location.reload();
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la mise à jour du statut');
    });
}

/**
 * Récupère le token CSRF
 */
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return token;
}

/**
 * Affiche les détails d'une commande dans une modale
 */
function showCommandeDetails(commandeId) {
    // Récupérer les détails via API
    fetch(`/api/commandes/${commandeId}/`, {
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        displayModalDetails(data);
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors du chargement des détails');
    });
}

/**
 * Affiche les détails dans une modale
 */
function displayModalDetails(commande) {
    // Créer ou mettre à jour la modale
    const modal = document.getElementById('detailsModal') || createDetailsModal();
    
    // Remplir la modale avec les données
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = generateDetailsHTML(commande);
    
    // Afficher la modale
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

/**
 * Crée une modale pour les détails
 */
function createDetailsModal() {
    const modal = document.createElement('div');
    modal.id = 'detailsModal';
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Détails de la commande</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body"></div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

/**
 * Génère le HTML pour les détails d'une commande
 */
function generateDetailsHTML(commande) {
    return `
        <p><strong>ID:</strong> #${commande.id_commande}</p>
        <p><strong>Client:</strong> ${commande.client_name}</p>
        <p><strong>Email:</strong> ${commande.client_email}</p>
        <p><strong>Date:</strong> ${new Date(commande.date).toLocaleDateString('fr-FR')}</p>
        <p><strong>Statut:</strong> <span class="badge statut-${commande.statut}">${commande.get_statut_display}</span></p>
        <p><strong>Total:</strong> ${commande.total}€</p>
    `;
}

// Exporter les fonctions pour utilisation globale
window.historique = {
    exportTableToCSV,
    printCommandes,
    filterTable,
    resetFilters,
    changeCommandeStatus,
    showCommandeDetails,
    toggleCommandeSelection
};
