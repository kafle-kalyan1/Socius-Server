
from django.urls import path
from .serializerHandler import UserData, AccountRetrieveUpdateDestroyView
from .views import UserRegistrationView, UserLoginView, UserProfileView, RefreshView, SendMail, VerifyOtp, UpdateProfile, UpdateProfilePicture, UpdatePassword


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('accounts/', UserData.as_view(), name='account-list-create'),
    path('accounts/<uuid:pk>/', AccountRetrieveUpdateDestroyView.as_view(), name='account-retrieve-update-destroy'),
    
     path('register/', UserRegistrationView.as_view(), name='user-registration'),
     path('login/', UserLoginView.as_view(), name='user-login'),
     path('user/', UserProfileView.as_view(), name='user-data'),
     
      path('refresh/', RefreshView.as_view(), name='token-refresh'),
      path('email/', SendMail.as_view(), name='send_email'),
      path('verify/', VerifyOtp.as_view(), name='verify'),
      path('update/', UpdateProfile.as_view(), name='update-profile'),
      path('updateProfilePicture/', UpdateProfilePicture.as_view(), name='update-profile-picture'),
      path('changePassword/', UpdatePassword.as_view(), name='change-password'),
     
     
    #  path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
   # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]