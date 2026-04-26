"""
Serializers pour l'app users
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Utilisateur, Client, Administrateur

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'bio', 'avatar', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'email', 'nom', 'prenom', 'telephone', 'adresse', 'date_inscription', 'est_actif']
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


class AdministrateurSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer()
    
    class Meta:
        model = Administrateur
        fields = ['id', 'utilisateur', 'role', 'permissions']

