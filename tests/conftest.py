"""
Configuration pytest
"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')

def pytest_configure():
    django.setup()
