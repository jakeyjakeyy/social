from django.contrib import admin
from django.urls import path

from .views import *

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("token", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("register", Register.as_view(), name="register"),
    path("post", Post.as_view(), name="post"),
    path("post/<int:page>", Post.as_view(), name="post"),
    path("profile/<str:username>/<int:page>", Profile.as_view(), name="profile"),
]
