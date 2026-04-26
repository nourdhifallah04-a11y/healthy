"""
Tests d'intégration
"""
import pytest

@pytest.mark.django_db
def test_user_creation(user):
    """Test de création d'utilisateur"""
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')

@pytest.mark.django_db
def test_user_registration_api(client):
    """Test de l'API d'inscription"""
    response = client.post('/api/v1/users/register/', {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123',
        'password_confirm': 'newpass123',
        'first_name': 'John',
        'last_name': 'Doe',
    })
    
    assert response.status_code == 201
