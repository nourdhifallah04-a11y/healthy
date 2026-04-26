"""
Configuration Django pour les tests
"""
from .base import *

DEBUG = True
TESTING = True

# Database - Base de données en mémoire pour les tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Email backend pour tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache pour tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Password hasher pour tests (plus rapide)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Logs pour tests
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'WARNING'

# Désactiver les migrations pendant les tests
MIGRATION_MODULES = {
    'auth': None,
    'contenttypes': None,
    'default': None,
    'sessions': None,
}
