from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from Authentication.models import UserProfile
from Posts.models import Post
from .models import FriendRequest, Friendship
import base64
from Notification.models import FriendRequestNotification
from django.db.models import Q
from django.contrib.auth.models import User
from Authentication.serializers import UserPublicSerializer, UserSerializer,UserDetailedSerializer
from django.db import transaction
from Posts.serializers import PostSerializer, CommentSerializer
from Posts.models import Comment, Post

class RecommendedFriends(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def get(self, request):
        try:
            user_profile = get_object_or_404(UserProfile, user=request.user)
            all_users = UserProfile.objects.filter(user__is_superuser=False, user__is_staff=False, user__is_active=True).exclude(user=request.user)
            accepted_friendships = Friendship.objects.filter(
                Q(user1=user_profile.user, status='accepted') | Q(user2=user_profile.user, status='accepted')
            )
            received_requests = FriendRequest.objects.filter(receiver=user_profile.user, status='pending')
            sent_requests = FriendRequest.objects.filter(sender=user_profile.user, status='pending')
            friends_set = set()
            received_set = {request.sender for request in received_requests}
            sent_set = {request.receiver for request in sent_requests}

            for friendship in accepted_friendships:
                friends_set.add(friendship.user1)
                friends_set.add(friendship.user2)

            friends_set.discard(user_profile.user)

            recommended_friends_list = []
            for user_profile in all_users:
                is_friend = user_profile.user in friends_set
                is_requested = user_profile.user in received_set or user_profile.user in sent_set
                is_requested_by_me = user_profile.user in sent_set

                recommended_friends_list.append({
                    'username': user_profile.user.username,
                    'profile_pic': user_profile.profile_picture,
                    'fullname': user_profile.fullname,
                    'is_friend': is_friend,
                    'is_requested': is_requested,
                    'is_requested_by_me': is_requested_by_me,
                })

            return Response({'status': 200, 'data': recommended_friends_list}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server", 'status': 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetOtherProfile(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic

    def get(self, request, username):
        try:
            user_data = User.objects.filter(username=username).first()
            print(user_data)
            if user_data:
                profile = User.objects.get(username=user_data)
                user_profile = UserProfile.objects.get(user=profile)
                user_serializer = UserDetailedSerializer(user_profile)
                user_posts = Post.objects.filter(user=profile, is_deleted=False).order_by('-timestamp')
                posts = PostSerializer(user_posts, many=True,context={'request': request})
                
                # check if both user are friends or not 
                user_profile = UserProfile.objects.get(user=request.user)
                friend_profile = UserProfile.objects.get(user=profile)
                is_friend = False
                is_requested = False
                is_requested_by_me = False
                friendship = Friendship.objects.filter(Q(user1=user_profile.user, user2=friend_profile.user) | Q(user1=friend_profile.user, user2=user_profile.user), status='accepted')
                if friendship:
                    is_friend = True
                else:
                    friend_request = FriendRequest.objects.filter(Q(sender=user_profile.user, receiver=friend_profile.user, status='pending') | Q(sender=friend_profile.user, receiver=user_profile.user, status='pending'))
                    if friend_request:
                        is_requested = True
                    else:
                        friend_request = FriendRequest.objects.filter(Q(sender=user_profile.user, receiver=friend_profile.user, status='pending'))
                        if friend_request:
                            is_requested_by_me = True
                if user_profile:
                    return Response({'status': 200, 'data':{
                    "data": user_serializer.data,
                    "is_friend": is_friend,
                    "is_requested": is_requested,
                    "is_requested_by_me": is_requested_by_me,
                    "posts": posts.data
                    },},
                                status=status.HTTP_200_OK)   
            else:
                return Response({'message': "User profile not found", 'status': 404},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server", 'status': 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FriendRequestBase(APIView):
    permission_classes = (IsAuthenticated,)
    action = ''
    @transaction.atomic

    def post(self, request):
        try:
            user_profile = User.objects.get(username=request.user)
            friend_username = request.data['friend']
            friend_profile = User.objects.get(username=friend_username)

            if user_profile != friend_profile:
                return self.handle_friend_request(user_profile, friend_profile)
            else:
                return Response({'status': 400, 'message': f'You cannot {self.action} yourself'},
                                status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'status': 404, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server", 'status': 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendFriendRequest(FriendRequestBase):
    action = 'send friend request'
    @transaction.atomic

    def handle_friend_request(self, user_profile, friend_profile):
        friend_request = FriendRequest.objects.create(sender=user_profile, receiver=friend_profile, status='pending')
        friend_request.save()
        FriendRequestNotification.objects.create(from_user=user_profile, to_user=friend_profile)
        return Response({'status': 200, 'message': 'Friend request sent'}, status=status.HTTP_200_OK)

class AcceptFriendRequest(FriendRequestBase):
    action = 'accept friend request'
    @transaction.atomic

    def handle_friend_request(self, user_profile, friend_profile):
        friend_request = FriendRequest.objects.get(sender=friend_profile, receiver=user_profile, status='pending')
        friend_request.status = 'accepted'
        friend_request.save()
        Friendship.objects.create(user1=user_profile, user2=friend_profile, status='accepted')
        return Response({'status': 200, 'message': 'Friend request accepted'}, status=status.HTTP_200_OK)

class RejectFriendRequest(FriendRequestBase):
    action = 'reject friend request'
    @transaction.atomic

    def handle_friend_request(self, user_profile, friend_profile):
        friend_request = FriendRequest.objects.get(sender=friend_profile, receiver=user_profile, status='pending')
        friend_request.status = 'rejected'
        friend_request.save()
        return Response({'status': 200, 'message': 'Friend request rejected'}, status=status.HTTP_200_OK)

class CancelFriendRequest(FriendRequestBase):
    action = 'cancel friend request'
    @transaction.atomic
    
    def handle_friend_request(self, user_profile, friend_profile):
        friend_request = FriendRequest.objects.get(sender=user_profile, receiver=friend_profile, status='pending')
        friend_request.delete()
        return Response({'status': 200, 'message': 'Friend request cancelled'}, status=status.HTTP_200_OK)

class RemoveFriend(FriendRequestBase):
    action = 'remove friend'
    @transaction.atomic
    
    def handle_friend_request(self, user_profile, friend_profile):
        friendship = Friendship.objects.get(Q(user1=user_profile, user2=friend_profile) | Q(user1=friend_profile, user2=user_profile), status='accepted')
        friendship.delete()
        return Response({'status': 200, 'message': 'Friend removed'}, status=status.HTTP_200_OK)

class GetFriends(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_profile = User.objects.get(usernam=request.user)
            user_friends = Friendship.objects.filter(Q(user1=user_profile) | Q(user2=user_profile), status='accepted')
            friends_list = []
            for friend in user_friends:
                friends_list.append(friend.user1 if friend.user2 == user_profile else friend.user2)

            all_users = UserProfile.objects.filter(user__is_superuser=False, user__is_staff=False, user__is_active=True).exclude(user=request.user)

            recommended_friends_list = []
            for user_profile in all_users:
                if user_profile in friends_list:
                    user_data = user_profile.user
                    profile_pic = base64.b64encode(user_profile.profile_picture) if user_profile.profile_picture is not None else None
                    recommended_friends_list.append({
                        'username': user_data.username,
                        'profile_pic': profile_pic,
                        'fullname': user_profile.fullname
                    })
            return Response({'status': 200, 'data': recommended_friends_list}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server", 'status': 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetFriendRequests(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_friends = FriendRequest.objects.filter(receiver=user_profile, status='pending')
            friends_list = []
            for friend in user_friends:
                friends_list.append(friend.sender)

            all_users = UserProfile.objects.filter(user__is_superuser=False, user__is_staff=False, user__is_active=True).exclude(user=request.user)

            recommended_friends_list = []
            for user_profile in all_users:
                if user_profile in friends_list:
                    user_data = user_profile.user
                    profile_pic = base64.b64encode(user_profile.profile_picture) if user_profile.profile_picture is not None else None
                    recommended_friends_list.append({
                        'username': user_data.username,
                        'profile_pic': profile_pic,
                        'fullname': user_profile.fullname
                    })
            return Response({'status': 200, 'data': recommended_friends_list}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server", 'status': 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
