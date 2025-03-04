from rest_framework.views import APIView
from rest_framework.response import Response
from social import models
from rest_framework_simplejwt.authentication import JWTAuthentication
from html_sanitizer import Sanitizer
from PIL import Image as PILImage

import logging

logger = logging.getLogger(__name__)
sanitizer = Sanitizer()

PAGE_SIZE = 16


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


def is_valid_image_pillow(file_name):
    try:
        with PILImage.open(file_name) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False


def serialize_post(post, request_user=None):
    """
    Serializes a post object into a dictionary containing all post data.
    Args:
        post: Post model instance
        request_user: The currently authenticated user (optional)
    """
    account = (
        models.Account.objects.get(user=request_user)
        if request_user and request_user.is_authenticated
        else None
    )

    post_data = {
        "id": post.id,
        "account_display_name": post.account.display_name if post.account else None,
        "account_username": post.account.user.username if post.account else None,
        "account_id": post.account.id if post.account else None,
        "created_at": post.created_at,
        "content": get_post_content(post),
        "favorited": (
            models.Favorite.objects.filter(account=account, post=post).exists()
            if account
            else False
        ),
        "reposted": (
            models.Repost.objects.filter(account=account, original_post=post).exists()
            if account
            else False
        ),
        "favorite_count": models.Favorite.objects.filter(post=post).count(),
        "repost_count": models.Repost.objects.filter(original_post=post).count(),
        "type": (
            "text"
            if hasattr(post, "text_post")
            else (
                "markdown"
                if hasattr(post, "markdown_post")
                else ("image" if hasattr(post, "image_post") else None)
            )
        ),
        "url": (post.image_post.image.url if hasattr(post, "image_post") else None),
        "is_owner": post.account.user == request_user if account else False,
        "is_repost": post.repost_post.exists(),
        "reply_to": (
            serialize_post(post.reply_to, request_user) if post.reply_to else None
        ),
    }

    # Add original post data if this is a repost
    if post.repost_post.exists():
        original_post = post.repost_post.first().original_post
        post_data["original_post"] = serialize_post(original_post, request_user)
    else:
        post_data["original_post"] = None

    return post_data


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
                # content=sanitizer.sanitize(data["content"]),
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
                original_post=original_post,
            )
            if entry[1] == False:
                post = entry[0].post
                entry[0].delete()
                post.delete()
                return Response({"message": "Unreposted successfully"})
            else:
                entry[0].post = models.Post.objects.create(
                    account=account, reply_to=reply_post
                )
                entry[0].save()
            return Response({"message": "Reposted successfully"})
        elif type == "image":
            if not data["image"]:
                return Response({"message": "No image provided"}, status=400)
            image = data["image"]
            if not is_valid_image_pillow(image):
                return Response({"message": "Invalid file provided"}, status=400)
            post = models.Post.objects.create(account=account, reply_to=reply_post)
            models.ImagePost.objects.create(
                post=post,
                image=image,
                caption=data["caption"],
            )
            return Response({"message": "Image post created successfully"})
        return Response({"message": "Invalid post type"}, status=400)

    def get(self, request):
        page = int(request.GET.get("page", 1))
        replies = request.GET.get("replies", False)
        if replies == False:
            posts = (
                models.Post.objects.all()
                .order_by("-created_at")
                .exclude(reply_to__isnull=False)[
                    (page - 1) * PAGE_SIZE : page * PAGE_SIZE
                ]
            )
        else:
            post = models.Post.objects.get(id=int(replies))
            posts = models.Post.objects.filter(reply_to=post).order_by("-created_at")[
                (page - 1) * PAGE_SIZE : page * PAGE_SIZE
            ]
        account = (
            models.Account.objects.get(user=request.user)
            if request.user.is_authenticated
            else None
        )
        post_data = [
            serialize_post(p, request.user if request.user.is_authenticated else None)
            for p in posts
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
            (page - 1) * PAGE_SIZE : page * PAGE_SIZE
        ]
        post_data = [serialize_post(post, request.user) for post in posts]
        return Response(post_data)
