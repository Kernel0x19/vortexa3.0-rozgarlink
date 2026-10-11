import enum
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    VOICE = "voice"


class NotificationType(str, enum.Enum):
    DEADLINE_REMINDER = "deadline_reminder"
    NEW_MATCH = "new_match"
    STATUS_UPDATE = "status_update"
    GENERAL = "general"


class NotificationService(ABC):
    @abstractmethod
    async def validate_recipient(self, recipient: str) -> bool:
        pass

    @abstractmethod
    async def send(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
        pass
