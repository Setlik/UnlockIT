import django_filters

from academy.models import Course, Lesson
from users.models import Payment


class PaymentFilter(django_filters.FilterSet):
    course = django_filters.ModelChoiceFilter(queryset=Course.objects.all())
    lesson = django_filters.ModelChoiceFilter(queryset=Lesson.objects.all())
    payment_method = django_filters.CharFilter(
        field_name="payment_method", lookup_expr="icontains"
    )
    payment_date = django_filters.DateFilter(field_name="payment_date")

    class Meta:
        model = Payment
        fields = ["course", "lesson", "payment_method", "payment_date"]
