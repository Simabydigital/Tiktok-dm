from .dm_interface import DMInterface
class TikTokDM(DMInterface):
    """Stub only — implement with official, compliant API later."""
    def send_message(self, to_user_id: str, text: str) -> bool:
        print(f"[SIMULATED SEND] -> {to_user_id}: {text}")
        return True
