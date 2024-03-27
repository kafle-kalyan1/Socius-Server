
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Authentication.urls')),
    path('user/', include('UserData.urls')),
    path('chat/', include('Chat.urls')),
    path('posts/', include('Posts.urls')),
    path('utils/', include('UserUtils.urls')),
    path('notifications/', include('Notification.views')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


