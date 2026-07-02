from django.core.management.base import BaseCommand
from django.utils import timezone

from games.models import GameKey
from games.tasks import mark_key_expired


class Command(BaseCommand):
    help = "Detect expired keys and enqueue webhook notifications."

    def handle(self, *args, **options):
        expired_keys = GameKey.objects.select_related("game", "game__publisher").filter(
            status=GameKey.STATUS_ACTIVE,
            expires_at__lte=timezone.now(),
        )
        count = 0
        for game_key in expired_keys:
            mark_key_expired(game_key)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {count} expired key(s)."))
