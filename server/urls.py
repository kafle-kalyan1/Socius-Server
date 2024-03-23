
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Authentication.urls')),
    path('user/', include('UserData.urls')),
    path('chat/', include('Chat.urls')),
    path('posts/', include('Posts.urls')),
    path('utils/', include('UserUtils.urls')),
    path('notifications/', include('Notification.views')),
]



