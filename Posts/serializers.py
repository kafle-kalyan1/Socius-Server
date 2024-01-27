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
    comments_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'user_profile', 'text_content', 'images', 'timestamp', 'is_deepfake', 'likes_count','comments_count','user_has_liked']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_user_profile(self, obj):
        user_profile = UserProfile.objects.get(user=obj.user)
        return UserProfileSerializer(user_profile).data
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_deleted=False).count() 
       
    def get_user_has_liked(self, obj):  
        request = self.context.get('request')
        if request is None:
            return False
        if not request.user.is_authenticated:
            return False
        return obj.likes.filter(liked_by=request.user.id).exists()

class CommentSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id','user','text','timestamp','user_profile']
    
    def get_user_profile(self, obj):
        user_profile = UserProfile.objects.get(user=obj.user)
        return UserProfileSerializer(user_profile).data
        