"""
Fixtures pour les tests
"""
import pytest
from django.contrib.auth import get_user_model
from apps.nutrition.models import Food, NutritionalProfile

User = get_user_model()

@pytest.fixture
def user(db):
    """Créer un utilisateur de test"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def admin_user(db):
    """Créer un administrateur de test"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

@pytest.fixture
def food(db):
    """Créer un aliment de test"""
    return Food.objects.create(
        name='Pomme',
        calories=52,
        proteins=0.3,
        carbs=13.8,
        fats=0.2,
        fiber=2.4
    )

@pytest.fixture
def nutritional_profile(db, user):
    """Créer un profil nutritionnel de test"""
    return NutritionalProfile.objects.create(
        user=user,
        age=30,
        height=170,
        weight=70,
        gender='M',
        activity_level='moderately_active',
        daily_calorie_goal=2500
    )
