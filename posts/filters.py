import django_filters

from posts.models import Post, PostPurchase


class PaymentFilter(django_filters.FilterSet):
    post = django_filters.ModelChoiceFilter(queryset=Post.objects.all())
    payment_date = django_filters.DateFilter(field_name="payment_date")

    class Meta:
        model = PostPurchase
        fields = ["post", "payment_date"]
