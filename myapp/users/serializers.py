from rest_framework import serializers
from django.contrib.auth import get_user_model
from myapp.users.models import Client

Utilisateur = get_user_model()

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'nom', 'prenom', 'telephone', 'adresse', 'date_inscription']
        read_only_fields = ['date_inscription']

class ClientSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer()
    
    class Meta:
        model = Client
        fields = ['id', 'utilisateur', 'date_naissance']
    
    def create(self, validated_data):
        utilisateur_data = validated_data.pop('utilisateur')
        utilisateur = Utilisateur.objects.create_user(**utilisateur_data)
        client = Client.objects.create(utilisateur=utilisateur, **validated_data)
        return client