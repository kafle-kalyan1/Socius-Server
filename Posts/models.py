from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.postgres.fields import ArrayField


    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.TextField()
    images = ArrayField(models.CharField(blank=True,null=True), blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    reports_count = models.IntegerField(default=0)
    is_deepfake = models.BooleanField(default=False)

    
    def __str__(self):
      return self.posted_by.user

class Like(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    liked_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='likes')
    
    def __str__(self):
        return self.liked_by-username + " " + self.post


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username + " " + self.post