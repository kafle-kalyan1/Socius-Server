from django.contrib.auth.models import User
from django.db import models

# Create your models here.

# choice field for dark mode
DARK_MODE = (
   ("auto", "auto"),
   ("light", "light"),
   ("dark", "dark")
)

# choice field for language
LANGUAGES = (
   ("en", "en"),
   ("np", "np"),
)

class UserSettings(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   dark_mode = models.CharField(choices=DARK_MODE, default="auto", max_length=5)
   language = models.CharField(choices=LANGUAGES, default="en", max_length=2)
   
   message_notification = models.BooleanField(default=True)
   friend_request_notification = models.BooleanField(default=True)
   post_notification = models.BooleanField(default=True)
   
   sync_post_for_offline = models.BooleanField(default=True)
   
   