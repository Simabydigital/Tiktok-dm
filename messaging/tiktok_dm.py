from __future__ import annotations
import random
from .dm_interface import DMInterface

class TikTokDM(DMInterface):
    def send_message(self, to_user_id: str, text: str) -> bool:
        # 50% chance to simulate a temporary glitch
        if random.random() < 0.5:
            raise RuntimeError("Temporary network glitch")
        print(f"[SIMULATED SEND] -> {to_user_id}: {text}")
        return True
