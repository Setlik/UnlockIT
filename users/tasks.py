from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER

from .models import Course, Subscription

User = get_user_model()


@shared_task
def send_course_update_email(course_id):
    """Отправляет письмо пользователю подписанного на курс информацию об обновлении."""
    course = Course.objects.get(id=course_id)
    subscriptions = Subscription.objects.filter(course=course)

    email_list = [subs.user.email for subs in subscriptions if subs.user.email]

    if email_list:
        subject = f"Обновление курса: {course.title}"
        message = f"Курс {course.title} обновлён! Проверьте новые материалы."
        send_mail(subject, message, EMAIL_HOST_USER, email_list)


@shared_task
def deactivate_inactive_users():
    """Деактивирует пользователей, которые не заходили более месяца."""
    one_month_ago = timezone.now() - timezone.timedelta(days=30)
    users_to_deactivate = User.objects.filter(
        last_login__lt=one_month_ago, is_active=True
    )

    if users_to_deactivate.exists():
        users_to_deactivate.update(is_active=False)
        print(f"Deactivated {users_to_deactivate.count()} users.")
    else:
        print("No inactive users to deactivate.")
