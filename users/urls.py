from django.urls import path

from users import views
from users.apps import UsersConfig
from users.views import (SubscriptionCancelView, SubscriptionPaymentView,
                         SubscriptionSuccessView)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("confirm/<str:phone>/", views.confirm_code, name="confirm_code"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "subscription/<int:author_pk>/",
        SubscriptionPaymentView.as_view(),
        name="subscription",
    ),
    path(
        "subscription/success/<int:author_pk>/",
        SubscriptionSuccessView.as_view(),
        name="subscription_success",
    ),
    path(
        "subscription/cancel/<int:author_pk>/",
        SubscriptionCancelView.as_view(),
        name="subscription_cancel",
    ),
]
