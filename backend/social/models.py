from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    display_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.user.username} - {self.created_at}"


class TextPost(models.Model):
    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="text_post"
    )
    content = models.TextField(max_length=255)

    def __str__(self):
        return self.content
