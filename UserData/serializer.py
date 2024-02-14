from django.contrib.auth.models import User
from Authentication.models import UserProfile
from django.db import models
from rest_framework import serializers


class OtherUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['fullname', 'bio', 'profile_pic', 'user']
        depth = 1