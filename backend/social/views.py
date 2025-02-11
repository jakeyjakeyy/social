from rest_framework.views import APIView
from rest_framework.response import Response
from social import models
from rest_framework_simplejwt.authentication import JWTAuthentication
from html_sanitizer import Sanitizer

import logging

logger = logging.getLogger(__name__)
sanitizer = Sanitizer()


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


def get_post_content(post):
    match post:
        case _ if hasattr(post, "text_post"):
            return post.text_post.content
        case _ if hasattr(post, "markdown_post"):
            return post.markdown_post.content
        case _ if hasattr(post, "image_post"):
            return post.image_post.caption
        case _:
            return None


class Post(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        account = models.Account.objects.get(user=request.user)
        reply_id = data.get("reply_id")
        reply_post = models.Post.objects.get(id=reply_id) if reply_id else None

        type = data["type"]
        if type == "text":
            post = models.Post.objects.create(account=account, reply_to=reply_post)
            models.TextPost.objects.create(
                post=post,
                content=data["content"],
            )
            return Response({"message": "Post created successfully"})
        elif type == "markdown":
            post = models.Post.objects.create(account=account, reply_to=reply_post)
            models.MarkdownPost.objects.create(
                post=post,
                content=sanitizer.sanitize(data["content"]),
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
        elif type == "image":
            if not data["image"]:
                return Response({"message": "No image provided"}, status=400)
            post = models.Post.objects.create(account=account, reply_to=reply_post)
            models.ImagePost.objects.create(
                post=post,
                image=data["image"],
                caption=data["caption"],
            )
            return Response({"message": "Image post created successfully"})
        return Response({"message": "Invalid post type"}, status=400)

    def get(self, request):
        page = int(request.GET.get("page", 1))
        posts = (
            models.Post.objects.all()
            .order_by("-created_at")
            .exclude(reply_to__isnull=False)[(page - 1) * 16 : page * 16]
        )
        account = (
            models.Account.objects.get(user=request.user)
            if request.user.is_authenticated
            else None
        )
        post_data = [
            {
                "id": post.id,
                "account_display_name": post.account.display_name,
                "account_username": post.account.user.username,
                "account_id": post.account.id,
                "created_at": post.created_at,
                "content": get_post_content(post),
                "favorited": (
                    models.Favorite.objects.filter(account=account, post=post).exists()
                    if account
                    else False
                ),
                "reposted": (
                    models.Repost.objects.filter(account=account, post=post).exists()
                    if account
                    else False
                ),
                "favorite_count": models.Favorite.objects.filter(post=post).count(),
                "repost_count": models.Repost.objects.filter(post=post).count(),
                "type": (
                    "text"
                    if hasattr(post, "text_post")
                    else (
                        "markdown"
                        if hasattr(post, "markdown_post")
                        else ("image" if hasattr(post, "image_post") else None)
                    )
                ),
                "url": (
                    post.image_post.image.url if hasattr(post, "image_post") else None
                ),
                "is_owner": post.account.user == request.user,
            }
            for post in posts
        ]
        return Response(post_data)

    def delete(self, request):
        post_id = request.GET.get("id")
        post = models.Post.objects.get(id=post_id)
        if post.account.user != request.user:
            return Response(
                {"detail": "You do not have permission to delete this post"}, status=403
            )
        post.delete()
        return Response({"message": "Post deleted successfully"})


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
                "content": get_post_content(post),
                "favorited": (
                    models.Favorite.objects.filter(account=account, post=post).exists()
                    if account
                    else False
                ),
                "reposted": (
                    models.Repost.objects.filter(account=account, post=post).exists()
                    if account
                    else False
                ),
                "favorite_count": models.Favorite.objects.filter(post=post).count(),
                "repost_count": models.Repost.objects.filter(post=post).count(),
                "type": (
                    "text"
                    if hasattr(post, "text_post")
                    else (
                        "markdown"
                        if hasattr(post, "markdown_post")
                        else ("image" if hasattr(post, "image_post") else None)
                    )
                ),
                "url": (
                    post.image_post.image.url if hasattr(post, "image_post") else None
                ),
                "is_owner": post.account.user == request.user,
            }
            for post in posts
        ]
        return Response(post_data)
