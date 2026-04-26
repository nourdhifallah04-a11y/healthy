"""
Serializers pour l'app scoring
"""
from rest_framework import serializers
from .models import Score, Recommendation

class ScoreSerializer(serializers.ModelSerializer):
    percentage = serializers.ReadOnlyField()
    score_type_display = serializers.CharField(source='get_score_type_display', read_only=True)
    
    class Meta:
        model = Score
        fields = [
            'id', 'user', 'score_type', 'score_type_display', 'value', 
            'max_value', 'percentage', 'details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class RecommendationSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'user', 'title', 'description', 'priority', 'priority_display',
            'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
