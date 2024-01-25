from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path('chat/<str:username_from>/<str:username_to>/', consumer.ChatConsumer.as_asgi()),
    path('notifications/<str:user>/', consumer.NotificationConsumer.as_asgi()),
]
