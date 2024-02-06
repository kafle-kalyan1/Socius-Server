from django.urls import path
from .views import GetNotifications, Search

urlpatterns = [
    path('search/', Search.as_view(), name='search'),
    path('notifications/', GetNotifications.as_view(), name='notifications'),
]