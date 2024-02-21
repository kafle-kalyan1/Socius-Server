from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserSettings(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   dark_mode = models.CharField(max_length=50, default="false")
   langauge = models.CharField(max_length=50, default="en")
   message_notification = models.BooleanField(default=True)
   friend_request_notification = models.BooleanField(default=True)
   post_notification = models.BooleanField(default=True)
   sync_post_for_offline = models.BooleanField(default=True)
   
   