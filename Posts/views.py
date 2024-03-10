import django.db
import django.utils
import django.utils.timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Notification.models import Notification
from .models import Comment, Like, Post, Report
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from .serializers import (CommentSerializer, PostSerializer, PostWithReportsSerializer,
    ReportedPostsSerializer)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from Authentication.models import UserProfile
from UserData.models import FriendRequest, Friendship
from django.db import transaction

from django.shortcuts import get_object_or_404
import better_profanity

# Create your views here.
class CreatePost(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        try:
            user = request.user
            text_content = request.data.get('text_content')
            censor = better_profanity.Profanity()
            images = request.data.get('images')
            deep_fake_confidence = request.data.get('deep_fake_confidence',0)
            is_posted_from_offline = request.data.get('is_posted_from_offline',False)
            analyzer = SentimentIntensityAnalyzer()
            sentiment = analyzer.polarity_scores(text_content)
            user_profile = UserProfile.objects.get(user=user)
            text_content = censor.censor(text_content)
            post = Post.objects.create(user=user, text_content=text_content,images=images,is_posted_from_offline=is_posted_from_offline,deep_fake_confidence=deep_fake_confidence, sentiment_score=sentiment['compound'])
            user_posts = Post.objects.filter(user=user)
            total_sentiment = sum([post.sentiment_score for post in user_posts])
            new_overall_sentiment = total_sentiment / user_posts.count()
            new_overall_sentiment = max(min(new_overall_sentiment + 0.005, 1), -1)
            user_profile.overall_sentiment = new_overall_sentiment
            user_profile.save()
            return Response({'message': 'Post created successfully',"status":201}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"message":"Some thing went wrong","status":500,'detail':e},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetPosts(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def get(self, request):
        sort = request.GET.get('sort', 'default')
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        page = int(request.GET.get('page', 1))  
        results_per_page = 5 

        if sort == 'default':
            user_sentiment = user_profile.overall_sentiment
            lower_bound = user_sentiment - 0.5
            upper_bound = user_sentiment + 0.5
            posts = Post.objects.filter(is_deleted=False, sentiment_score__range=(lower_bound, upper_bound)).order_by('-timestamp')
        elif sort == 'new':
            posts = Post.objects.filter(is_deleted=False).order_by('-timestamp')
        elif sort == 'friend':
            friendships = Friendship.objects.filter(Q(user1=user_profile.user, status='accepted') | Q(user2=user_profile.user, status='accepted'))
            friends = [friendship.user1 if friendship.user2 == user_profile.user else friendship.user2 for friendship in friendships]
            posts = Post.objects.filter(is_deleted=False, user__in=friends).order_by('-timestamp')

        paginator = Paginator(posts, results_per_page)
        paginated_posts = paginator.get_page(page)

        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class GetPost(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def get(self, request, post_uid):
        post = Post.objects.get(id=post_uid)
        serializer = PostSerializer(post,context={'request': request})
        comments_for_post = Comment.objects.filter(post=post,is_deleted=False).order_by('-timestamp') 
        comments = CommentSerializer(comments_for_post, many=True) 
        return Response({
            'post': serializer.data,
            'comments': comments.data
        }, status=status.HTTP_200_OK)

class DeletePost(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        post_id = request.data.get('post_id')
        if not post_id:
            return Response({'error': 'post_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        if post.user != request.user:
            return Response({'error': 'You are not authorized to delete this post'}, status=status.HTTP_403_FORBIDDEN)

        post.is_deleted = True
        post.save()
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.overall_sentiment = max(min(user_profile.overall_sentiment - 0.005, 1), -1)
        user_profile.save()
        return Response({'message': 'Post deleted successfully',"status":200}, status=status.HTTP_200_OK)

   
class ReportPost(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        try:
            post_id = request.data.get("post_id")
            post = get_object_or_404(Post, id=post_id) 
            post.reports_count += 1
            post.save()
            Report.objects.create(post=post, reported_by=request.user, report_reason=request.data.get("report_reason"))
            return Response({'message': 'Post reported successfully',
            'status':200    
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message":"Some thing went wrong","status":500,'detail':e},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
      
class LikePost(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        try:
            post_id = request.data.get("post_id")
            post = Post.objects.get(id=post_id)
            user = request.user
            total_like = Like.objects.filter(post=post)
            like = Like.objects.filter(post=post, liked_by=user)
            user_profile = UserProfile.objects.get(user=user)
            if like.exists():
                like.delete()
                user_profile.overall_sentiment = max(min(user_profile.overall_sentiment - 0.001, 1), -1)
                user_profile.save()
                notification = Notification.objects.filter(user=post.user, action_on_view=f"/post/{post_id}", is_deleted=False)
                notification.update(is_deleted=True)
                return Response({'message': 'Post unliked successfully',"status":200,'data':total_like.count()}, status=status.HTTP_200_OK)
            else:
                Like.objects.create(post=post, liked_by=user)
                user_profile.overall_sentiment = max(min(user_profile.overall_sentiment + 0.001, 1), -1) 
                user_profile.save()
                notification = Notification(
                    timestamp = django.utils.timezone.now(),
                    user = post.user,
                    notification_type = "like",
                    notification_message = f"{post.user} Liked Your Post {post.text_content.strip()[:20] + '...' if len(post.text_content) > 20 else post.text_content}",
                    action_on_view = f"/post/{post_id}",
                )
                notification.save()
                return Response({'message': 'Post liked successfully',"status":200,'data':total_like.count()}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message":"Some thing went wrong","status":500},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentPost(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        try:
            post_id = request.data.get("post_id")
            post = Post.objects.get(id=post_id,is_deleted=False)
            user = request.user
            comment = request.data.get("comment")
            Comment.objects.create(user=user, post=post, text=comment)
            user_profile = UserProfile.objects.get(user=user)
            user_profile.overall_sentiment = max(min(user_profile.overall_sentiment + 0.002, 1), -1)
            user_profile.save()
            notification = Notification(
                    timestamp = django.utils.timezone.now(),
                    user = post.user,
                    notification_type = "comment",
                    notification_message = f"{post.user} Commented in Your Post {comment.strip()[:20] + '...' if len(comment) > 20 else comment}",
                    action_on_view = f"/post/{post_id}",
                )
            notification.save()
            comments_for_post = Comment.objects.filter(post=post, is_deleted=False).order_by('-timestamp') 
            comments = CommentSerializer(comments_for_post, many=True) 

            return Response({"message":"Comment added Sucessfully!","status":201,"data":comments.data},status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response({"message":"Comment Failed!","status":500},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class DeleteComment(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
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
                notification = Notification.objects.filter(user=post.user, action_on_view=f"/post/{post_id}", is_deleted=False)
                notification.update(is_deleted=True)
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
    @transaction.atomic
    def get(self, request):
        user = request.user
        posts = Post.objects.filter(is_deleted=False, user=user).order_by('-timestamp')
        serializer = PostSerializer(posts, many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
     
# class ReportPost(APIView):
#     permission_classes = [IsAuthenticated]
#     @transaction.atomic
#     def post(self, request):
#         try:
#             post_id = request.data.get("post_id")
#             post_data = Post.objects.get_object_or_404(id=post_id)
#             if not post_data:
#                 return Response({"message":"Post couldn't found!","status":404},status=status.HTTP_404_NOT_FOUND)
#             else:
#                 post_data.reports_count += post_data.reports_count
#                 post_data.save()

#         except Exception as e:
#             print(e)
#             return Response(
#                 {
#                     "message": "Something went wrong",
#                     "status": 500,
#                     "detail":e
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )        
            
            
class GetReportedPosts(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def get(self, request):
        user = request.user
        if user.is_staff:
            reported_posts = Post.objects.filter(reports__isnull=False).distinct()
            serializer = PostWithReportsSerializer(reported_posts, many=True, context={'request': request})
            return Response({"message":"Posts Loaded Sucesfully","status":200,"data":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"You are not authorized to view this page","status":403},status=status.HTTP_403_FORBIDDEN) 
    
class RemoveFakeReports(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        user = request.user
        if user.is_staff:
            post_id = request.data.get("post_id")
            post = Post.objects.get(id=post_id, is_deleted=False)
            post.reports_count = 0
            post.save()
            reports = Report.objects.filter(post=post)
            reports.delete()
            return Response({"message":"Fake Reports Removed Sucesfully","status":200}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"You are not authorized to view this page","status":403},status=status.HTTP_403_FORBIDDEN)
        
class DeleteReportedPost(APIView):
    permission_classes = [IsAuthenticated,]
    @transaction.atomic
    def post(self, request):
        user = request.user
        if user.is_staff:
            post_id = request.data.get("post_id")
            if not post_id:
                return Response({"message":"Post Id is required","status":400},status=status.HTTP_400_BAD_REQUEST)
            elif not Post.objects.filter(id=post_id).exists():
                return Response({"message":"Post couldn't found!","status":404},status=status.HTTP_404_NOT_FOUND)
            else:
                post = Post.objects.get(id=post_id)
                post.is_deleted = True
                post.save()
                reports = Report.objects.filter(post=post)
                reports.delete()
                return Response({"message":"Post Deleted Sucesfully","status":200}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"You are not authorized to view this page","status":403},status=status.HTTP_403_FORBIDDEN)
            
        