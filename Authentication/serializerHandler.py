from django.shortcuts import render
from .serializers import UserSerializer
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

from .models import UserProfile

# Create your views here.
class UserData(ListAPIView):
   queryset = UserProfile.objects.all()
   serializer_class = UserSerializer

class AccountRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer
    
