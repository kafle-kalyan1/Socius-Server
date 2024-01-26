from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Like
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from .serializers import PostSerializer


# Create your views here.
class CreatePost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        text_content = request.data.get('text_content')
        images = request.data.get('images')
 
        post = Post.objects.create(user=user, text_content=text_content,images=images ,is_deepfake=False)
        return Response({'message': 'Post created successfully'}, status=status.HTTP_201_CREATED)
     
class GetPosts(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        posts = Post.objects.filter(is_deleted=False).order_by('-timestamp')
        serializer = PostSerializer(posts, many=True)
        print(posts.query)
        return Response(serializer.data, status=status.HTTP_200_OK)
     
     
class GetPost(APIView):
      permission_classes = [IsAuthenticated]
      def get(self, request, post_uid):
         post = Post.objects.get(uuid=post_uid)
         serializer = PostSerializer(post)
         return Response(serializer.data, status=status.HTTP_200_OK)

class DeletePost(APIView):
      permission_classes = [IsAuthenticated]
      def delete(self, request, post_id):
         post = Post.objects.get(id=post_id)
         post.is_deleted = True
         post.save()
         return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)
   
class ReportPost(APIView):
      permission_classes = [IsAuthenticated]
      def post(self, request, post_id):
         post = Post.objects.get(id=post_id)
         post.reports_count += 1
         post.save()
         return Response({'message': 'Post reported successfully'}, status=status.HTTP_200_OK)
      
class LikePost(APIView):
      permission_classes = [IsAuthenticated]
      def post(self, request, post_id):
         post = Post.objects.get(id=post_id)
         user = request.user
         like = Like.objects.filter(post=post, liked_by=user)
         if like.exists():
            like.delete()
            post.number_of_likes -= 1
            post.save()
            return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)
         else:
            Like.objects.create(post=post, liked_by=user)
            post.number_of_likes += 1
            post.save()
            return Response({'message': 'Post liked successfully'}, status=status.HTTP_200_OK)

