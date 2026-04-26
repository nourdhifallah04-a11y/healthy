# Documentation API REST

## 📍 Base URL
```
http://localhost:8000/api/v1/
```

## 🔐 Authentification
L'API utilise l'authentification par session Django.

## 👥 Utilisateurs

### Inscription
```http
POST /users/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Réponse:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_verified": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### Profil utilisateur
```http
GET /users/profile/
Authorization: Bearer <token>
```

## 🥗 Nutrition

### Lister les aliments
```http
GET /nutrition/foods/
```

### Obtenir un aliment
```http
GET /nutrition/foods/{id}/
```

### Profil nutritionnel
```http
GET /nutrition/profiles/
Authorization: Bearer <token>
```

## 📊 Scoring

### Calculer un score
```http
POST /scoring/scores/calculate/
Content-Type: application/json
Authorization: Bearer <token>

{
  "score_type": "professional"
}
```

### Récupérer les scores
```http
GET /scoring/scores/
Authorization: Bearer <token>
```

### Recommandations
```http
GET /scoring/recommendations/
Authorization: Bearer <token>
```

## 🛒 Commandes

### Panier - Ajouter un article
```http
POST /orders/cart/
Content-Type: application/json
Authorization: Bearer <token>

{
  "food": 1,
  "quantity": 100
}
```

### Résumé du panier
```http
GET /orders/cart/summary/
Authorization: Bearer <token>
```

### Valider le panier
```http
POST /orders/cart/checkout/
Content-Type: application/json
Authorization: Bearer <token>

{
  "delivery_address": "123 Rue de la Paix, 75000 Paris"
}
```

### Lister les commandes
```http
GET /orders/orders/
Authorization: Bearer <token>
```

## ✅ Santé de l'API
```http
GET /health/
```

**Réponse:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

## 🔄 Codes de statut HTTP

| Code | Signification |
|------|-------------|
| 200 | OK |
| 201 | Créé |
| 400 | Erreur de validation |
| 401 | Non authentifié |
| 403 | Non autorisé |
| 404 | Non trouvé |
| 500 | Erreur serveur |

## 📦 Pagination
Par défaut, les résultats sont limités à 20 éléments.

```http
GET /nutrition/foods/?page=2
```

## 🔍 Filtrage et recherche
```http
GET /nutrition/foods/?search=pomme
GET /users/?ordering=-created_at
```
