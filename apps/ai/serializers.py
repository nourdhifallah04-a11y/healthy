"""
Serializers pour l'app ai
"""
from rest_framework import serializers
from .models import SystemeIA


class SystemeIASerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemeIA
        fields = ['id', 'nom', 'version', 'est_actif', 'created_at']
        read_only_fields = ['id', 'created_at']
