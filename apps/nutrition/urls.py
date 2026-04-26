"""
URLs pour l'app nutrition
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'nutrition'

router = DefaultRouter()
router.register(r'foods', views.FoodViewSet, basename='food')
router.register(r'profiles', views.NutritionalProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
