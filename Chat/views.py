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
from Authentication.serializers import UserPublicSerializer



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

            profile_picture = None
            if user_profile.profile_picture:
                  profile_picture = base64.b64encode(user_profile.profile_picture).decode('utf-8')

            last_messages.append({
                  'username': other_user.username,
                  'last_message': last_message.message if last_message else '',
                  'timestamp': last_message.timestamp if last_message else '',
                  'profile_picture': profile_picture,
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
        print(page)
        page_size = 10

        messages = Message.objects.filter(
            Q(sender=user, receiver=other_user) | Q(sender=other_user, receiver=user)
        ).order_by('-timestamp')[(page - 1) * page_size : page * page_size]

        print(messages.query)

        serializer = MessageSerializer(messages, many=True)
                
        return Response({
            'status_code': 200,
            'data': serializer.data,
        }, status=status.HTTP_200_OK)