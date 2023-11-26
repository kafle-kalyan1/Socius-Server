from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
import uuid

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=1000, blank=True, null=True)
    profile_picture = CloudinaryField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    isVerified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username
