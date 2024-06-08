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
            'is_staff',
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
        

class PostUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['fullname']

# other user data serializers to show fullname, username, is_active, is_verified, date of birth, gender, bio, and profile picture

class UserDetailedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    is_active = serializers.BooleanField(source='user.is_active')
    date_joined = serializers.DateTimeField(source='user.date_joined')
    fullname = serializers.CharField()
    date_of_birth = serializers.DateField()
    gender = serializers.CharField()
    bio = serializers.CharField()
    location = serializers.CharField()
    profile_picture = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ['username', 'is_active','date_joined', 'fullname',  'date_of_birth', 'gender', 'bio', 'profile_picture','location']