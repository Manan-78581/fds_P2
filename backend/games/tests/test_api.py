from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from games.models import Game, GameKey, Publisher

User = get_user_model()


def create_game_bundle():
    publisher_user = User.objects.create_user(username="publisher", password="Password123")
    publisher = Publisher.objects.create(
        user=publisher_user,
        name="Acme Studios",
        webhook_url="https://example.com/webhook",
        webhook_secret="supersecret",
    )
    game = Game.objects.create(title="Portal 3", publisher=publisher, price="29.99")
    key = GameKey.objects.create(
        key_string="PORTAL-3-KEY-001",
        game=game,
        expires_at=timezone.now() + timedelta(days=1),
    )
    return publisher_user, publisher, game, key


def test_register_endpoint_creates_user_and_token(db):
    client = APIClient()
    response = client.post(
        "/api/register/",
        {"username": "alice", "email": "alice@example.com", "password": "Password123"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["user"]["username"] == "alice"
    assert User.objects.filter(username="alice").exists()


def test_order_purchase_consumes_game_key(db):
    _, _, game, key = create_game_bundle()
    buyer = User.objects.create_user(username="buyer", password="Password123")
    client = APIClient()
    client.force_authenticate(user=buyer)

    response = client.post("/api/orders/", {"game_id": game.id}, format="json")

    assert response.status_code == 201
    assert response.data["items"][0]["key_string"] == key.key_string

    key.refresh_from_db()
    assert key.status == GameKey.STATUS_SOLD
    assert key.owner == buyer
