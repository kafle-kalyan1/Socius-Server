from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationViewTestCase(APITestCase):
    def test_user_registration_success(self):
        # Prepare test data
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword',
            'gender': 'Male',
            'dob': '1990-01-01',
            'fullname': 'Test User',
            'profile_picture': "https://www.example.com/test.jpg"
        }

        response = self.client.post(reverse('user-registration'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='testuser').exists())

    def test_user_registration_existing_username(self):
        # Prepare test data
        existing_user = User.objects.create_user(username='existinguser', password='testpassword')
        data = {
            'username': 'existinguser',  
            'email': 'test@example.com',
            'password': 'testpassword',
            'gender': 'Male',
            'dob': '1990-01-01',
            'fullname': 'Test User',
            'profile_picture': "https://www.example.com/test.jpg"
        }

        response = self.client.post(reverse('user-registration'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
