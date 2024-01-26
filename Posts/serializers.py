from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Like, Comment
from Authentication.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['fullname','profile_picture']

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class PostSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    user = UserPublicSerializer()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'user_profile', 'text_content', 'images', 'timestamp', 'is_deepfake', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_user_profile(self, obj):
        user_profile = UserProfile.objects.get(user=obj.user)
        return UserProfileSerializer(user_profile).data
