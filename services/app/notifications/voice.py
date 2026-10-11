from typing import Dict, Any
from app.notifications.service import NotificationService


class VoiceNotificationService(NotificationService):
    """Automated voice call alert service."""

    async def validate_recipient(self, recipient: str) -> bool:
        return bool(recipient and isinstance(recipient, str))

    async def send(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "call_sid": "mock-call-sid"}
