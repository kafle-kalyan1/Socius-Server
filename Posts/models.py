from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Media(models.Model):
    file = models.FileField(upload_to='post_media/')
    def save(self, *args, **kwargs):
        username = self.user.username 
        self.file.name = os.path.join('post_media/', username, self.file.name)
        super().save(*args, **kwargs)
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.TextField()
    media = models.ManyToManyField(Media, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    reports_count = models.IntegerField(default=0)
    is_deepfake = models.BooleanField(default=False)
    
    def __str__(self):
      return self.posted_by.user
class Image(models.Model):
    image = models.ImageField(upload_to='post_images/')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')
class Like(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    liked_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='likes')
    
    def __str__(self):
        return self.liked_by-username + " " + self.post


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)