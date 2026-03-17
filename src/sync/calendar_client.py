"""Google Calendar API wrapper."""

# pylint: disable=no-member

from __future__ import annotations

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import Settings
from src.domain.models import CalendarEventPayload

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class EventNotFoundError(RuntimeError):
    """Raised when target Google Calendar event is missing."""


class CalendarGateway:
    """Encapsulates Google Calendar operations."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.service = self._build_service()

    def _build_service(self):
        creds = None
        if os.path.exists(self.settings.token_file):
            creds = Credentials.from_authorized_user_file(self.settings.token_file, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.settings.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(self.settings.token_file, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def create_event(self, payload: CalendarEventPayload) -> str:
        """Create event and return event id."""
        event = (
            self.service.events()
            .insert(calendarId=self.settings.gcal_calendar_id, body=payload.to_api_body())
            .execute()
        )
        return event["id"]

    def update_event(self, event_id: str, payload: CalendarEventPayload) -> None:
        """Patch existing event."""
        try:
            (
                self.service.events()
                .patch(
                    calendarId=self.settings.gcal_calendar_id,
                    eventId=event_id,
                    body=payload.to_api_body(),
                )
                .execute()
            )
        except HttpError as exc:
            if getattr(exc, "status_code", None) == 404 or "<HttpError 404" in str(exc):
                raise EventNotFoundError(str(exc)) from exc
            raise
