from django.urls import path, include
from .views import CreatePost,GetPosts, LikePost, GetPost, DeletePost, CommentPost, DeleteComment, GetOwnPost


urlpatterns = [
   path('createPost/', CreatePost.as_view(), name='create-post'),
   path('getPosts/', GetPosts.as_view(), name='get-posts'),
   path('likePost/', LikePost.as_view(), name='like-post'),
   path('getPost/<uuid:post_uid>/', GetPost.as_view(), name='get-post'),
   path('deletePost/', DeletePost.as_view(), name='delete-post'),
   path('commentPost/', CommentPost.as_view(), name='comment-post'),
   path('deleteComment/', DeleteComment.as_view(), name='delete-post'),
   path('getOwnPost/', GetOwnPost.as_view(), name='get-own-post'),
   
]