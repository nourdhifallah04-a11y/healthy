"""
Admin pour l'app nutrition
"""
from django.contrib import admin
from .models import Food, NutritionalProfile

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'calories', 'proteins', 'carbs', 'fats']
    search_fields = ['name']
    list_filter = ['calories']

@admin.register(NutritionalProfile)
class NutritionalProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'weight', 'daily_calorie_goal']
    search_fields = ['user__username']
    list_filter = ['gender', 'activity_level']
