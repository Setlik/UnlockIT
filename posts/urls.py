from django.urls import path

from posts import views
from posts.views import PostCreateView

app_name = "posts"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # path('payments/', PostPurchaseListView.as_view(), name='payment-list'),
    path("create/", PostCreateView.as_view(), name="create_post"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("user/<str:username>/", views.UserPostsView.as_view(), name="user_posts"),
    path("<int:post_id>/buy/", views.PostBuyView.as_view(), name="post_buy"),
]
