from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user_service.views import CreateUserView, UpdateRetrieveUserView

urlpatterns = [
    path("users/", CreateUserView.as_view(), name="register"),
    path("users/me/", UpdateRetrieveUserView.as_view(), name="manage"),
    path("users/token/", TokenObtainPairView.as_view(), name="login"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

app_name = "user_service"
