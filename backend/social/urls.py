from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("token", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("register", Register.as_view(), name="register"),
    path("post", Post.as_view(), name="post"),
    path("profile", Profile.as_view(), name="profile"),
    path("profile/info", ProfileInfo.as_view(), name="profile-info"),
    path("follow", Follow.as_view(), name="follow"),
    path("account/id", GetAccountId.as_view(), name="get-account-id"),
    path("notification/token", NotificationToken.as_view(), name="notification-token"),
    path("notification", Notification.as_view(), name="notification"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
