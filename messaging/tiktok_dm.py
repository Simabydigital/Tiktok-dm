from __future__ import annotations
from .dm_interface import DMInterface

class TikTokDM(DMInterface):
    """Demo: fail the first attempt for each user, then succeed — to show retries/backoff."""
    def __init__(self) -> None:
        self._attempts_per_user: dict[str, int] = {}

    def send_message(self, to_user_id: str, text: str) -> bool:
        n = self._attempts_per_user.get(to_user_id, 0)
        if n < 1:  # make it < 2 if you want to see two retries
            self._attempts_per_user[to_user_id] = n + 1
            raise RuntimeError("Temporary network glitch (demo)")
        print(f"[SIMULATED SEND] -> {to_user_id}: {text}")
        return True
