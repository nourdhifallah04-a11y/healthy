import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
django.setup()

from django.test import Client as TestClient
from myapp.models import Utilisateur, Client as ClientModel, Menu

# Create test user
try:
    user = Utilisateur.objects.get(email='test@test.com')
except Utilisateur.DoesNotExist:
    user = Utilisateur.objects.create_user(email='test@test.com', password='testpass', nom='Test', prenom='User')
print(f'Using user: {user.email}')

# Create client for user if doesn't exist
client_obj, created = ClientModel.objects.get_or_create(utilisateur=user)
print(f'Client: {client_obj.id}')

# Get the menu
menu = Menu.objects.first()
print(f'Using menu: {menu.id_menu}')

# Create Django test client
client = TestClient()

# Try to POST without authentication
print('\nTesting POST without authentication...')
response = client.post('/api/ligne-commande/', 
    data=json.dumps({'menu_id': menu.id_menu, 'quantite': 1}),
    content_type='application/json'
)
print(f'Status: {response.status_code}')
try:
    print(f'Response: {response.json()}')
except:
    print(f'Response: {response.content[:200]}')

# Try with authentication
print('\nTesting POST with authentication...')
client.force_login(user)
response = client.post('/api/ligne-commande/', 
    data=json.dumps({'menu_id': menu.id_menu, 'quantite': 1}),
    content_type='application/json'
)
print(f'Status: {response.status_code}')
try:
    resp_data = response.json()
    print(f'Response: {resp_data}')
except:
    print(f'Response: {response.content[:200]}')
