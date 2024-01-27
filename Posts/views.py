from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, Like, Comment
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from .serializers import PostSerializer, CommentSerializer


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
        serializer = PostSerializer(posts, many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
     
     
class GetPost(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, post_uid):
        post = Post.objects.get(id=post_uid)
        serializer = PostSerializer(post)
        comments_for_post = Comment.objects.filter(post=post,is_deleted=False).order_by('-timestamp') 
        comments = CommentSerializer(comments_for_post, many=True) 
        return Response({
            'post': serializer.data,
            'comments': comments.data
        }, status=status.HTTP_200_OK)

class DeletePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get('post_id')
        if not post_id:
            return Response({'error': 'post_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Http404

        if post.user != request.user:
            return Response({'error': 'You are not authorized to delete this post'}, status=status.HTTP_403_FORBIDDEN)

        post.is_deleted = True
        post.save()
        return Response({'message': 'Post deleted successfully',"status":200}, status=status.HTTP_200_OK)
   
class ReportPost(APIView):
      permission_classes = [IsAuthenticated]
      def post(self, request):
         post_id = request.data.get("post_id")
         post = Post.objects.get(id=post_id)
         post.reports_count += 1
         post.save()
         return Response({'message': 'Post reported successfully'}, status=status.HTTP_200_OK)
      
class LikePost(APIView):
      permission_classes = [IsAuthenticated]
      def post(self, request):
         try:
            post_id = request.data.get("post_id")
            post = Post.objects.get(id=post_id)
            user = request.user
            total_like = Like.objects.filter(post=post)
            like = Like.objects.filter(post=post, liked_by=user)
            if like.exists():
               like.delete()
               return Response({'message': 'Post unliked successfully',"status":200,'data':total_like.count()}, status=status.HTTP_200_OK)
            else:
               Like.objects.create(post=post, liked_by=user)
               return Response({'message': 'Post liked successfully',"status":200,'data':total_like.count()}, status=status.HTTP_200_OK)
         except Exception as e:
            print(e)
            return Response({"message":"Some thing went wrong","status":500},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentPost(APIView):
   permission_classes = [IsAuthenticated]
   def post(self, request):
      try:
         post_id = request.data.get("post_id")
         post = Post.objects.get(id=post_id,is_deleted=False)
         user = request.user
         comment = request.data.get("comment")
         Comment.objects.create(user=user, post=post, text=comment)
         comments_for_post = Comment.objects.filter(post=post, is_deleted=False).order_by('-timestamp') 
         comments = CommentSerializer(comments_for_post, many=True) 

         return Response({"message":"Comment added Sucessfully!","status":201,"data":comments.data},status=status.HTTP_201_CREATED)

      except Exception as e:
         print(e)
         return Response({"message":"Comment Failed!","status":500},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteComment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            comment_id = request.data.get("comment_id")
            post_id = request.data.get("post_id")
            user = request.user
            comment = Comment.objects.get(user=user, id=comment_id)
            post = Post.objects.get(id=post_id, is_deleted=False)
            if comment.post == post:
                comment.is_deleted = True
                comment.save()
                comments_for_post = Comment.objects.filter(post=post, is_deleted=False).order_by('-timestamp') 
                comments = CommentSerializer(comments_for_post, many=True)
                return Response({"message":"Comment deleted Sucessfully!","status":200,"data":comments.data},status=status.HTTP_200_OK)
            else:
                return Response({"message":"Comment couldn't found!","status":404},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"message":"Something went wrong","status":500},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
      
class GetOwnPost(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        posts = Post.objects.filter(is_deleted=False, user=user).order_by('-timestamp')
        serializer = PostSerializer(posts, many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
     