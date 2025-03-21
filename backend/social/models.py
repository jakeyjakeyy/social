from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

User = get_user_model()


def user_image_path(self, filename):
    username = (
        self.post.account.user.username if hasattr(self, "post") else self.user.username
    )
    return f'users/{username}/images/{datetime.now().strftime("%Y/%m/%d")}/{filename}'


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    display_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(
        upload_to=user_image_path, blank=True, null=True
    )
    banner_picture = models.ImageField(upload_to=user_image_path, blank=True, null=True)
    notification_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(pre_save, sender=Account)
def delete_old_profile_images(sender, instance, **kwargs):
    # Check if this is an existing account
    if instance.pk:
        try:
            old_instance = Account.objects.get(pk=instance.pk)

            # Check if profile picture has changed
            if (
                old_instance.profile_picture
                and old_instance.profile_picture != instance.profile_picture
            ):
                if os.path.isfile(old_instance.profile_picture.path):
                    os.remove(old_instance.profile_picture.path)

            # Check if banner picture has changed
            if (
                old_instance.banner_picture
                and old_instance.banner_picture != instance.banner_picture
            ):
                if os.path.isfile(old_instance.banner_picture.path):
                    os.remove(old_instance.banner_picture.path)

        except Account.DoesNotExist:
            pass


class Post(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )

    def __str__(self):
        return f"{self.account.user.username} - {self.created_at}"


class TextPost(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="text_post"
    )
    content = models.TextField(max_length=255)

    def __str__(self):
        return self.content


class MarkdownPost(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="markdown_post"
    )
    content = models.TextField()

    def __str__(self):
        return self.content


class ImagePost(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="image_post"
    )
    image = models.ImageField(upload_to=user_image_path)
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.image.url


@receiver(pre_delete, sender=ImagePost)
def delete_image_file(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


class Follow(models.Model):
    follower = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="followers"
    )

    def __str__(self):
        return f"{self.follower.user.username} follows {self.following.user.username}"


class Favorite(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="favorites"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="favorited_by"
    )

    def __str__(self):
        return f"{self.account.user.username} favorited {self.post.id}"


class Repost(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="reposts"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="repost_post", null=True
    )
    original_post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="reposted_by"
    )

    def __str__(self):
        return f"{self.account.user.username} reposted {self.post.id}"


class Notification(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="notifications"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="notifications", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    action = models.CharField(max_length=255)
    action_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="action_account"
    )

    def __str__(self):
        return f"{self.account.user.username} notified about {self.action_account.user.username} {self.action}"


@receiver(pre_save, sender=Notification)
def send_notification(sender, instance, **kwargs):
    user_id = instance.account.user.id
    token = instance.account.notification_token
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notification_{user_id}_{token}",
        {
            "type": "send_notification",
            "message": {
                "action": instance.action,
                "action_account": instance.action_account.user.username,
                "read": instance.read,
                "created_at": instance.created_at,
                "post_id": instance.post.id if instance.post else None,
            },
        },
    )
