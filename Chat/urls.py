from django.urls import path
from .views import UserMessageView, MessageView

urlpatterns = [
   path('getUserList/', UserMessageView.as_view()),
   path('getMessages/', MessageView.as_view()),
]
