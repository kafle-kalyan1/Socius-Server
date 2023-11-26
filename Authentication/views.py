from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserPublicSerializer, UserSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from .utils import send_email_register


import secrets
import time
from django.utils import timezone
from datetime import timedelta
import os
from django.shortcuts import render



def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[secrets.randbelow(10)]
    return OTP

class UserRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = UserPublicSerializer(data=request.data)
            if User.objects.filter(username=request.data['username']).exists():
                return Response({'message': "Username is already taken"}, status=status.HTTP_400_BAD_REQUEST)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            user = User(username=request.data['username'], email=request.data['email'], password=make_password(
                request.data['password']))
            otp = generateOTP()
            user.save()
            user_profile = UserProfile(
                user=user, isVerified=False, otp=otp, otp_created_at=timezone.now(), gender=request.data['gender'], date_of_birth=request.data['dob']
            )
            otpResponse = send_email_register(
                self.request, request.data['email'], otp)

            if otpResponse.status_code == 200:
                user_profile.save()
                return Response({'message': "Verification mail successfully send."}, status=status.HTTP_201_CREATED)
            else:
                user.delete()
                return Response({'message': "Failed to send email. User creation aborted."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e :
            print(e )
            user.delete()
            return Response({'message': "Something went wrong on the server."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    def post(self, request):
        try:            
            username = request.data.get('username')
            password = request.data.get('password')       
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
                        return Response({'message': "Verification mail successfully send."},headers={'email':userData.email},status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                    else:
                        return Response({'message': "Failed to send email. User creation aborted."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    refresh = RefreshToken.for_user(user)
                    print(refresh)
                    tokens = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                    return Response(tokens, status=status.HTTP_200_OK)
            else:
                return Response({'message': "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e :
            print(e )
            return Response({'message': "Something went wrong on the server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user)   
            print(profile)
            return Response(status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'message': "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshView(TokenRefreshView):
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({'access': access_token})
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class SendMail(APIView):
    def post(self, request):
        send_email_register(self.request)
        return Response({'success': True}, status=status.HTTP_200_OK)


class VerifyOtp(APIView):
    def post(self ,request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            otp = request.data.get('otp')
            if username is None or email is None:
                return Response({'message': "Username or Email is not provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({'message': "Authentication failed"}, status=status.HTTP_400_BAD_REQUEST)
                        
            # Check if OTP is provided
            if otp is None:
                return Response({'message': "OTP is not provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the user's profile data
            profileData = UserProfile.objects.get(user=user)
            
            # Compare OTP
            if profileData.otp != str(otp):
                return Response({'message': "OTP is not matched"}, status=status.HTTP_400_BAD_REQUEST)
            
            # check if OTP is expired
     
            # If OTP is matched, set isVerified to True
            if profileData.isVerified:
                return Response({"message": "User is already verified!"}, status=status.HTTP_403_FORBIDDEN)
            else:
                if (profileData.otp_created_at is None or profileData.otp_created_at < timezone.now() - timedelta(minutes=1440)):
                    return Response({'message': "OTP is expired click 'Resend' to resend OTP"}, status=status.HTTP_400_BAD_REQUEST)
                profileData.isVerified = True
                profileData.save()
                return Response({"message": "Successfully Verified! Now You can login!"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response({"message": "Error Occurred on Server!"}, status=status.HTTP_400_BAD_REQUEST)
        

class UpdateProfile(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        try:
            user = request.user
            profile = UserProfile.objects.get(user=user)
            userData = User.objects.get(username=user)
            serializer = UserPublicSerializer(userData, data=request.data, partial=True)
            serializer2 = UserSerializer(profile, data=request.data, partial=True)

            if serializer.is_valid() and serializer2.is_valid():
                # if 'profile_picture' in request.data or request.data['profile_picture'] == "":
                #     serializer2.fields.pop('profile_picture')
                # print(serializer2.fields)
                serializer.save()
                serializer2.save()
                return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Maybe Username Already Exist'}, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({'message': "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'message': "Something went wrong on the server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
