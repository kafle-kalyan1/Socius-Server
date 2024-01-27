from django.urls import path
from Chat.consumer import ChatConsumer
from Notification.consumers import NotificationConsumer


websocket_urlpatterns = [
    path('chat/<str:username_from>/<str:username_to>/', ChatConsumer.as_asgi()),
    path('notifications/<str:user>/', NotificationConsumer.as_asgi()),
]
