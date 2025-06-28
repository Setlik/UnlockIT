import time

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.generics import get_object_or_404

from users.forms import PhoneLoginForm, UserRegistrationForm
from users.management.commands.sms_auth import send_verification_code
from users.models import AuthorSubscription, User

verification_codes = {}
registration_sessions = {}
stripe.api_key = settings.STRIPE_API_KEY

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            code = send_verification_code(phone)
            if code:
                registration_sessions[phone] = {
                    "password": form.cleaned_data["password"],
                    "username": form.cleaned_data["username"],
                    "email": form.cleaned_data["email"],
                    "created_at": time.time(),
                }
                verification_codes[phone] = str(code)
                return redirect("users:confirm_code", phone=phone)
            else:
                messages.error(request, "Не удалось отправить код. Попробуйте позже.")
        else:
            print("Errors in registration form:", form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def confirm_code(request, phone):
    if request.method == "POST":
        input_code = request.POST.get("code")
        real_code = verification_codes.get(phone)

        if not real_code:
            messages.error(request, "Время действия кода истек или код не найден.")
            return redirect("users:register")

        if input_code == real_code:
            data = registration_sessions.get(phone)
            if data:
                user = User(
                    username=data["username"],
                    email=data["email"],
                    phone_number=phone,
                )
                user.set_password(data["password"])
                user.is_active = True
                user.save()

                verification_codes.pop(phone, None)
                registration_sessions.pop(phone, None)

                messages.success(request, "Вы успешно зарегистрированы!")
                return redirect("users:login")
            else:
                messages.error(request, "Данные регистрации не найдены.")
        else:
            messages.error(request, "Неверный код подтверждения.")
    return render(request, "users/confirm_code.html", {"phone": phone})


def login_view(request):
    if request.method == "POST":
        form = PhoneLoginForm(request, data=request.POST)
        if form.is_valid():
            print("Form errors:", form.errors)
            user = form.get_user()
            if user:
                login(request, user)
                return redirect("posts:home")
            else:
                messages.error(request, "Неверный телефон или пароль.")
        else:
            messages.error(request, "Проверьте правильность данных.")
    else:
        form = PhoneLoginForm()
    return render(request, "users/login.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("posts:home")


class SubscriptionPaymentView(View):
    def get(self, request, author_pk):
        author = get_object_or_404(get_user_model(), pk=author_pk)
        context = {
            "author": author,
            "subscription_exists": AuthorSubscription.objects.filter(
                subscriber=request.user, author=author, is_active=True
            ).exists(),
        }
        return render(request, "subscription/subscription_payment.html", context)

    def post(self, request, author_pk):
        author = get_object_or_404(get_user_model(), pk=author_pk)
        amount = 1000

        if AuthorSubscription.objects.filter(
            subscriber=request.user, author=author, is_active=True
        ).exists():
            return redirect("some_existing_subscription_page")

        product = stripe.Product.create(name=f"Подписка на {author.username}")
        price = stripe.Price.create(
            currency="rub",
            unit_amount=amount * 100,
            product=product.id,
            recurring={"interval": "month"},
        )

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price.id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=request.build_absolute_uri(
                f"/users/subscription/success/{author.pk}/"
            ),
            cancel_url=request.build_absolute_uri(
                f"/users/subscription/cancel/{author.pk}/"
            ),
            metadata={
                "subscriber_id": request.user.pk,
                "author_id": author.pk,
                "amount": amount,
            },
        )

        # subscription = AuthorSubscription.objects.create(
        #     subscriber=request.user,
        #     author=author,
        #     amount=amount,
        #     is_active=False,
        #     session_id=session.id,
        #     payment_link=session.url,
        # )
        return redirect(session.url)


class SubscriptionSuccessView(View):
    def get(self, request, author_pk):
        author = get_object_or_404(get_user_model(), pk=author_pk)

        subscription = AuthorSubscription.objects.filter(
            subscriber=request.user,
            author=author,
            session_id=request.GET.get("session_id"),
        ).first()

        if subscription:
            subscription.is_active = True
            subscription.save()

        return render(
            request, "subscription/subscription_success.html", {"author": author}
        )


class SubscriptionCancelView(View):
    def get(self, request, author_pk):
        author = get_object_or_404(get_user_model(), pk=author_pk)
        return render(
            request, "subscription/subscription_cancel.html", {"author": author}
        )
