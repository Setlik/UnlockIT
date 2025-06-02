from django.urls import path

from posts.views import PostListAPIView, PostCreateAPIView, PostUpdateAPIView, PostRetrieveAPIView, PostDestroyAPIView

app_name = 'posts'

urlpatterns = [
    path("posts/", PostListAPIView.as_view(), name="posts_list"),
    path("posts/create/", PostCreateAPIView.as_view(), name="posts_create"),
    path(
        "posts/<int:pk>/update/", PostUpdateAPIView.as_view(), name="posts_update"
    ),
    path("posts/<int:pk>/", PostRetrieveAPIView.as_view(), name="posts_retrieve"),
    path(
        "posts/<int:pk>/delete/",
        PostDestroyAPIView.as_view(),
        name="posts_delete",
    ),
]

# urlpatterns += router.urls
