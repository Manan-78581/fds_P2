import json
from urllib import error, request

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import GameKey, WebhookDeliveryLog
from .webhooks import build_expired_key_payload, sign_payload


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_game_key_expired_webhook(self, game_key_id: int) -> dict:
    game_key = GameKey.objects.select_related("game", "game__publisher").get(pk=game_key_id)
    payload = build_expired_key_payload(game_key)
    publisher = game_key.game.publisher
    signature = sign_payload(publisher.webhook_secret, payload)
    body = json.dumps(payload).encode("utf-8")

    req = request.Request(
        publisher.webhook_url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
        },
    )

    try:
        with request.urlopen(req, timeout=10) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            status = response.getcode()
            WebhookDeliveryLog.objects.create(
                publisher=publisher,
                game_key=game_key,
                event_type="game.key.expired",
                payload=payload,
                response_status=status,
                response_body=response_body,
                success=200 <= status < 300,
            )
            return {"status": status, "body": response_body}
    except error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        WebhookDeliveryLog.objects.create(
            publisher=publisher,
            game_key=game_key,
            event_type="game.key.expired",
            payload=payload,
            response_status=exc.code,
            response_body=response_body,
            success=False,
        )
        raise self.retry(exc=exc)
    except error.URLError as exc:
        WebhookDeliveryLog.objects.create(
            publisher=publisher,
            game_key=game_key,
            event_type="game.key.expired",
            payload=payload,
            response_status=None,
            response_body=str(exc),
            success=False,
        )
        raise self.retry(exc=exc)


def mark_key_expired(game_key: GameKey) -> None:
    with transaction.atomic():
        if game_key.status != GameKey.STATUS_EXPIRED:
            game_key.status = GameKey.STATUS_EXPIRED
            game_key.save(update_fields=["status"])
            send_game_key_expired_webhook.delay(game_key.id)
