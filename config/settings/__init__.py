"""
Configuration Django par environnement
"""
import os
from pathlib import Path

# Déterminer l'environnement
ENV = os.getenv('DJANGO_ENV', 'development')

# Importer les settings selon l'environnement
if ENV == 'production':
    from .production import *
elif ENV == 'testing':
    from .testing import *
else:
    from .development import *
