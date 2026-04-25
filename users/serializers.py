from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'favorite_genres']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'avatar',
            'favorite_genres', 'taste_profile', 'date_joined',
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'taste_profile']


class PublicUserSerializer(serializers.ModelSerializer):
    """Safe public profile — no email"""
    class Meta:
        model = User
        fields = ['id', 'username', 'bio', 'avatar', 'taste_profile']
