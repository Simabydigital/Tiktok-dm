from abc import ABC, abstractmethod
class DMInterface(ABC):
    @abstractmethod
    def send_message(self, to_user_id: str, text: str) -> bool: ...
