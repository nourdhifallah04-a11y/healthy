import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
os.environ['DJANGO_ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
django.setup()

from django.test import Client as TestClient
from myapp.models import Utilisateur, Client as ClientModel, Menu

# Get or create test user
try:
    user = Utilisateur.objects.get(email='test@test.com')
except Utilisateur.DoesNotExist:
    user = Utilisateur.objects.create_user(email='test@test.com', password='testpass', nom='Test', prenom='User')

# Get or create client
client_obj, _ = ClientModel.objects.get_or_create(utilisateur=user)

# Get menu
menu = Menu.objects.first()

# Create test client
client = TestClient()

print("=" * 60)
print("TEST 1: Unauthenticated POST (should get 401)")
print("=" * 60)
response = client.post('/commande/api/ligne-commandes/', 
    data=json.dumps({'menu_id': menu.id_menu, 'quantite': 1}),
    content_type='application/json'
)
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')

print("\n" + "=" * 60)
print("TEST 2: Authenticated POST without menu_id (should get error)")
print("=" * 60)
client.force_login(user)
response = client.post('/commande/api/ligne-commandes/', 
    data=json.dumps({'quantite': 1}),
    content_type='application/json'
)
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')

print("\n" + "=" * 60)
print("TEST 3: Authenticated POST with menu_id=135 (should get 404)")
print("=" * 60)
response = client.post('/commande/api/ligne-commandes/', 
    data=json.dumps({'menu_id': 135, 'quantite': 1}),
    content_type='application/json'
)
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')

print("\n" + "=" * 60)
print("TEST 4: Authenticated POST with valid menu_id (should work)")
print("=" * 60)
response = client.post('/commande/api/ligne-commandes/', 
    data=json.dumps({'menu_id': menu.id_menu, 'quantite': 1}),
    content_type='application/json'
)
print(f'Status: {response.status_code}')
print(f'Response keys: {list(response.json().keys()) if response.status_code == 201 else response.json()}')
