#!/usr/bin/env python
"""
Script pour démarrer les migrations initiales
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

def main():
    """Exécuter les migrations initiales"""
    print("Creating migrations...")
    call_command('makemigrations')
    
    print("Running migrations...")
    call_command('migrate')
    
    print("Collecting static files...")
    call_command('collectstatic', '--noinput')
    
    print("✅ Initialization completed!")

if __name__ == '__main__':
    main()
