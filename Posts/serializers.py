from rest_framework import serializers
from Authentication.models import UserProfile
from django.contrib.auth.models import User
from .models import Post, Like, Comment
from Authentication.serializers import UserPublicSerializer,PostUserDataSerializer

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    user = PostUserDataSerializer()
    likes_count = serializers.SerializerMethodField()
    # comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['user', 'text_content', 'images', 'timestamp', 'is_deepfake', 'likes_count']

    def get_likes_count(self, obj):
        return obj.likes.count()

    # def get_comments_count(self, obj):
    #     return obj.comment.count()
