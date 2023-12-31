from django.db import models
from django.contrib.auth.models import User

import uuid
# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class MessageNotification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_message_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_message_notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.message})"