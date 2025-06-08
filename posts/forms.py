from django import forms

from .models import Post


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "price_type", "price"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок публикации",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Введите описание публикации",
                }
            ),
            "price_type": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": 1.0}
            ),
        }
        labels = {
            "title": "Заголовок публикации",
            "content": "Описание публикации",
            "price_type": "Тип доступа",
            "price": "Цена (только для платной публикации)",
        }
        help_texts = {
            "price": "Укажите цену, если публикация платная (для бесплатных оставьте 0)"
        }

    def clean(self):
        cleaned_data = super().clean()
        price_type = cleaned_data.get("price_type")
        price = cleaned_data.get("price")

        if price_type == "paid" and price <= 0:
            raise forms.ValidationError("Для платной публикации укажите цену больше 0")

        if price_type != "paid" and price > 0:
            raise forms.ValidationError(
                "Для бесплатной публикации или публикации по подписке цена должна быть 0"
            )

        return cleaned_data
