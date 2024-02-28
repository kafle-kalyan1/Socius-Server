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

#choices for notification type
NOTIFICATION_TYPE = (
   ("push", "push"),
   ("app", "app"),
   ("both", "both"),
   ("none", "none")
)

class UserSettings(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   dark_mode = models.CharField(choices=DARK_MODE, default="auto", max_length=5)
   language = models.CharField(choices=LANGUAGES, default="en", max_length=2)
   
   message_notification = models.CharField(choices=NOTIFICATION_TYPE, default="app", max_length=5)
   friend_request_notification = models.CharField(choices=NOTIFICATION_TYPE, default="app", max_length=5)
   post_like_notification = models.CharField(choices=NOTIFICATION_TYPE, default="app", max_length=5)
   post_comment_notification = models.CharField(choices=NOTIFICATION_TYPE, default="app", max_length=5)
   request_accepted_notification = models.CharField(choices=NOTIFICATION_TYPE, default="app", max_length=5)
   
   sync_post_for_offline = models.BooleanField(default=True)
   
   