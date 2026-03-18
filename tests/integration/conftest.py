"""Shared fixtures for integration tests."""

from datetime import date
import json

import pytest

from src.config import Settings
from src.domain.models import NotionTask
from src.sync.calendar_client import EventNotFoundError


class FakeNotionGateway:
    """In-memory Notion gateway."""

    def __init__(self, tasks):
        self._tasks = tasks
        self.updated_ids: list[tuple[str, str]] = []

    def query_tasks(self):
        return list(self._tasks)

    def update_google_id(self, page_id: str, google_id: str):
        self.updated_ids.append((page_id, google_id))


class FakeCalendarGateway:
    """In-memory calendar gateway."""

    def __init__(
        self,
        fail_on: set[str] | None = None,
        not_found_event_ids: set[str] | None = None,
    ):
        self.fail_on = fail_on or set()
        self.not_found_event_ids = not_found_event_ids or set()
        self.created: list[dict] = []
        self.updated: list[tuple[str, dict]] = []

    def create_event(self, payload):
        if payload.summary in self.fail_on:
            raise RuntimeError("forced create failure")
        self.created.append(payload.to_api_body())
        return f"evt-{len(self.created)}"

    def update_event(self, event_id: str, payload):
        if event_id in self.not_found_event_ids:
            raise EventNotFoundError(f"event not found: {event_id}")
        if payload.summary in self.fail_on:
            raise RuntimeError("forced update failure")
        self.updated.append((event_id, payload.to_api_body()))


@pytest.fixture
def notion_factory():
    """Factory for fake notion gateway."""
    return lambda tasks: FakeNotionGateway(tasks)


@pytest.fixture
def calendar_factory():
    """Factory for fake calendar gateway."""
    return lambda fail_on=None, not_found_event_ids=None: FakeCalendarGateway(
        fail_on=fail_on,
        not_found_event_ids=not_found_event_ids,
    )


@pytest.fixture
def settings(tmp_path):
    """Provide explicit settings for tests."""
    contacts = {"Alice": "alice@example.com", "Bob": "not-an-email"}
    contact_path = tmp_path / "contact.json"
    contact_path.write_text(json.dumps(contacts), encoding="utf-8")
    return Settings(
        notion_token="test-token",
        notion_database_id="test-db",
        gcal_calendar_id="primary",
        timezone="Asia/Seoul",
        contact_file=str(contact_path),
        dry_run=False,
    )


@pytest.fixture
def sample_create_task():
    return NotionTask(
        notion_page_id="page-1",
        task_name="Write spec",
        due_date=date(2026, 3, 17),
        status="Todo",
        assignees=["Alice", "Bob"],
        google_id=None,
    )


@pytest.fixture
def sample_update_task():
    return NotionTask(
        notion_page_id="page-2",
        task_name="Review PR",
        due_date=date(2026, 3, 18),
        status="Done",
        assignees=["Alice"],
        google_id="evt-abc",
    )
