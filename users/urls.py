from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (
    PaymentListView,
    SubscriptionAPIView,
    UserCreateAPIView,
    UserDestroyAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
    path("update/<int:pk>/", UserUpdateAPIView.as_view(), name="users_update"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="users_retrieve"),
    path(
        "delete/<int:pk>/",
        UserDestroyAPIView.as_view(),
        name="users_delete",
    ),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("subscription/", SubscriptionAPIView.as_view(), name="subscription"),
]
