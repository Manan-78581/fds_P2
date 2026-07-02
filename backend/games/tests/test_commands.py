from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone

from games.models import Game, GameKey, Publisher

User = get_user_model()


def test_check_expired_keys_marks_keys_and_enqueues_webhook(db):
    user = User.objects.create_user(username="publisher", password="Password123")
    publisher = Publisher.objects.create(
        user=user,
        name="Acme Studios",
        webhook_url="https://example.com/webhook",
        webhook_secret="supersecret",
    )
    game = Game.objects.create(title="Portal 3", publisher=publisher, price="29.99")
    key = GameKey.objects.create(
        key_string="PORTAL-3-KEY-EXPIRED",
        game=game,
        expires_at=timezone.now() - timedelta(minutes=1),
    )

    with patch("games.tasks.send_game_key_expired_webhook.delay") as mocked_delay:
        call_command("check_expired_keys")

    key.refresh_from_db()
    assert key.status == GameKey.STATUS_EXPIRED
    mocked_delay.assert_called_once_with(key.id)
