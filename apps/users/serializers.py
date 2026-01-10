from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    class Meta:
        model = Profile
        fields = ['bio', 'avatar_url', 'website']


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id', 'username', 'email']


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested representations."""

    avatar_url = serializers.CharField(source='profile.avatar_url', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar_url']


class MeSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user (me endpoint)."""

    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id', 'username']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
