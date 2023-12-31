from rest_framework import serializers
from .models import Message
from Authentication.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['fullname', 'profile_picture']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    class Meta:
        model = Message
        fields = ['sender', 'message', 'timestamp']
