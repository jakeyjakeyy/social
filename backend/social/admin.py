from django.contrib import admin
from .models import (
    Account,
    Post,
    TextPost,
    Follow,
    Favorite,
    Repost,
    MarkdownPost,
    ImagePost,
)

admin.site.register(Account)
admin.site.register(Post)
admin.site.register(TextPost)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Repost)
admin.site.register(MarkdownPost)
admin.site.register(ImagePost)
