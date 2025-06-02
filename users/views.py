import time
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views import View

from users.forms import UserRegistrationForm, PhoneLoginForm
from users.management.commands.sms_auth import send_verification_code
from users.models import User


verification_codes = {}
registration_sessions = {}

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            # Генерируем и отправляем код
            code = send_verification_code(phone)
            if code:
                # Сохраняем данные до подтверждения
                registration_sessions[phone] = {
                    'password': form.cleaned_data['password'],
                    'username': form.cleaned_data['username'],
                    'email': form.cleaned_data['email'],
                    'created_at': time.time()
                }
                verification_codes[phone] = str(code)
                return redirect('users:confirm_code', phone=phone)
            else:
                messages.error(request, "Не удалось отправить код. Попробуйте позже.")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def confirm_code(request, phone):
    if request.method == "POST":
        input_code = request.POST.get('code')
        real_code = verification_codes.get(phone)

        if not real_code:
            messages.error(request, "Время действия кода истек или код не найден.")
            return redirect('users:register')

        if input_code == real_code:
            data = registration_sessions.get(phone)
            if data:
                user = User(
                    username=data['username'],
                    email=data['email'],
                    phone_number=phone,
                )
                user.set_password(data['password'])
                user.is_active = True
                user.save()

                # Очистить временные данные
                verification_codes.pop(phone, None)
                registration_sessions.pop(phone, None)

                messages.success(request, "Вы успешно зарегистрированы!")
                return redirect('users:login')
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
                return redirect("home")
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
        return redirect("home")
