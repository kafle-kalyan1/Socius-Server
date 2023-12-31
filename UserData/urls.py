from django.urls import path
from .views import GetOtherProfile, RecommendedFriends, GetFriends, GetFriendRequests, AcceptFriendRequest, RejectFriendRequest, SendFriendRequest, CancelFriendRequest, RemoveFriend

urlpatterns = [
    path('getProfile/<str:username>/', GetOtherProfile.as_view(), name='getProfile'),
    path('friends/', RecommendedFriends.as_view(), name='getProfile'),
    path('friendList/', GetFriends.as_view(), name='friendList'),
    path('friendRequests/', GetFriendRequests.as_view(), name='friendRequests'),
    path('acceptFriendRequest/', AcceptFriendRequest.as_view(), name='acceptFriendRequest'),
    path('rejectFriendRequest/', RejectFriendRequest.as_view(), name='rejectFriendRequest'),
    path('sendFriendRequest/', SendFriendRequest.as_view(), name='sendFriendRequest'),
    path('cancelFriendRequest/', CancelFriendRequest.as_view(), name='cancelFriendRequest'),
    path('removeFriend/', RemoveFriend.as_view(), name='removeFriend'),
    
]
