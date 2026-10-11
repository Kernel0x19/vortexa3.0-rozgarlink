import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.notifications.service import NotificationService
from app.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceNotificationService(NotificationService):
    """Automated voice call alert service."""

    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None, from_phone: Optional[str] = None):
        self.account_sid = account_sid or getattr(settings, "twilio_account_sid", None)
        self.auth_token = auth_token or getattr(settings, "twilio_auth_token", None)
        self.from_phone = from_phone or getattr(settings, "twilio_from_phone", None)

    async def validate_recipient(self, recipient: str) -> bool:
        return bool(recipient and isinstance(recipient, str))

    async def send(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
        if not await self.validate_recipient(recipient):
            return {"success": False, "error": f"Invalid phone number format: {recipient}"}
        if not (self.account_sid and self.auth_token and self.from_phone):
            logger.info("[DEV] Voice call simulated to %s", recipient)
            return {"success": True, "call_sid": f"dev-call-{int(datetime.utcnow().timestamp())}", "provider": "development_mock"}
        try:
            from twilio.rest import Client
            call = Client(self.account_sid, self.auth_token).calls.create(
                to=recipient,
                from_=self.from_phone,
                twiml=f"<Response><Say voice=\"alice\" language=\"en-IN\">{message.get('body', 'RozgarLink deadline reminder.')}</Say></Response>",
            )
            return {"success": True, "call_sid": call.sid, "provider": "twilio", "status": call.status}
        except Exception as exc:
            logger.exception("Voice call delivery failed for %s", recipient)
            return {"success": False, "error": str(exc)}
