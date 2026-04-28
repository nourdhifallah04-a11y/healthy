from rest_framework import serializers
from myapp.systemeIA.models import SystemeIA


class SystemeIASerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemeIA
        fields = '__all__'

