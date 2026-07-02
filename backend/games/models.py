from django.conf import settings
from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    webhook_url = models.URLField()
    webhook_secret = models.CharField(max_length=128)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="publisher",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="games",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class GameKey(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SOLD = "sold"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_SOLD, "Sold"),
        (STATUS_EXPIRED, "Expired"),
    ]

    key_string = models.CharField(max_length=80, unique=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="keys")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    expires_at = models.DateTimeField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="game_keys",
    )
    purchased_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.key_string


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Order #{self.pk or 'new'}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    game_key = models.OneToOneField(GameKey, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.game.title} in order {self.order_id}"


class WebhookDeliveryLog(models.Model):
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name="webhook_logs")
    game_key = models.ForeignKey(GameKey, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=64)
    payload = models.JSONField()
    response_status = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    attempt = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.event_type} -> {self.publisher.name}"
