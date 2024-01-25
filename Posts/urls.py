from django.urls import path, include
from .views import CreatePost,GetPosts


urlpatterns = [
   path('createPost/', CreatePost.as_view(), name='create-post'),
   path('getPosts/', GetPosts.as_view(), name='get-posts'),
]