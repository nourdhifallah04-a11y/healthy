"""
Serializers pour les modèles communs
"""
from rest_framework import serializers

class TimestampedSerializer(serializers.Serializer):
    """Serializer de base avec timestamps"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
