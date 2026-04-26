# Guide de Déploiement

## 🚀 Déploiement en Production

### Prérequis
- Serveur Linux (Ubuntu 20.04+)
- PostgreSQL 12+
- Redis 6+
- Nginx
- Gunicorn

### 1. Cloner et configurer
```bash
git clone <repository> /var/www/healthy-ia
cd /var/www/healthy-ia
```

### 2. Créer l'environnement
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 3. Configurer les variables
```bash
cp .env.example .env
# Éditer .env pour production
nano .env
```

Configuration essentielles pour production:
```
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=<générer-une-clé-forte>
ALLOWED_HOSTS=your-domain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=healthy_ia
DB_USER=healthyia
DB_PASSWORD=<mot-de-passe-fort>
DB_HOST=localhost
REDIS_URL=redis://localhost:6379/1
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. Migrations de base de données
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5. Configurer Gunicorn
Créer `/etc/systemd/system/gunicorn-healthyia.service`:
```ini
[Unit]
Description=gunicorn daemon for healthy-ia
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/healthy-ia
ExecStart=/var/www/healthy-ia/venv/bin/gunicorn \
          --workers 3 \
          --worker-class sync \
          --bind unix:/var/www/healthy-ia/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Démarrer le service:
```bash
systemctl start gunicorn-healthyia
systemctl enable gunicorn-healthyia
```

### 6. Configurer Nginx
Créer `/etc/nginx/sites-available/healthyia`:
```nginx
upstream gunicorn_app {
    server unix:/var/www/healthy-ia/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 20M;
    
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }
    
    location /static/ {
        alias /var/www/healthy-ia/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/healthy-ia/media/;
    }
    
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://gunicorn_app;
    }
}
```

Activer le site:
```bash
ln -s /etc/nginx/sites-available/healthyia /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 7. SSL avec Let's Encrypt
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

### 8. Monitoring
```bash
# Logs Gunicorn
tail -f /var/log/syslog | grep gunicorn

# Logs Django
tail -f /var/www/healthy-ia/logs/django.log

# Logs Nginx
tail -f /var/log/nginx/error.log
```

## 🔄 Déploiement continu (CI/CD)

### GitHub Actions
Créer `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Run tests
      run: |
        pip install -r requirements.txt
        pytest
    
    - name: Deploy to server
      run: |
        # Déploiement via SSH
        ssh user@your-domain.com 'cd /var/www/healthy-ia && git pull && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && systemctl restart gunicorn-healthyia'
```

## 📊 Maintenance

### Sauvegardes
```bash
# Sauvegarde base de données
pg_dump healthy_ia > backup_$(date +%Y%m%d).sql

# Sauvegarde fichiers
tar -czf backup_files_$(date +%Y%m%d).tar.gz /var/www/healthy-ia/media/
```

### Mises à jour
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
systemctl restart gunicorn-healthyia
```

## ⚠️ Sécurité

- [ ] Certificat SSL activé
- [ ] SECRET_KEY modifiée
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configuré
- [ ] Base de données sécurisée
- [ ] Authentification strong pour SSH
- [ ] Firewall configuré
- [ ] Sauvegarde régulière
