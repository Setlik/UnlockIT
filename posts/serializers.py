from rest_framework.serializers import ModelSerializer

from posts.models import Post, PostPurchase


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = "__all__"


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = PostPurchase
        fields = "__all__"
