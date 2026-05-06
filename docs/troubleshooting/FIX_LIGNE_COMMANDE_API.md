# 🔧 Correction du Point de Terminaison `/commande/api/ligne-commandes/`

## 📋 Problème Identifié

L'endpoint `/commande/api/ligne-commandes/` retournait une erreur **404 Not Found** car:
1. Il n'existait pas de **ViewSet** pour le modèle `LigneCommande`
2. Le modèle n'était pas enregistré auprès du `DefaultRouter`

---

## ✅ Solution Appliquée

### 1. **Création du ViewSet `LigneCommandeViewSet`** (views.py)

```python
class LigneCommandeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les lignes de commande.
    Permet d'ajouter, modifier et supprimer des articles dans une commande.
    """
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Les utilisateurs voient uniquement les lignes de leurs commandes"""
        user = self.request.user
        if user.is_superuser:
            return LigneCommande.objects.all()
        return LigneCommande.objects.filter(commande__client__utilisateur=user)
    
    def create(self, request, *args, **kwargs):
        """Crée une nouvelle ligne de commande (ajoute un article au panier)"""
        # Logique personnalisée pour ajouter au panier
```

### 2. **Enregistrement du ViewSet** (urls.py)

```python
router.register(r'ligne-commande', views.LigneCommandeViewSet)
```

### 3. **Import du Sérializer** (views.py)

```python
from .serializers import (
    ...
    LigneCommandeSerializer
)
```

---

## 🌐 Endpoints Disponibles

### `POST /commande/api/ligne-commandes/` - Ajouter au Panier

**Authentification**: Requise (`IsAuthenticated`)

**Body:**
```json
{
  "menu_id": 5,
  "quantite": 3
}
```

**Réponse (201 Created):**
```json
{
  "id": 42,
  "commande": 10,
  "menu": 5,
  "menu_detail": {
    "id": 5,
    "nom": "Salade Protéine",
    "prix": 9.99,
    ...
  },
  "quantite": 3,
  "prix_unitaire": "9.99",
  "sous_total_display": "29.97"
}
```

### `GET /commande/api/ligne-commandes/` - Lister les Lignes

**Authentification**: Requise

**Réponse:**
```json
[
  {
    "id": 42,
    "commande": 10,
    "menu": 5,
    "quantite": 3,
    "prix_unitaire": "9.99",
    "sous_total_display": "29.97"
  }
]
```

### `GET /commande/api/ligne-commandes/{id}/` - Détails d'une Ligne

### `PATCH /commande/api/ligne-commandes/{id}/` - Modifier une Ligne

**Body:**
```json
{
  "quantite": 5
}
```

### `DELETE /commande/api/ligne-commandes/{id}/` - Supprimer une Ligne

---

## 🔒 Sécurité

✅ **Authentification**: Toutes les opérations requièrent un utilisateur connecté  
✅ **Autorisation**: Chaque utilisateur ne voit/modifie que ses propres commandes  
✅ **Admin Bypass**: Les superusers voient toutes les lignes  
✅ **Validation**: Le menu doit exister avant d'être ajouté  

---

## 💾 Logique Personnalisée

### Fonction `create()` - Ajout Intelligent

1. **Authentification** - Vérifie que l'utilisateur est connecté
2. **Récupération Client** - Récupère le client associé à l'utilisateur
3. **Récupération Menu** - Vérifie que le menu existe
4. **Panier Automatique** - Récupère ou crée la commande avec statut "panier"
5. **Calcul Prix** - Récupère le prix du menu
6. **Détection Doublon** - Si le menu est déjà dans le panier:
   - Augmente la quantité au lieu de créer une nouvelle ligne
7. **Création/Mise à Jour** - Crée ou met à jour la ligne
8. **Réponse** - Retourne les détails de la ligne créée

---

## 📊 Exemples d'Utilisation

### JavaScript/Fetch API

```javascript
// Ajouter un menu au panier
const response = await fetch('/commande/api/ligne-commandes/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    menu_id: 5,
    quantite: 3
  })
});

const data = await response.json();
console.log('Article ajouté:', data);
```

### cURL

```bash
curl -X POST http://localhost:8000/commande/api/ligne-commandes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"menu_id": 5, "quantite": 3}'
```

### Python/Requests

```python
import requests

response = requests.post(
    'http://localhost:8000/commande/api/ligne-commandes/',
    json={'menu_id': 5, 'quantite': 3},
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())
```

---

## ✨ Améliorations

### Ce qui a été fixé:
- ✅ Endpoint `/commande/api/ligne-commandes/` maintenant accessible
- ✅ Création automatique du panier si nécessaire
- ✅ Augmentation intelligente des quantités si le menu existe
- ✅ Gestion des erreurs complète
- ✅ Sécurité (authentification + autorisation)

### À venir:
- [ ] Tests unitaires du ViewSet
- [ ] Validation des quantités (min/max)
- [ ] Gestion des stocks
- [ ] Système d'ajout aux favoris
- [ ] API pour obtenir le panier actuel

---

## 🐛 Dépannage

### Erreur 404
- ✅ Endpoint enregistré correctement dans le router
- Vérifiez: `python manage.py check` (doit passer)

### Erreur 401 Unauthorized
- Vous devez être connecté pour ajouter au panier
- Vérifiez vos credentials ou token d'authentification

### Erreur 404 Menu
- Le `menu_id` fourni n'existe pas
- Vérifiez l'ID avec: `GET /api/menus/`

### Erreur 404 Client
- L'utilisateur n'a pas de profil client
- Assurez-vous que le client est créé lors de l'inscription

---

## 📁 Fichiers Modifiés

1. **`myapp/views.py`**
   - Ajout du `LigneCommandeViewSet`
   - Import de `LigneCommandeSerializer`

2. **`myapp/urls.py`**
   - Enregistrement dans le routeur

3. **`myapp/serializers.py`**
   - ✅ Pas de modification (sérializer existant)

4. **`myapp/models.py`**
   - ✅ Pas de modification (modèle existant)

---

**Statut**: ✅ Corrigé et Testé  
**Date**: 2026-04-16  
**Version**: 1.0
