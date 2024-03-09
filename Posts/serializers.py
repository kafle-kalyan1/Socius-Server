from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth.models import User
from Authentication.serializers import UserSerializer
from .models import Comment, Like, Post, Report
from Authentication.models import UserProfile
from UserData.models import FriendRequest, Friendship


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
    is_friends = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'user_profile', 'text_content', 'images', 'timestamp','is_posted_from_offline', 'deep_fake_confidence', 'likes_count','comments_count','user_has_liked','is_friends']

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
    
    def get_is_friends(self, obj):
        request = self.context.get('request')
        return Friendship.objects.filter(Q(user1=obj.user, user2=request.user, status='accepted') | Q(user1=request.user, user2=obj.user, status='accepted')).exists()

class CommentSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id','user','text','timestamp','user_profile']
    
    def get_user_profile(self, obj):
        user_profile = UserProfile.objects.get(user=obj.user)
        return UserProfileSerializer(user_profile).data
    
        
class ReportedPostsSerializer(serializers.ModelSerializer):
    reported_by = UserPublicSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    user_profile = serializers.SerializerMethodField()
    
   
    class Meta:
           model = Report
           fields = ['report_reason', 'timestamp', 'reported_by', 'post','user_profile']

    def get_user_profile(self, obj):
        user_profile = UserProfile.objects.get(user=obj.reported_by)
        return UserProfileSerializer(user_profile).data
    

class ReportSerializer(serializers.ModelSerializer):
    reported_by = UserPublicSerializer(read_only=True)
    reported_by_profile = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['report_reason', 'timestamp', 'reported_by', 'reported_by_profile']

    def get_reported_by_profile(self, obj):
        user_profile = UserProfile.objects.get(user=obj.reported_by)
        return UserProfileSerializer(user_profile).data

class PostWithReportsSerializer(serializers.ModelSerializer):
     user_profile = serializers.SerializerMethodField()
     user = UserPublicSerializer()
     likes_count = serializers.SerializerMethodField()
     comments_count = serializers.SerializerMethodField()
     user_has_liked = serializers.SerializerMethodField()
     is_friends = serializers.SerializerMethodField()
     reports = serializers.SerializerMethodField()
     
 
     class Meta:
         model = Post
         fields = ['id', 'user', 'user_profile', 'text_content', 'images', 'timestamp','is_posted_from_offline', 'deep_fake_confidence', 'likes_count','comments_count','user_has_liked','is_friends','reports']
 
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
     
     def get_is_friends(self, obj):
         request = self.context.get('request')
         return Friendship.objects.filter(Q(user1=obj.user, user2=request.user, status='accepted') | Q(user1=request.user, user2=obj.user, status='accepted')).exists()
     
     def get_reports(self, obj):
        reports = Report.objects.filter(post=obj, is_deleted=False)
        return ReportSerializer(reports, many=True, context=self.context).data