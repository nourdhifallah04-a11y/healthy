# API Documentation

## Base URL
```
http://localhost:8000/
```

## Authentication
All API endpoints require authentication. Use session authentication or token-based auth.

## Endpoints

### Users
- `GET /users/` - List users
- `POST /users/` - Create user
- `GET /users/<id>/` - Get user details
- `PUT /users/<id>/` - Update user
- `DELETE /users/<id>/` - Delete user

### Plats (Dishes)
- `GET /plats/` - List dishes
- `POST /plats/` - Create dish
- `GET /plats/<id>/` - Get dish details
- `PUT /plats/<id>/` - Update dish
- `DELETE /plats/<id>/` - Delete dish

### Commande (Orders)
- `GET /commande/` - List orders
- `POST /commande/` - Create order
- `GET /commande/<id>/` - Get order details
- `PUT /commande/<id>/` - Update order
- `DELETE /commande/<id>/` - Cancel order

### Contact
- `POST /contact/` - Submit contact message
- `GET /contact/` - List contact submissions

### Special Diet
- `GET /specialdiet/` - List special diets
- `POST /specialdiet/` - Create special diet
- `GET /specialdiet/<id>/` - Get diet details

## Pagination

Add query parameters to list endpoints:
```
?page=1&page_size=10
```

## Response Format

Success (200):
```json
{
  "success": true,
  "data": { ... }
}
```

Error (400+):
```json
{
  "success": false,
  "error": "Error message"
}
```
