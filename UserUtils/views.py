from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from Authentication.models import UserProfile
from UserData.models import FriendRequest, Friendship
from Authentication.serializers import UserDetailedSerializer, UserSerializer
from Posts.models import Post
from Posts.serializers import PostSerializer
from django.core.paginator import Paginator


class Search(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            keyword = request.data.get("keyword")
            type = request.data.get("type", "all")
            page = int(request.data.get("page", 1))
            results_per_page = 10

            if not keyword:
                return Response({"message": "Search Failed! keyword is required", "status": 400},
                                status=status.HTTP_400_BAD_REQUEST)

            user_results = []
            post_results = []
            if type in ["all", "users"]:
                users = UserProfile.objects.filter(
                    Q(fullname__icontains=keyword) |
                    Q(user__username__icontains=keyword) | 
                    Q(bio__icontains=keyword)
                ).distinct()
                user_results += list(users)

            if type in ["all", "posts"]:
                posts = Post.objects.filter(text_content__icontains=keyword)
                post_results += list(posts)

            if not user_results and not post_results:
                return Response({"message": "Search Failed! Invalid type", "status": 400},
                                status=status.HTTP_400_BAD_REQUEST)

            paginator = Paginator(user_results + post_results, results_per_page)
            paginated_results = paginator.get_page(page)

            user_serializer = []
            post_serializer = []
            for result in paginated_results:
                if isinstance(result, UserProfile):
                    user_serializer.append(UserDetailedSerializer(result).data)
                elif isinstance(result, Post):
                    post_serializer.append(PostSerializer(result, context={'request': request}).data)

            return Response({"message": "Search Successfully!", "status": 200, "data": {"user_data": user_serializer, "post_data": post_serializer}},
                            status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"message": "Search Failed! Something went wrong", "status": 500},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)