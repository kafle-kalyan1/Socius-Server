from django.urls import path, include
from .views import CreatePost,GetPosts, LikePost, GetPost, DeletePost, CommentPost, DeleteComment, GetOwnPost, ReportPost, GetReportedPosts, DeleteReportedPost, RemoveFakeReports


urlpatterns = [
   path('createPost/', CreatePost.as_view(), name='create-post'),
   path('getPosts/', GetPosts.as_view(), name='get-posts'),
   path('likePost/', LikePost.as_view(), name='like-post'),
   path('getPost/<uuid:post_uid>/', GetPost.as_view(), name='get-post'),
   path('deletePost/', DeletePost.as_view(), name='delete-post'),
   path('commentPost/', CommentPost.as_view(), name='comment-post'),
   path('deleteComment/', DeleteComment.as_view(), name='delete-post'),
   path('getOwnPost/', GetOwnPost.as_view(), name='get-own-post'),
   path('reportPost/', ReportPost.as_view(), name='report-post'),
   path('getReportedPosts/', GetReportedPosts.as_view(), name='get-reported-posts'),
   path('deleteReportedPost/', DeleteReportedPost.as_view(), name='delete-reported-post'),
   path('removeFakeReports/', RemoveFakeReports.as_view(), name='remove-fake-reports'),
   
   
]