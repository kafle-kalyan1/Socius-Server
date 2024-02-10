from django.shortcuts import render
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
from Notification.models import MessageNotification
from Notification.models import FriendRequestNotification
from UserUtils.serializer import (UserNotificationForFriendRequestSerializer,
    UserNotificationForMessageSerializer)
 


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
            user_data = UserProfile.objects.get(user=user)
            page = int(request.data.get("page", 1))
            results_per_page = 10
            
            message_notifications = MessageNotification.objects.filter(receiver=user, is_read=False)
            friend_request_notifications = FriendRequestNotification.objects.filter(to_user=user, is_read=False)
            final = UserNotificationForFriendRequestSerializer(friend_request_notifications, many=True).data
            final2 = UserNotificationForMessageSerializer(message_notifications, many=True).data
            return Response({"message": "Ok", "status": 500, "data": {"message_notifications": final2, "friend_request_notifications": final}},
                            status=status.HTTP_200_OK)
             
            pass
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
            page = int(request.data.get("page", 1))
            results_per_page = 10
            posts = Post.objects.all().order_by('-timestamp')[:10]
            paginator = Paginator(posts, results_per_page)
            paginated_posts = paginator.get_page(page)
            serializer = PostSerializer(paginated_posts, many=True)
            return Response({"message": "Ok", "status": 500, "data": serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": "Get Some Trending Posts Failed! Something went wrong", "status": 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            