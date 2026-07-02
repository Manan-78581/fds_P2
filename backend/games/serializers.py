from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Game, GameKey, Order, OrderItem, Publisher

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PublisherSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    game_count = serializers.SerializerMethodField()
    webhook_secret = serializers.CharField(write_only=True)

    def get_game_count(self, obj):
        return obj.games.count()

    class Meta:
        model = Publisher
        fields = ("id", "name", "webhook_url", "webhook_secret", "user", "game_count", "created_at")
        read_only_fields = ("created_at",)


class GameSerializer(serializers.ModelSerializer):
    publisher = serializers.SerializerMethodField()
    available_keys = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            "id",
            "title",
            "description",
            "publisher",
            "price",
            "is_active",
            "available_keys",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def get_publisher(self, obj):
        return {"id": obj.publisher_id, "name": obj.publisher.name}

    def get_available_keys(self, obj):
        return obj.keys.filter(status=GameKey.STATUS_ACTIVE, owner__isnull=True, expires_at__gt=timezone.now()).count()


class GameKeySerializer(serializers.ModelSerializer):
    game_title = serializers.ReadOnlyField(source="game.title")
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = GameKey
        fields = ("id", "key_string", "game", "game_title", "status", "expires_at", "owner", "purchased_at")
        read_only_fields = ("status", "owner", "purchased_at")


class OrderItemSerializer(serializers.ModelSerializer):
    game_title = serializers.ReadOnlyField(source="game.title")
    key_string = serializers.ReadOnlyField(source="game_key.key_string")

    class Meta:
        model = OrderItem
        fields = ("id", "game", "game_title", "game_key", "key_string", "price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Order
        fields = ("id", "user", "status", "total_amount", "created_at", "completed_at", "items")
        read_only_fields = ("status", "total_amount", "created_at", "completed_at", "items")


class OrderCreateSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()

    def create(self, validated_data):
        user = self.context["request"].user
        try:
            game = Game.objects.select_related("publisher").get(pk=validated_data["game_id"])
        except Game.DoesNotExist as exc:
            raise serializers.ValidationError({"game_id": "Game not found."}) from exc

        with transaction.atomic():
            key = (
                GameKey.objects.select_for_update()
                .select_related("game", "game__publisher")
                .filter(
                    game=game,
                    status=GameKey.STATUS_ACTIVE,
                    owner__isnull=True,
                    expires_at__gt=timezone.now(),
                )
                .order_by("expires_at", "id")
                .first()
            )
            if key is None:
                raise serializers.ValidationError({"game_id": "No active keys are available for this game."})

            order = Order.objects.create(user=user, status=Order.STATUS_COMPLETED, total_amount=game.price)
            key.owner = user
            key.status = GameKey.STATUS_SOLD
            key.purchased_at = timezone.now()
            key.save(update_fields=["owner", "status", "purchased_at"])
            OrderItem.objects.create(order=order, game=game, game_key=key, price=game.price)
            order.completed_at = timezone.now()
            order.save(update_fields=["completed_at"])
            return order
