import django.core.paginator
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Message
from .serializer import MessageSerializer
from django.contrib.auth.models import User
from Authentication.models import UserProfile
import base64
from rest_framework import status
from Authentication.serializers import UserDetailedSerializer, UserPublicSerializer
from Notification.models import MessageNotification
from django.core.paginator import Paginator, EmptyPage



# Create your views here.
#To show all user list with their last message and time
class UserMessageView(APIView):
    def get(self, request, format=None):
        user = request.user
        last_messages = []
        all_users = User.objects.exclude(id=user.id)

        for other_user in all_users:
            last_message = Message.objects.filter(
                Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
            ).order_by('-timestamp').first()
            
            user_profile = UserProfile.objects.get(user=other_user)

            last_messages.append({
                  'username': other_user.username,
                  'last_message': last_message.message if last_message else '',
                  'timestamp': last_message.timestamp if last_message else '',
                  'profile_picture': user_profile.profile_picture,
            })

        return Response({
            'status_code': 200,
            'data': last_messages,
            'user': UserPublicSerializer(user).data.get('username')
        }, status=status.HTTP_200_OK)
        
#To show all message between two user
class MessageView(APIView):
    def get(self, request, format=None):
        user = request.user
        username = request.GET.get('username')
        other_user = User.objects.get(username=username)
        page = int(request.GET.get('page', 1))
        page_size = 20

        messages_query = Message.objects.filter(
        Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
        ).order_by('-timestamp')
        paginator = Paginator(messages_query, page_size)
        
        try:
            messages = paginator.page(page)
        except EmptyPage:
            return Response({
                'status_code': 200,
                'data': [],
            }, status=status.HTTP_200_OK)

        # Mark all messages as read
        MessageNotification.objects.filter(
            sender=other_user, receiver=user, is_read=False
        ).update(is_read=True)
        other_user = UserProfile.objects.get(user=other_user)
        
        user_data = UserDetailedSerializer(other_user).data
        
        serializer = MessageSerializer(messages, many=True)
                
        return Response({
            'status_code': 200,
            'data': serializer.data,
            'user': user_data,
        }, status=status.HTTP_200_OK)
        