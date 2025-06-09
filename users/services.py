import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product():
    """Создает продукт для оплаты в stripe."""

    product = stripe.Product.create(name="Подписка на пользователя")
    return product.id


def create_stripe_product_price(amount, product_id):
    """Создает цену на продукт для оплаты в stripe."""

    price = stripe.Price.create(
        currency="rub",
        unit_amount=amount * 100,
        product=product_id,
    )
    return price.id


def create_stripe_sessions(price_id):
    """Создает сессию на оплату продукта в stripe."""

    session = stripe.checkout.Session.create(
        success_url="https://127.0.0.1:8000/",
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
    )
    return session.get("id"), session.get("url")
