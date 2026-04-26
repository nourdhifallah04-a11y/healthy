# Installation et Configuration

## 📋 Prérequis

- Python 3.10+
- pip ou pipenv
- PostgreSQL 12+ (recommandé pour production)
- Redis 6+ (optionnel, pour cache et celery)

## 🚀 Installation de développement

### 1. Cloner le repository
```bash
git clone <repository-url>
cd healthy-ia
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Pour développement
```

### 4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 5. Créer la base de données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Créer un administrateur
```bash
python manage.py createsuperuser
```

### 7. Charger les données de test (optionnel)
```bash
python manage.py loaddata fixtures/foods.json
```

### 8. Lancer le serveur de développement
```bash
python manage.py runserver
```

L'application est maintenant accessible sur `http://localhost:8000`

## 📝 Commandes utiles

### Tests
```bash
# Tous les tests
pytest

# Tests d'une app spécifique
pytest tests/apps/users/

# Avec couverture
pytest --cov=apps
```

### Linting
```bash
# Python
flake8 apps
black apps

# JavaScript
npm run lint
```

### Migrations
```bash
# Créer une migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir l'état des migrations
python manage.py showmigrations
```

### Admin
```bash
# Créer un superuser
python manage.py createsuperuser

# Accès: http://localhost:8000/admin/
```

## 🐳 Avec Docker

### Utiliser Docker Compose
```bash
docker-compose up -d
```

### Accès
- Application: `http://localhost:8000`
- Admin: `http://localhost:8000/admin/`
- Adminer (DB): `http://localhost:8080`

## ✅ Vérification de l'installation

```bash
# Test de santé de l'API
curl http://localhost:8000/api/v1/health/

# Devrait retourner:
# {"status": "healthy", "message": "API is running"}
```

## 🆘 Dépannage

### Port 8000 déjà utilisé
```bash
python manage.py runserver 8001
```

### Erreurs de base de données
```bash
# Réinitialiser la base de données
python manage.py flush
python manage.py migrate
```

### Cache Redis non disponible
Le projet fonctionne sans Redis. En développement, le cache en mémoire est utilisé.

## 📖 Documentation supplémentaire

- [API.md](API.md) - Documentation API REST
- [DEPLOYMENT.md](DEPLOYMENT.md) - Déploiement production
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guide de contribution
