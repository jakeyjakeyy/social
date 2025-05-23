import html
import logging
import secrets
from PIL import Image as PILImage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from social import models
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)

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
        "account_profile_picture": (
            post.account.profile_picture.url if post.account.profile_picture else None
        ),
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
        if not request.user.is_authenticated:
            return Response({"message": "Not logged in"}, status=401)
        
        data = request.data
        account = models.Account.objects.get(user=request.user)
        reply_id = data.get("reply_id")
        reply_post = models.Post.objects.get(id=reply_id) if reply_id else None
        action = None

        type = data["type"]
        if type == "text":
            post = models.Post.objects.create(account=account, reply_to=reply_post)
            models.TextPost.objects.create(
                post=post,
                content=data["content"],
            )
            if reply_post:
                action = "replied"
        elif type == "markdown":
            post = models.Post.objects.create(account=account, reply_to=reply_post)
            models.MarkdownPost.objects.create(
                post=post,
                # content=html.escape(data["content"]),
                content=data["content"],
            )
            if reply_post:
                action = "replied"
        elif type == "favorite":
            post = models.Post.objects.get(id=data["post_id"])
            entry = models.Favorite.objects.get_or_create(
                account=account,
                post=post,
            )
            if entry[1] == False:
                entry[0].delete()
                models.Notification.objects.filter(
                    account=post.account,
                    post=post,
                    action="favorited",
                    action_account=account,
                ).delete()
                return Response({"message": "Unfavorited successfully"})
            action = "favorited"
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
                models.Notification.objects.filter(
                    account=original_post.account,
                    post=original_post,
                    action="reposted",
                    action_account=account,
                ).delete()
                return Response({"message": "Unreposted successfully"})
            else:
                entry[0].post = models.Post.objects.create(
                    account=account, reply_to=reply_post
                )
                entry[0].save()
                action = "reposted"
                post = original_post
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
            if reply_post:
                action = "replied"
        else:
            return Response({"message": "Invalid post type"}, status=400)

        if action is not None:
            models.Notification.objects.create(
                account=post.account,
                post=post,
                action=action,
                action_account=account,
            )
        return Response({"message": "Post created successfully"})

    def get(self, request):
        if request.GET.get("id"):
            post = models.Post.objects.get(id=request.GET.get("id"))
            return Response(
                serialize_post(
                    post, request.user if request.user.is_authenticated else None
                )
            )
        timestamp = int(request.GET.get("timestamp", datetime.now().timestamp() * 1000))
        time_from = datetime.fromtimestamp(timestamp / 1000)
        replies = request.GET.get("replies", False)
        followingFeed = request.GET.get("following", False)
        if replies == False:  # Get all posts (that aren't replies)
            if followingFeed:  # Get posts from users that the user is following
                account = models.Account.objects.get(user=request.user)
                following = models.Follow.objects.filter(follower=account)
                posts = (
                    models.Post.objects.filter(
                        account__in=[f.following for f in following]
                    )
                    .order_by("-created_at")
                    .exclude(reply_to__isnull=False)
                    .filter(created_at__lte=time_from)[0:PAGE_SIZE]
                )
            else:  # Else get all posts
                posts = (
                    models.Post.objects.all()
                    .order_by("-created_at")
                    .exclude(reply_to__isnull=False)
                    .filter(created_at__lte=time_from)[0:PAGE_SIZE]
                )
        else:  # Get replies to a specific post
            post = models.Post.objects.get(id=int(replies))
            posts = (
                models.Post.objects.filter(reply_to=post)
                .order_by("-created_at")
                .filter(created_at__lte=time_from)[0:PAGE_SIZE]
            )
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
        models.Notification.objects.filter(post=post).delete()
        post.delete()
        return Response({"message": "Post deleted successfully"})


class Profile(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        timestamp = int(request.GET.get("timestamp", datetime.now().timestamp() * 1000))
        time_from = datetime.fromtimestamp(timestamp / 1000)
        username = request.GET.get("username")
        account = models.Account.objects.get(
            user=models.User.objects.get(username=username)
        )
        posts = (
            models.Post.objects.filter(account=account)
            .order_by("-created_at")
            .filter(created_at__lte=time_from)[0:PAGE_SIZE]
        )
        post_data = [serialize_post(post, request.user) for post in posts]
        return Response(post_data)


class GetAccountId(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        username = request.GET.get("username")
        account = models.Account.objects.get(user__username=username)
        return Response({"id": account.id})


class Follow(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        username = request.GET.get("username")
        if not request.user.is_authenticated:
            return Response({"message": "Not logged in"}, status=401)
        account = models.Account.objects.get(user=request.user)
        if username is not None:  # Checks if user is following specific username
            following = models.Account.objects.get(user__username=username)
            return Response(
                {
                    "following": models.Follow.objects.filter(
                        follower=account, following=following
                    ).exists()
                }
            )
        else:  # Returns all users that the user is following
            following = models.Follow.objects.filter(follower=account)
            following_data = [
                {
                    "id": f.following.id,
                    "display_name": f.following.display_name,
                    "username": f.following.user.username,
                }
                for f in following
            ]
            return Response(following_data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "Not logged in"}, status=401)
        data = request.data
        follower = models.Account.objects.get(user=request.user)
        following = models.Account.objects.get(user__username=data["username"])
        object = models.Follow.objects.get_or_create(
            follower=follower,
            following=following,
        )
        if object[1] == False:
            object[0].delete()
            models.Notification.objects.filter(
                account=following,
                post=None,
                action="followed",
                action_account=follower,
            ).delete()
            return Response({"message": "Unfollowed successfully"})
        else:
            models.Notification.objects.create(
                account=following,
                post=None,
                action="followed",
                action_account=follower,
            )
            return Response({"message": "Followed successfully"})


class ProfileInfo(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        username = request.GET.get("username")
        account = models.Account.objects.get(user__username=username)
        following = models.Follow.objects.filter(follower=account).count()
        followers = models.Follow.objects.filter(following=account).count()
        return Response(
            {
                "display_name": account.display_name,
                "followers": followers,
                "following": following,
                "username": account.user.username,
                "is_owner": account.user == request.user,
                "is_following": (
                    models.Follow.objects.filter(
                        follower=request.user.account, following=account
                    ).exists()
                    if request.user.is_authenticated
                    else False
                ),
                "profile_picture": (
                    account.profile_picture.url if account.profile_picture else None
                ),
                "banner_picture": (
                    account.banner_picture.url if account.banner_picture else None
                ),
            }
        )

    def post(self, request):
        data = request.data
        if not request.user.is_authenticated:
            return Response({"message": "Not logged in"}, status=401)
        username = data["username"]
        if request.user.username != username:
            return Response({"message": "Not authorized"}, status=403)
        account = models.Account.objects.get(user=request.user)
        if data["type"] == "pfp":
            if not is_valid_image_pillow(data["file"]):
                return Response({"message": "Invalid file provided"}, status=400)
            account.profile_picture = data["file"]
            account.save()
        if data["type"] == "banner":
            if not is_valid_image_pillow(data["file"]):
                return Response({"message": "Invalid file provided"}, status=400)
            account.banner_picture = data["file"]
            account.save()
        if data["type"] == "display_name":
            account.display_name = data["display_name"]
            account.save()
        return Response({"message": "Profile updated successfully"})


class NotificationToken(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "Not logged in"}, status=401)
        account = models.Account.objects.get(user=request.user)

        try:
            stream = models.NotificationStream.objects.get(account=account)
        except models.NotificationStream.DoesNotExist:
            stream = models.NotificationStream.objects.create(account=account)

        secure_token = secrets.token_urlsafe(32)
        stream.token = secure_token
        stream.created_at = timezone.now()
        stream.save()
        return Response({"token": secure_token})


def serialize_notification(notification):
    return {
        "action_account_displayname": notification.action_account.display_name,
        "action_account": notification.action_account.user.username,
        "action": notification.action,
        "post_id": notification.post.id if notification.post else None,
        "created_at": notification.created_at,
        "read": notification.read,
        "notification_id": notification.id,
    }


class Notification(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        timestamp = int(request.GET.get("timestamp", datetime.now().timestamp() * 1000))
        time_from = datetime.fromtimestamp(timestamp / 1000)
        if not request.user.is_authenticated:
            return Response({"message": "Not logged in"}, status=401)
        account = models.Account.objects.get(user=request.user)
        notifications = models.Notification.objects.filter(account=account).order_by(
            "-created_at"
        )
        notifications = notifications.filter(created_at__lte=time_from)
        notifications = notifications[0:PAGE_SIZE]
        return Response([serialize_notification(n) for n in notifications])

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "Not logged in"}, status=401)
        account = models.Account.objects.get(user=request.user)
        data = request.data
        if data["type"] == "read":
            notification_id = data["notification_id"]
            notification = models.Notification.objects.get(id=notification_id)
            if notification.account != account:
                return Response({"message": "Not authorized"}, status=403)
            notification.read = True
            notification.save()
            return Response({"message": "Notification read successfully"})
        elif data["type"] == "all":
            notifications = models.Notification.objects.filter(account=account)
            for notification in notifications:
                notification.read = True
                notification.save()
            return Response({"message": "All notifications read successfully"})
