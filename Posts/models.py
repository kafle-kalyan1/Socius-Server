from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.postgres.fields import ArrayField
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


    
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    return sentiment_scores
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_content = models.TextField()
    images = ArrayField(models.CharField(blank=True,null=True), blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    reports_count = models.IntegerField(default=0)
    deep_fake_confidence = models.FloatField(default=0)
    is_posted_from_offline = models.BooleanField(default=False)
    sentiment_score = models.FloatField(default=0)

    
    def __str__(self):
      return self.posted_by.user
    
  
    def save(self, *args, **kwargs):
        sentiment_scores = analyze_sentiment(self.text_content)
        self.sentiment_score = sentiment_scores['compound']
        super().save(*args, **kwargs)

class Like(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    liked_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='likes')
    
    def __str__(self):
        return self.liked_by.username + " " + self.post.user.username


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username + " " + self.post
    
class Report(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='reports')
    report_reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.reported_by.username + " " + self.post.user.username
    