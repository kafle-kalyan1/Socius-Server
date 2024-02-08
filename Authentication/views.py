from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserPublicSerializer, UserSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from .utils import send_email_register


import secrets
from django.utils import timezone
from datetime import timedelta

from django.db import transaction


def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[secrets.randbelow(10)]
    return OTP

class UserRegistrationView(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            serializer = UserPublicSerializer(data=request.data)
            if User.objects.filter(username=request.data['username']).exists():
                return Response({'message': "Username is already taken", "status_code":400 }, status=status.HTTP_400_BAD_REQUEST)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = User(username=request.data['username'], email=request.data['email'], password=make_password(
                request.data['password']))
            otp = generateOTP()
            user.save()
            user_profile = UserProfile(
                user=user, isVerified=False, otp=otp, otp_created_at=timezone.now(), gender=request.data['gender'], date_of_birth=request.data['dob'], fullname=request.data['fullname']
            )
            otpResponse = send_email_register(
                self.request, request.data['email'], otp)

            if otpResponse.status_code == 200:
                user_profile.save()
                return Response({'message': "Verification mail successfully send.", "status_code":200}, status=status.HTTP_201_CREATED)            
            else:
                user.delete()
                return Response({'message': "Failed to send email. User creation aborted.","status_code":422, }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e :
            print(e)
            return Response({'message': "Something went wrong on the server.", "status_code":500 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    @transaction.atomic
    def post(self, request):
        try:            
            username = request.data.get('username')
            password = request.data.get('password') 
            # password = decrypt_data(password)      
            # print(password)
            user = authenticate(username=username, password=password)
            print(user)
            if user is not None:
                profile = UserProfile.objects.get(user=user)
                userData = User.objects.get(username=user)
                print(profile)
                if not profile.isVerified:
                    otp = generateOTP()
                    profile.otp = otp
                    profile.otp_created_at = timezone.now()
                    profile.save()
                    emailResponse = send_email_register(
                        self.request, userData.email, otp)
                    if emailResponse.status_code == 200:
                        return Response({'message': "Verification mail successfully send.","status_code":422 },headers={'email':userData.email},status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    else:
                        return Response({'message': "Failed to send email. User creation aborted.","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    refresh = RefreshToken.for_user(user)
                    print(refresh)
                    tokens = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                    return Response(tokens, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Invalid username or password","status_code":401}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e :
            print(e )
            return Response({'message': "Something went wrong on the server","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic

    def get(self, request):
        try:
            user = request.user
            UserData = User.objects.get(username=user)
            profile = UserProfile.objects.get(user=user)

            ser_profile = UserPublicSerializer(UserData).data
            extra = UserSerializer(profile).data
            ser_profile.pop('password')
            ser_profile.pop('id')
            extra.pop('user')

            final_data = { **ser_profile, **extra}
                           
            return Response({'status_code':200,'data':final_data},status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'message': "User profile not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshView(TokenRefreshView):
    @transaction.atomic
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided',"status_code":400}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({'access': access_token})
        except TokenError:
            return Response({'error': 'Invalid refresh token',"status_code":400}, status=status.HTTP_400_BAD_REQUEST)


class SendMail(APIView):
    @transaction.atomic
    def post(self, request):
        send_email_register(self.request)
        return Response({'success': True}, status=status.HTTP_200_OK)


class VerifyOtp(APIView):
    @transaction.atomic
    def post(self ,request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            otp = request.data.get('otp')
            if username is None or email is None:
                return Response({'message': "Username or Email is not provided","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({'message': "Authentication failed","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
                        
            # Check if OTP is provided
            if otp is None:
                return Response({'message': "OTP is not provided","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the user's profile data
            profileData = UserProfile.objects.get(user=user)
            
            # Compare OTP
            if profileData.otp != str(otp):
                return Response({'message': "OTP is not matched","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            
            # check if OTP is expired
     
            # If OTP is matched, set isVerified to True
            if profileData.isVerified:
                return Response({"message": "User is already verified!","status_code":403}, status=status.HTTP_403_FORBIDDEN)
            else:
                if (profileData.otp_created_at is None or profileData.otp_created_at < timezone.now() - timedelta(minutes=1440)):
                    return Response({'message': "OTP is expired click 'Resend' to resend OTP","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
                profileData.isVerified = True
                profileData.otp = None
                profileData.save()
                
                return Response({"message": "Successfully Verified! Now You can login!","status_code":202}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response({"message": "Error Occurred on Server!","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
        

class UpdateProfile(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user)
            userData = User.objects.get(username=user)
            print(userData)
            serializer = UserPublicSerializer(userData, data=request.data, partial=True)
            serializer2 = UserSerializer(profile, data=request.data, partial=True)
            print(serializer)
            print(serializer2)

            if serializer.is_valid() and serializer2.is_valid():
                serializer.save()
                serializer2.save()
                return Response({'message': 'Profile updated successfully',"status_code":200}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Something went wrong',"status_code":400}, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'message': "User profile not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#class for update profile picture
class UpdateProfilePicture(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        try:
           User = request.user
           profile = UserProfile.objects.get(user=User)
           profile_picture_data_uri = request.data.get('profile_picture')
           if not profile_picture_data_uri:
                return Response({'message': 'profile_picture is required', 'status_code': 400}, status=status.HTTP_400_BAD_REQUEST)
           profile.profile_picture = profile_picture_data_uri
           profile.save()
           return Response({'message': 'Profile picture updated successfully', 'status_code': 200}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'message': "User profile not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#class for update password with old password
class UpdatePassword(APIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic
    def post(self, request):
        try:
            user = request.user
            userData = User.objects.get(username=user)
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')
            if old_password is None or new_password is None:
                return Response({'message': "Old Password or New Password is not provided","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=user, password=old_password)
            if user is None:
                return Response({'message': "Authentication failed","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            userData.set_password(new_password)
            userData.save()
            return Response({'message': 'Password updated successfully',"status_code":200}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'message': "User profile not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class ForgetPassword(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            if username is None or email is None:
                return Response({'message': "Username or Email is not provided","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(username=username)
            if user is None:
                return Response({'message': "User not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
            profile = UserProfile.objects.get(user=user)
            if profile is None:
                return Response({'message': "User profile not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
            otp = generateOTP()
            profile.otp = otp
            profile.otp_created_at = timezone.now()
            profile.save()
            emailResponse = send_email_register(
                self.request, email, otp)
            if emailResponse.status_code == 200:
                return Response({'message': "Verification mail successfully send.","status_code":200}, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Failed to send email. User creation aborted.","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ResetPassword(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            otp = request.data.get('otp')
            if username is None or password is None:
                return Response({'message': "Username or Password is not provided","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(username=username)
            if user is None:
                return Response({'message': "User not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
            profile = UserProfile.objects.get(user=user)
            if profile is None:
                return Response({'message': "User profile not found","status_code":404}, status=status.HTTP_404_NOT_FOUND)
            if otp is None:
                return Response({'message': "OTP is not provided","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            if profile.otp != str(otp):
                return Response({'message': "OTP is not matched","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            if profile.otp_created_at < timezone.now() - timedelta(minutes=1440):
                return Response({'message': "OTP is expired click 'Resend' to resend OTP","status_code":400}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            profile.otp = None
            profile.save()
            return Response({'message': 'Password updated successfully',"status_code":200}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server","status_code":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)