"""
Vues pour l'app nutrition
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Food, NutritionalProfile
from .serializers import FoodSerializer, NutritionalProfileSerializer

class FoodViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les aliments"""
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

class NutritionalProfileViewSet(viewsets.ModelViewSet):
    """ViewSet pour les profils nutritionnels"""
    queryset = NutritionalProfile.objects.all()
    serializer_class = NutritionalProfileSerializer
    permission_classes = [IsAuthenticated]
