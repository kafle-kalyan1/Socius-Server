from django.urls import path
from .views import GetNotifications, Search, GetRecomandedUsers, GetSomeTrendingPosts, GetUserSettings

urlpatterns = [
    path('search/', Search.as_view(), name='search'),
    path('notifications/', GetNotifications.as_view(), name='notifications'),
    path('recomandedUsers/', GetRecomandedUsers.as_view(), name='recomanded_users'),
    path('trendingPosts/', GetSomeTrendingPosts.as_view(), name='trending_posts'),
    path('getSettings/', GetUserSettings.as_view(), name='get_settings'),
]