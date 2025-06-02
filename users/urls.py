from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users import views
from users.apps import UsersConfig


app_name = UsersConfig.name

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path('register/', views.register, name='register'),
    path('confirm/<str:phone>/', views.confirm_code, name='confirm_code'),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
