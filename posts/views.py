import stripe
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from rest_framework.reverse import reverse_lazy

from posts.forms import PostCreateForm
from posts.models import Post


class HomeView(ListView):
    model = Post
    template_name = "posts/home.html"
    context_object_name = "posts"

    def get_queryset(self):
        username = self.kwargs.get("username")
        if username:
            self.current_user = get_user_model().objects.get(username=username)
        else:
            self.current_user = (
                self.request.user if self.request.user.is_authenticated else None
            )

        if self.current_user:
            return self.current_user.posts.all().order_by("-created_at")
        else:
            return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_users"] = get_user_model().objects.all().order_by("username")
        context["current_user"] = self.current_user
        if self.request.user.is_authenticated:
            context["username"] = self.request.user.username
            context["user_post_count"] = self.request.user.posts.count()
        else:
            context["username"] = None
            context["user_post_count"] = 0
        return context


class UserPostsView(ListView):
    template_name = "posts/user_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        user = get_object_or_404(get_user_model(), username=self.kwargs["username"])
        queryset = user.posts.all()

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(price_type="free")

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_users"] = get_user_model().objects.all().order_by("username")
        context["profile_user"] = get_object_or_404(
            get_user_model(), username=self.kwargs["username"]
        )
        context["is_owner"] = self.request.user == context["profile_user"]
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = "posts/create_post.html"
    success_message = "Публикация успешно создана!"

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_paid = form.cleaned_data["price_type"] == "paid"
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание публикации"
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = "posts/post_edit.html"
    success_message = "Публикация успешно обновлена!"

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.is_paid = form.cleaned_data["price_type"] == "paid"
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактирование: {self.object.title}"
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            messages.error(request, "Вы не можете редактировать эту публикацию")
            return redirect("posts:post_detail", pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("posts:home")
    success_message = "Публикация успешно удалена!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class PostBuyView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)

        if post.price_type != "paid":
            messages.error(request, "Этот пост не доступен для покупки.")
            return redirect("posts:user_posts", username=request.user.username)

        stripe_price_id = post.stripe_price_id
        if not stripe_price_id:
            messages.error(request, "Цена для этого поста не настроена.")
            return redirect("posts:user_posts", username=request.user.username)

        success_url = request.build_absolute_uri(
            reverse("payment_success") + f"?post_id={post.id}"
        )
        cancel_url = request.build_absolute_uri(
            reverse("payment_cancel") + f"?post_id={post.id}"
        )

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": stripe_price_id,
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "post_id": post.id,
                    "user_id": request.user.id,
                },
            )
        except Exception as e:
            messages.error(request, f"Ошибка при создании платежа: {e}")
            return redirect("posts:user_posts", username=request.user.username)

        return redirect(session.url)
