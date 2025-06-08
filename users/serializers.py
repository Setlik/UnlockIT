from rest_framework.serializers import ModelSerializer

from users.models import AuthorSubscription, User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class AuthorSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = AuthorSubscription
        fields = "__all__"
