from rest_framework.views import APIView
from rest_framework.response import Response
from social import models
from rest_framework_simplejwt.authentication import JWTAuthentication

import logging

logger = logging.getLogger(__name__)


class Register(APIView):

    def post(self, request):
        data = request.data
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
        post = models.Post.objects.create(account=account)
        if type == "text":
            models.TextPost.objects.create(
                post=post,
                content=data["content"],
            )
        return Response({"message": "Post created successfully"})

    def get(self, request, page=1):
        page = int(page)
        posts = models.Post.objects.all().order_by("-created_at")[
            (page - 1) * 16 : page * 16
        ]
        post_data = [
            {
                "id": post.id,
                "account": post.account.display_name,
                "created_at": post.created_at,
                "content": (
                    post.text_post.content if hasattr(post, "text_post") else None
                ),
            }
            for post in posts
        ]
        return Response(post_data)
