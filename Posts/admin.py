from django.contrib import admin

# Register your models here.
from .models import Post, Image, Like, Comment

admin.site.register(Post)
admin.site.register(Image)
admin.site.register(Like)
admin.site.register(Comment)
