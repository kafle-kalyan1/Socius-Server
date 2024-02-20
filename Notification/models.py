import Notification.models
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FriendRequestNotification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    is_deleted = models.BooleanField(default=False)

class MessageNotification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_message_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_message_notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.message})"
    
class Notification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    notification_message = models.TextField()
    action_on_view = models.TextField()
    is_deleted = models.BooleanField(default=False)
    