"""Focused verification for the 7-day and 2-day deadline notification flow.

Run with: ``venv\\Scripts\\python.exe -m unittest services.tests.test_deadline_notifications``
All providers are mocked, so this never sends a real email, SMS, or call.
"""

import asyncio
import os
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import AsyncMock

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# These values stay in services/.env, which is excluded from Git.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from app.agents.hackathon import HackathonAgent
from app.agents.internship import InternshipAgent
from app.db.models import (
    Application,
    Hackathon,
    HackathonSubscription,
    Notification,
    NotificationHistory,
    NotificationPreference,
    Opportunity,
    OpportunityCategory,
    User,
)
from app.db.session import Base
from app.notifications.email import EmailNotificationService
from app.notifications.orchestrator import NotificationOrchestrator
from app.notifications.service import NotificationType
from app.notifications.sms import SMSNotificationService
from app.notifications.voice import VoiceNotificationService


class DeadlineNotificationTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.user = User(email="student@example.com", phone_number="+919999999999")
        self.db.add(self.user)
        self.db.flush()
        self.db.add(NotificationPreference(
            user_id=self.user.id, email_enabled=True, sms_enabled=True,
            push_enabled=False, voice_enabled=True, deadline_reminders=True,
        ))
        self.db.commit()

    def _orchestrator(self):
        orchestrator = NotificationOrchestrator(self.db)
        orchestrator.email_service.send = AsyncMock(return_value={"success": True})
        orchestrator.sms_service.send = AsyncMock(return_value={"success": True})
        orchestrator.voice_service.send = AsyncMock(return_value={"success": True})
        return orchestrator

    def test_seven_day_uses_email_sms_and_two_day_adds_voice(self):
        seven_day = self._orchestrator()
        asyncio.run(seven_day.send_notification(
            self.user.id, NotificationType.DEADLINE_REMINDER,
            "Internship deadline in 7 days", "Prepare your application.", include_voice=False,
        ))
        self.assertEqual(seven_day.voice_service.send.await_count, 0)
        self.assertEqual(seven_day.email_service.send.await_count, 1)
        self.assertEqual(seven_day.sms_service.send.await_count, 1)

        two_day = self._orchestrator()
        asyncio.run(two_day.send_notification(
            self.user.id, NotificationType.DEADLINE_REMINDER,
            "Hackathon deadline in 2 days", "Register now.", include_voice=True,
        ))
        self.assertEqual(two_day.voice_service.send.await_count, 1)
        self.assertEqual(self.db.query(Notification).count(), 2)
        self.assertEqual(self.db.query(NotificationHistory).count(), 7)

    def test_agents_select_only_tracked_items_at_seven_or_two_days(self):
        internship = Opportunity(
            source="test", external_id="internship-1", category=OpportunityCategory.INTERNSHIP,
            title="Backend Internship", deadline=date.today() + timedelta(days=7),
        )
        hackathon = Hackathon(
            source="test", external_id="hackathon-1", title="AI Challenge",
            registration_deadline=date.today() + timedelta(days=2),
        )
        self.db.add_all([internship, hackathon])
        self.db.flush()
        self.db.add_all([
            Application(user_id=self.user.id, opportunity_id=internship.id, saved=True),
            HackathonSubscription(user_id=self.user.id, hackathon_id=hackathon.id),
        ])
        self.db.commit()

        calls = []

        async def record_send(_self, **kwargs):
            calls.append(kwargs)
            self.db.add(Notification(user_id=kwargs["user_id"], title=kwargs["title"], body=kwargs["body"]))
            self.db.commit()
            return {"channels_attempted": []}

        original = NotificationOrchestrator.send_notification
        NotificationOrchestrator.send_notification = record_send
        try:
            self.assertEqual(InternshipAgent().scan_deadlines(self.db), 1)
            self.assertEqual(HackathonAgent().scan_deadlines(self.db), 1)
        finally:
            NotificationOrchestrator.send_notification = original

        self.assertEqual({call["metadata"]["kind"] for call in calls}, {"internship", "hackathon"})
        self.assertEqual({call["include_voice"] for call in calls}, {False, True})

    @unittest.skipUnless(
        os.getenv("RUN_LIVE_NOTIFICATION_SMOKE_TEST", "false").lower() == "true",
        "Set RUN_LIVE_NOTIFICATION_SMOKE_TEST=true in services/.env to contact the configured test recipient.",
    )
    def test_live_email_sms_and_voice_delivery(self):
        """Opt-in provider smoke test; this deliberately contacts the configured recipient."""
        email = os.environ["NOTIFICATION_TEST_EMAIL"]
        phone = os.environ["NOTIFICATION_TEST_PHONE"]

        email_result = asyncio.run(EmailNotificationService().send(email, {
            "subject": "RozgarLink notification test",
            "body": "This is a test email from the RozgarLink notification service.",
        }))
        sms_result = asyncio.run(SMSNotificationService().send(phone, {
            "body": "RozgarLink notification test: SMS delivery is working.",
        }))
        voice_result = asyncio.run(VoiceNotificationService().send(phone, {
            "body": "This is a RozgarLink notification test call. Your deadline alerts are working.",
        }))

        self.assertTrue(email_result["success"], email_result)
        self.assertTrue(sms_result["success"], sms_result)
        self.assertTrue(voice_result["success"], voice_result)


if __name__ == "__main__":
    unittest.main()
