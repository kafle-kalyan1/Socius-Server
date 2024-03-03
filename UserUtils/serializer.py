from rest_framework import serializers
from Authentication.models import UserProfile
from django.contrib.auth.models import User
from Notification.models import MessageNotification
from Notification.models import FriendRequestNotification
from UserUtils.models import UserSettings
 
 
class UserNotificationForFriendRequestSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='from_user.username')
    profile_picture = serializers.CharField(source='from_user.userprofile.profile_picture')
    fullname = serializers.CharField(source='from_user.userprofile.fullname')
    class Meta:
        model = FriendRequestNotification
        fields = ['user', 'profile_picture', 'fullname', 'timestamp', 'is_read']
        
        

class UserNotificationForMessageSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='sender.username')
    profile_picture = serializers.CharField(source='sender.userprofile.profile_picture')
    fullname = serializers.CharField(source='sender.userprofile.fullname')
    class Meta:
        model = MessageNotification
        fields = ['user', 'profile_picture', 'fullname', 'timestamp', 'is_read', 'message']

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = '__all__'
        