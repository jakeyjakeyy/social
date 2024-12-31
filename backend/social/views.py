from rest_framework.views import APIView
from rest_framework.response import Response
from social import models
from rest_framework_simplejwt.authentication import JWTAuthentication

import logging

logger = logging.getLogger(__name__)


class Register(APIView):

    def post(self, request):
        data = request.data
        if models.User.objects.filter(username=data["username"].lower()).exists():
            return Response({"detail": "Username already exists"}, status=400)
        user = models.User.objects.create_user(
            username=data["username"].lower(),
            password=data["password"],
        )
        account = models.Account.objects.create(
            user=user,
            display_name=data["username"],
        )
        return Response({"message": "User created successfully"})


class Post(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        account = models.Account.objects.get(user=request.user)
        type = data["type"]
        if type == "text":
            post = models.Post.objects.create(account=account)
            models.TextPost.objects.create(
                post=post,
                content=data["content"],
            )
            return Response({"message": "Post created successfully"})
        elif type == "favorite":
            post = models.Post.objects.get(id=data["post_id"])
            entry = models.Favorite.objects.get_or_create(
                account=account,
                post=post,
            )
            if entry[1] == False:
                entry[0].delete()
                return Response({"message": "Unfavorited successfully"})
            return Response({"message": "Favorited successfully"})
        elif type == "repost":
            original_post = models.Post.objects.get(id=data["post_id"])
            entry = models.Repost.objects.get_or_create(
                account=account,
                post=original_post,
            )
            if entry[1] == False:
                entry[0].delete()
                return Response({"message": "Unreposted successfully"})
            return Response({"message": "Reposted successfully"})
        return Response({"message": "Invalid post type"}, status=400)

    def get(self, request, page=1):
        page = int(page)
        posts = models.Post.objects.all().order_by("-created_at")[
            (page - 1) * 16 : page * 16
        ]
        post_data = [
            {
                "id": post.id,
                "account_display_name": post.account.display_name,
                "account_username": post.account.user.username,
                "account_id": post.account.id,
                "created_at": post.created_at,
                "content": (
                    post.text_post.content if hasattr(post, "text_post") else None
                ),
            }
            for post in posts
        ]
        return Response(post_data)


class Profile(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request, username, page=1):
        page = int(page)
        account = models.Account.objects.get(
            user=models.User.objects.get(username=username)
        )
        posts = models.Post.objects.filter(account=account).order_by("-created_at")[
            (page - 1) * 16 : page * 16
        ]
        post_data = [
            {
                "id": post.id,
                "account_display_name": post.account.display_name,
                "account_username": post.account.user.username,
                "account_id": post.account.id,
                "created_at": post.created_at,
                "content": (
                    post.text_post.content if hasattr(post, "text_post") else None
                ),
            }
            for post in posts
        ]
        return Response(post_data)
