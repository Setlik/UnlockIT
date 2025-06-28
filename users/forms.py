import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError

from .models import User


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label="Никнейм",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите свой никнейм", "class": "form-control"}
        ),
    )
    password = forms.CharField(
        label="Введите пароль",
        widget=forms.PasswordInput(
            attrs={"placeholder": "Введите пароль", "class": "form-control"}
        ),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Подтвердите свой пароль", "class": "form-control"}
        ),
        label="Подтвердите пароль",
    )
    phone_number = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Введите номер в формате +7XXXXXXXXXX",
                "class": "form-control",
            }
        ),
        validators=[
            RegexValidator(
                regex=r"^\+?7\d{10}$",
                message="Введите номер в формате +7XXXXXXXXXX",
                code="invalid_phone_number",
            )
        ],
    )
    email = forms.EmailField(
        label="Почта",
        widget=forms.EmailInput(
            attrs={"placeholder": "Введите вашу почту", "class": "form-control"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "phone_number", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if not re.match(r"^\+?7\d{10}$", phone_number):
            raise ValidationError("Введите номер в формате +7XXXXXXXXXX")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError("Пароли не совпадают")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class PhoneLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(
            attrs={"placeholder": "Введите номер в формате +7XXXXXXXXXX"}
        ),
        validators=[
            RegexValidator(
                regex=r"^\+?7\d{10}$",
                message="Введите номер в формате +7XXXXXXXXXX",
                code="invalid_phone_number",
            )
        ],
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.TextInput(attrs={"placeholder": "Введите свой пароль"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
