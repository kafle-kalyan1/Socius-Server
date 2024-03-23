from django.shortcuts import render
import django.urls
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from Notification.models import Notification
from django.urls import path, include

# Create your views here.
class MarkAllNotificationAsRead(APIView):
    def get(self, request, format=None):
        user = request.user
        try:
            notification = Notification.objects.filter(user_id=user.id, is_read=False)
            for n in notification:
                n.is_read = True
                n.save()
            return Response({
                'status': 200,
                'message': 'All notifications marked as read'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 400,
                'detail': f'{e}',
                'message': 'Something went wrong'
            }, status=status.HTTP_400_BAD_REQUEST)

# create url for mark all notification as read
urlpatterns = [
      path('markallnotificationasread/', MarkAllNotificationAsRead.as_view(), name='mark-all-notification-as-read'),
]