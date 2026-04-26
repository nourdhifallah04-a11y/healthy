"""
Serializers pour l'app nutrition
"""
from rest_framework import serializers
from .models import Food, NutritionalProfile

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'calories', 'proteins', 'carbs', 'fats', 'fiber',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class NutritionalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalProfile
        fields = [
            'id', 'user', 'age', 'height', 'weight', 'gender',
            'activity_level', 'daily_calorie_goal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
