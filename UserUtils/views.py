import datetime
from django.shortcuts import render
import django.utils
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from Authentication.models import UserProfile
from UserData.models import FriendRequest, Friendship
from Authentication.serializers import UserDetailedSerializer, UserSerializer
from Posts.models import Post
from Posts.serializers import PostSerializer
from django.core.paginator import Paginator
from django.db import transaction
from Notification.models import MessageNotification, Notification
from Notification.models import FriendRequestNotification
from UserUtils.serializer import (NotificationSerializer,
    UserNotificationForFriendRequestSerializer, UserNotificationForMessageSerializer,
    UserSettingsSerializer)
from .models import UserSettings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

class Search(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic

    def get(self, request):
        try:
            keyword = request.GET.get('keyword')
            type = request.GET.get("type", "all")
            page = int(request.GET.get("page", 1))
            results_per_page = 10

            if not keyword:
                return Response({"message": "Search Failed! keyword is required", "status": 400},
                                status=status.HTTP_400_BAD_REQUEST)

            user_results = []
            post_results = []
            if type in ["all", "users"]:
                users = UserProfile.objects.filter(
                    Q(fullname__icontains=keyword) |
                    Q(user__username__icontains=keyword) | 
                    Q(bio__icontains=keyword)
                ).distinct()
                user_results += list(users)

            if type in ["all", "posts"]:
                posts = Post.objects.filter(text_content__icontains=keyword)
                post_results += list(posts)

            if not user_results and not post_results:
                return Response({"message": "No result","data":{"post_data": [],"user_data":[]}, "status": 200},
                                status=status.HTTP_200_OK)

            paginator = Paginator(user_results + post_results, results_per_page)
            paginated_results = paginator.get_page(page)

            user_serializer = []
            post_serializer = []
            for result in paginated_results:
                if isinstance(result, UserProfile):
                    user_serializer.append(UserDetailedSerializer(result).data)
                elif isinstance(result, Post):
                    post_serializer.append(PostSerializer(result, context={'request': request}).data)

            return Response({"message": "Search Successfully!", "status": 200, "data": {"user_data": user_serializer, "post_data": post_serializer}},
                            status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"message": "Search Failed! Something went wrong", "status": 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class GetNotifications(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            page = int(request.data.get("page", 1))
            results_per_page = 10
            
            # message_notifications = MessageNotification.objects.filter(receiver=user, is_read=False)
            # friend_request_notifications = FriendRequestNotification.objects.filter(to_user=user, is_read=False)
            # final = UserNotificationForFriendRequestSerializer(friend_request_notifications, many=True).data
            # final2 = UserNotificationForMessageSerializer(message_notifications, many=True).data
            notifications = Notification.objects.filter(user=user, is_read=False, is_deleted=False).order_by('-timestamp')
            notifications = NotificationSerializer(notifications, many=True).data  # Serialize the notifications here
            
            paginator = Paginator(notifications, results_per_page)
            paginated_notifications = paginator.get_page(page).object_list  # Get the objects in the page
            
            return Response({"message": "Ok", "status": 200, "data": {"notifications": paginated_notifications}},
                            status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            return Response({"message": "Get Notifications Failed! Something went wrong", "status": 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class GetRecomandedUsers(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            user_data = UserProfile.objects.get(user=user)
            page = int(request.data.get("page", 1))
            results_per_page = 10
            users = UserProfile.objects.exclude(user=user).order_by('?')
            paginator = Paginator(users, results_per_page)
            paginated_users = paginator.get_page(page)
            serializer = UserDetailedSerializer(paginated_users, many=True)
            return Response({"message": "Ok", "status": 500, "data": serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Get Recomanded Users Failed! Something went wrong", "status": 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetSomeTrendingPosts(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            user_data = UserProfile.objects.get(user=user)
            page = int(request.query_params.get("page", 1))
            results_per_page = 10

            # Filter posts from the last 7 days
            seven_days_ago = timezone.now() - timedelta(days=7)
            posts = Post.objects.filter(timestamp__gte=seven_days_ago)

            # Annotate posts with popularity score (likes + comments)
            posts = posts.annotate(
                popularity=Count('likes') + Count('comments')
            ).order_by('-popularity', '-timestamp')

            paginator = Paginator(posts, results_per_page)
            paginated_posts = paginator.get_page(page)
            serializer = PostSerializer(paginated_posts.object_list, many=True, context={'request': request})
            return Response({"message": "Ok", "status": 200, "data": serializer.data},
                            status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"message": "User profile not found", "status": 404},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)  # Log the exception for debugging purposes
            return Response({"message": "Get Some Trending Posts Failed! Something went wrong", "status": 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GetUserSettings(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            user_settings = UserSettings.objects.filter(user=user).first()
            if not user_settings:
                # If user settings not found, create default settings
                default_settings = UserSettings.objects.create(user=user)
                return Response({
                    "message": "User Settings Not Found. Default settings created.",
                    "status": 200,
                    "data": UserSettingsSerializer(default_settings).data
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "User Settings Found.",
                "status": 200,
                "data": UserSettingsSerializer(user_settings).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({
                "message": "Get User Settings Failed! Something went wrong",
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class UpdateUserSettings(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        try:
            user = request.user
            user_settings = UserSettings.objects.filter(user=user).first()
            if not user_settings:
                # If user settings not found, create default settings
                default_settings = UserSettings.objects.create(user=user)
                return Response({
                    "message": "User Settings Not Found. Default settings created.",
                    "status": 200,
                    "data": UserSettingsSerializer(default_settings).data
                }, status=status.HTTP_200_OK)
            user_settings_serializer = UserSettingsSerializer(user_settings, data=request.data, partial=True)
            if user_settings_serializer.is_valid():
                user_settings_serializer.save()
                return Response({
                    "message": "User Settings Updated Successfully.",
                    "status": 200,
                    "data": user_settings_serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "User Settings Update Failed! Invalid Data.",
                "status": 400,
                "data": user_settings_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                "message": "Update User Settings Failed! Something went wrong",
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class RestoreSettingsToDefault(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        try:
            # delete old data for user settings and create new one
            user = request.user
            user_settings = UserSettings.objects.filter(user=user).first()
            if not user_settings:
                # If user settings not found, create default settings
                default_settings = UserSettings.objects.create(user=user)
                return Response({
                    "message": "User Settings Not Found. Default settings created.",
                    "status": 200,
                    "data": UserSettingsSerializer(default_settings).data
                }, status=status.HTTP_200_OK)
            user_settings.delete()
            default_settings = UserSettings.objects.create(user=user)
            return Response({
                "message": "User Settings Restored To Default Successfully.",
                "status": 200,
                "data": UserSettingsSerializer(default_settings).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({
                "message": "Restore Settings To Default Failed! Something went wrong",
                "detail": str(e),
                "status": 500
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
