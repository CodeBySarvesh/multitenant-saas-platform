from django.urls import path
from .views import LogoutAPIView, RegisterView, LoginView, UserListAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("users/", UserListAPIView.as_view()),
    path("logout/", LogoutAPIView.as_view()),
]