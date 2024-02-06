from django.db import models
from django.contrib.auth.models import User
from Authentication.models import UserProfile
import uuid

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"

class Friendship(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('blocked', 'Blocked'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_as_user2')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='accepted')
    friendship_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} <-> {self.user2.username} ({self.status})"

