from django.db import models
from django.contrib.auth.models import User
# from cloudinary.models import CloudinaryField
import uuid


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=1000, blank=True, null=True)
    profile_picture =  models.CharField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    isVerified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    secondary_email = models.EmailField(blank=True, null=True)
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    overall_sentiment = models.FloatField(default=0.3)

    def __str__(self):
        return self.user.username



# class UserExtras(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
#     number_of_warnings = models.IntegerField(default=0)
#     number_of_reports = models.IntegerField(default=0)
#     number_of_posts = models.IntegerField(default=0)
#     number_of_comments = models.IntegerField(default=0)
#     number_of_likes = models.IntegerField(default=0)
#     def __str__(self):
#         return self.user.username + " - " + self.follower.username

# class UserData(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     userEducation = models.ManyToManyField('UserEducation', blank=True)
#     userExperience = models.ManyToManyField('UserExperience', blank=True)
    
# class UserEducation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     education_name = models.CharField(max_length=100)
#     education_start_date = models.DateField()
#     education_end_date = models.DateField()
#     education_id = models.UUIDField(default=uuid.uuid4 , editable=False, unique=True)

#     def __str__(self):
#         return self.user.username + " - " + self.education_name

# class UserExperience(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     experience_certificate = models.FileField(upload_to='certificates/', null=True, blank=True)
#     experience_name = models.CharField(max_length=100)
#     experience_start_date = models.DateField()
#     experience_end_date = models.DateField()
#     experience_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    