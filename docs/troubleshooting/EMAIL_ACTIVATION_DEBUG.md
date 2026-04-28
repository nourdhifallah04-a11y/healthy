# 🔧 Résolution des problèmes d'email d'activation

## 📋 Vue d'ensemble
Vous n'avez pas reçu l'email d'activation après votre inscription ? Ce guide vous aide à identifier et résoudre le problème.

---

## 🔍 **Étape 1 : Vérifier la configuration DEBUG**

### Problème principal identifié
En **développement** (DEBUG=True), Django affiche les emails dans la console au lieu de les envoyer.

### Vérification
```bash
# Regardez votre terminal lors de l'inscription
# Vous devriez voir quelque chose comme :

Message received from email backend:
------- Email -------
Subject: Activez votre compte Healthy IA
From: noreply@freshgreens.com
To: user@example.com
Content-Type: text/plain; charset="utf-8"

Bonjour [Prenom],
Merci pour votre inscription.
Pour activer votre compte, cliquez sur le lien ci-dessous :
http://localhost:8000/users/activate/[uidb64]/[token]/
```

✅ **Si vous voyez cela** : C'est normal ! L'email est généré correctement. Copiez simplement le lien et ouvrez-le dans votre navigateur.

❌ **Si vous ne voyez rien** : Continuez au diagnostic suivant.

---

## 🔍 **Étape 2 : Vérifier votre environnement**

```bash
# Vérifiez votre configuration
python manage.py shell -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
"
```

### Résultats attendus en DEV
```
DEBUG: True
EMAIL_BACKEND: django.core.mail.backends.console.EmailBackend
EMAIL_HOST_USER: your-email@gmail.com
DEFAULT_FROM_EMAIL: noreply@freshgreens.com
```

---

## 🔍 **Étape 3 : Tester l'envoi d'email manuellement**

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'Ceci est un message de test',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com'],
)

# Vous devriez voir dans la console :
# Message received from email backend:
```

---

## ✅ **Solution : Pour la PRODUCTION**

Si vous souhaitez que l'email soit réellement envoyé (pas seulement affiché en console), vous devez :

### 1. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
DJANGO_DEBUG=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=votre-email@gmail.com
```

### 2. Configurer Gmail (important !)

1. **Activez la vérification 2FA** : https://myaccount.google.com/security
2. **Générez un mot de passe d'application** :
   - Allez sur : https://myaccount.google.com/apppasswords
   - Sélectionnez "Mail" et "Windows"
   - Copiez le mot de passe 16 caractères
   - Mettez-le dans `.env` sous `EMAIL_HOST_PASSWORD`

### 3. Installez python-dotenv

```bash
pip install python-dotenv
```

### 4. Chargez les variables dans settings.py

```python
# myapp/settings.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.getenv("DJANGO_DEBUG", "1").lower() in {"1", "true", "yes", "on"}
```

---

## 🚀 **Test d'inscription complet**

1. **Redémarrez le serveur** :
   ```bash
   python manage.py runserver
   ```

2. **Inscrivez-vous** :
   - Allez sur `/register/`
   - Remplissez le formulaire
   - Validez

3. **Regardez les logs** :
   - En DEV : Vous verrez l'email dans la console
   - En PROD : Vous recevrez un email réel

4. **Activez votre compte** :
   - Cliquez sur le lien dans l'email
   - Vous serez redirigé vers la page de connexion
   - Connectez-vous avec vos identifiants

---

## 📊 **Vérification de la base de données**

```bash
python manage.py shell
```

```python
from myapp.users.models import Utilisateur

# Vérifiez votre nouvel utilisateur
user = Utilisateur.objects.last()
print(f"Email: {user.email}")
print(f"Actif: {user.is_active}")
print(f"Est actif: {user.est_actif}")
```

Attendez-vous à :
```
Email: votre-email@example.com
Actif: False
Est actif: False
```

Après activation (clic sur le lien) :
```
Actif: True
Est actif: True
```

---

## ❌ **Problèmes courants**

### "BadHeaderError: Header values can't contain newlines"
- **Cause** : Des caractères spéciaux dans le nom/email
- **Solution** : Vérifiez vos données avant envoi

### "SMTPAuthenticationError"
- **Cause** : Credentials Gmail incorrects
- **Solution** : Vérifiez le mot de passe d'application (pas le mot de passe Gmail)

### "Connection refused"
- **Cause** : Serveur SMTP inaccessible
- **Solution** : Vérifiez votre connexion internet et les paramètres SMTP

---

## 📞 **Support avancé**

Activez le debug complet :

```bash
# Ajoutez dans settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

Puis redémarrez et testez l'inscription.
