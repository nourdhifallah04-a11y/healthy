# 🚀 Quick Start Guide - Feature Commande

## Navigation URLs

After implementation, users can access these URLs:

```
/panier/                           # Shopping cart
/checkout/                         # Checkout page
/commande/confirmation/<id>/       # Order confirmation
/mes-commandes/                    # Order history
/commande/<id>/                    # Order details
```

---

## 🎯 User Workflow

### 1. Viewing Cart
```
User clicks "Panier" → /panier/
- See all items
- Modify quantities
- Apply promo codes
- See total
- Click "Passer la commande"
```

### 2. Checkout
```
/checkout/
- Enter delivery address
- Review order summary
- Accept terms
- Submit
```

### 3. Confirmation
```
/commande/confirmation/<id>/
- See order details
- View nutritional info
- Check next steps
- View options to reorder or continue shopping
```

### 4. Order History
```
/mes-commandes/
- See all orders
- Filter by status
- Click order for details
- Reorder if delivered
```

---

## 💾 Database Models

### Commande Fields
- `id_commande` (PK)
- `client` (FK → Client)
- `date` (DateTime)
- `statut` (CharField - choices)
- `total` (DecimalField)
- `adresse_livraison` (TextField)
- `notes` (TextField)

### LigneCommande Fields
- `id` (PK)
- `commande` (FK)
- `menu` (FK)
- `quantite` (PositiveInteger)
- `prix_unitaire` (DecimalField)

### Statuts Available
- `panier` - Panier
- `en_attente` - En attente
- `confirmee` - Confirmée
- `en_preparation` - En préparation
- `livree` - Livrée
- `annulee` - Annulée

---

## 🧪 Testing

### Run Feature Tests
```bash
python test_commande_feature.py
```

### Run Unit Tests
```bash
python manage.py test myapp.tests.CommandeTestCase -v 2
python manage.py test myapp.tests.LigneCommandeTestCase -v 2
python manage.py test myapp.tests.CommandeViewsTestCase -v 2
python manage.py test myapp.tests.CommandeIntegrationTestCase -v 2
```

### System Check
```bash
python manage.py check
# Expected: System check identified no issues (0 silenced).
```

---

## 🔧 Admin Interface

Access Django admin at `/admin/`:

1. **Commandes** - Manage all orders
   - Filter by status and date
   - View inline line items
   - Edit delivery info

2. **Lignes de Commande** - Manage order items
   - See order and menu details
   - Calculate subtotals
   - Filter by order status

---

## 📝 Key Model Methods

### Commande Methods

```python
# Validate and change status
commande.valider_commande() → bool

# Calculate total price
commande.calculer_total() → Decimal

# Get nutritional totals
commande.calculer_nutrition_totale() → Dict
# Returns: {calories, proteines, glucides, lipides}
```

### LigneCommande Properties

```python
# Calculate line subtotal
ligne.sous_total → Decimal (quantite * prix_unitaire)

# String representation
str(ligne) → "1 - Menu Délice x2"
```

---

## 🎨 Template Variables

### Panier Template
```django
{{ commande }}           # Current order
{{ commande.lignecommande_set.all }}  # Order items
{{ commande.total }}     # Order total
```

### Checkout Template
```django
{{ commande }}
{{ user }}
{{ commande.calculer_nutrition_totale }}
```

### Confirmation Template
```django
{{ commande.id_commande }}
{{ commande.statut }}
{{ commande.adresse_livraison }}
{{ commande.calculer_nutrition_totale }}
```

---

## 📊 API Endpoints (ViewSet)

Available at `/api/commandes/`:

```
GET    /api/commandes/              # List user's orders
GET    /api/commandes/{id}/         # Get order details
POST   /api/commandes/              # Create new order
PATCH  /api/commandes/{id}/         # Update order
DELETE /api/commandes/{id}/         # Delete order

# Custom Actions:
POST   /api/commandes/{id}/valider/ # Validate order
POST   /api/commandes/{id}/ajouter_menu/  # Add menu item
POST   /api/commandes/{id}/calculer_total/  # Recalculate total
```

---

## 🔐 Permissions

- **Authentication** - All views require `@login_required` or `IsAuthenticated`
- **Owner Check** - Users can only access their own orders
- **Read-only Fields** - `date`, `id`, `total` are read-only in admin

---

## 🐛 Common Issues & Solutions

### Issue: "Commande not found"
**Solution:** Ensure user is authenticated and viewing their own order

### Issue: "Quantities not updating"
**Solution:** Check browser console for JavaScript errors. Verify CSRF token is present

### Issue: "Totals showing 0"
**Solution:** Ensure CompositionMenu items are added to menu. Verify menu.plats.add()

### Issue: "Template 404 error"
**Solution:** Ensure all template files exist in `templates/commande/`

---

## 📱 CSS Classes for Customization

```css
.panier-container          /* Main cart container */
.panier-table             /* Cart items table */
.commande-card            /* Order card */
.status-badge             /* Status display */
.quantity-control         /* Quantity buttons */
.summary-box              /* Summary sidebar */
.btn-primary              /* Primary button */
.modal                    /* Modal dialog */
.empty-state              /* Empty state */
```

---

## 🔊 JavaScript Functions

```javascript
// Initialize pages
PanierManager.initPanier()
PanierManager.initCheckout()
PanierManager.initMesCommandes()

// Cart operations
PanierManager.updateCartItem(ligneId, qty)
PanierManager.removeCartItem(ligneId)

// Order operations
PanierManager.cancelOrder(orderId)
PanierManager.reorderFromOrder(orderId)

// Notifications
PanierManager.showSuccess(message)
PanierManager.showError(message)
```

---

## 📖 Documentation Files

- `FEATURE_COMMANDE.md` - Complete feature documentation
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation guide
- `QUICK_START.md` - This file

---

## ✅ Checklist for Integration

- [x] Templates created
- [x] Static files (CSS, JS) created
- [x] Views implemented
- [x] URLs configured
- [x] Forms created
- [x] Models updated
- [x] Admin interface configured
- [x] Tests written and passing
- [x] Security checks done
- [x] System checks passing
- [x] Documentation complete

---

## 🎉 Summary

The Commande feature is production-ready with:
- ✅ Full cart management
- ✅ Complete checkout flow
- ✅ Order history tracking
- ✅ Nutritional information
- ✅ Responsive design
- ✅ Comprehensive tests
- ✅ Security features
- ✅ Complete documentation

**Ready to deploy!**
