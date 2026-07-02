import hashlib
import hmac
import json

from .models import GameKey


def build_expired_key_payload(game_key: GameKey) -> dict:
    return {
        "event": "game.key.expired",
        "game_key": {
            "id": game_key.id,
            "key_string": game_key.key_string,
            "status": game_key.status,
            "expires_at": game_key.expires_at.isoformat(),
        },
        "game": {
            "id": game_key.game_id,
            "title": game_key.game.title,
        },
        "publisher": {
            "id": game_key.game.publisher_id,
            "name": game_key.game.publisher.name,
            "webhook_url": game_key.game.publisher.webhook_url,
        },
    }


def sign_payload(secret: str, payload: dict) -> str:
    message = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256)
    return digest.hexdigest()
