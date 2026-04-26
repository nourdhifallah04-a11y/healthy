"""
Admin pour l'app scoring
"""
from django.contrib import admin
from .models import Score, Recommendation

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'score_type', 'value', 'created_at']
    list_filter = ['score_type', 'created_at']
    search_fields = ['user__username']

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'priority', 'is_completed', 'created_at']
    list_filter = ['priority', 'is_completed', 'created_at']
    search_fields = ['user__username', 'title']
