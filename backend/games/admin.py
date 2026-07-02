from django.contrib import admin

from .models import Game, GameKey, Order, OrderItem, Publisher, WebhookDeliveryLog


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "webhook_url", "created_at")
    search_fields = ("name", "user__username")


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("title", "publisher", "price", "is_active", "created_at")
    list_filter = ("is_active", "publisher")
    search_fields = ("title",)


@admin.register(GameKey)
class GameKeyAdmin(admin.ModelAdmin):
    list_display = ("key_string", "game", "status", "owner", "expires_at")
    list_filter = ("status",)
    search_fields = ("key_string",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "game", "game_key", "price")


@admin.register(WebhookDeliveryLog)
class WebhookDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "publisher", "success", "response_status", "attempt", "created_at")
    list_filter = ("success", "event_type")
