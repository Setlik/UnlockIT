# from django.utils import timezone
#
# from users.models import AuthorSubscription
#
#
# def deactivate_expired_subscriptions():
#     expired = AuthorSubscription.objects.filter(
#         expires_at__lte=timezone.now(),
#         is_active=True
#     )
#     for sub in expired:
#         sub.is_active = False
#         sub.save()
