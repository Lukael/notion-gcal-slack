"""Unit tests for Calendar gateway."""

from src.config import Settings
from src.domain.models import CalendarEventPayload
from src.sync.calendar_client import CalendarGateway


class _FakeEvents:
    def __init__(self):
        self._created = []
        self._updated = []

    def insert(self, **kwargs):
        self._created.append(kwargs)
        return self

    def patch(self, **kwargs):
        self._updated.append(kwargs)
        return self

    def execute(self):
        if self._created:
            return {"id": "evt-created"}
        return {"id": "evt-updated"}


class _FakeService:
    def __init__(self):
        self._events = _FakeEvents()

    def events(self):
        return self._events


def test_create_and_update_event(monkeypatch, tmp_path):
    settings = Settings(
        notion_token="token",
        notion_database_id="db",
        token_file=str(tmp_path / "token.json"),
        credentials_file=str(tmp_path / "credentials.json"),
    )
    monkeypatch.setattr(CalendarGateway, "_build_service", lambda self: _FakeService())
    gateway = CalendarGateway(settings)
    payload = CalendarEventPayload(
        summary="Task",
        start_date="2026-03-17",
        end_date="2026-03-18",
        timezone="Asia/Seoul",
    )

    event_id = gateway.create_event(payload)
    gateway.update_event("evt-created", payload)

    assert event_id == "evt-created"
