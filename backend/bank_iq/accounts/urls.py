from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import LoginView, LogoutAndBlacklistRefreshTokenView, RegisterView, UserMeView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),

    path("login/", LoginView.as_view(), name="auth_login"),

    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/access/", TokenVerifyView.as_view(), name="token_varify"),

    path("logout/", LogoutAndBlacklistRefreshTokenView.as_view(), name="auth_logout"),

    path("me/", UserMeView.as_view(), name="user_me"),

]
