from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'last_login',
            'is_active',
            'date_joined',
            'first_name',
            'last_name',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'fullname', 'profile_picture', 'isVerified',
                  'date_of_birth', 'gender', 'bio', 'phone_number', 'secondary_email']
