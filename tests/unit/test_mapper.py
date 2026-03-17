"""Unit tests for mapping logic."""

from datetime import date

from src.domain.models import NotionTask
from src.sync.mapper import map_task_to_event


def test_map_task_to_all_day_payload(settings):
    task = NotionTask(
        notion_page_id="p1",
        task_name="Prepare demo",
        due_date=date(2026, 3, 17),
        status="Todo",
        assignees=["Alice"],
        google_id=None,
    )
    payload = map_task_to_event(task, settings, {"Alice": "alice@example.com"})
    body = payload.to_api_body()
    assert body["start"]["date"] == "2026-03-17"
    assert body["end"]["date"] == "2026-03-18"
    assert body["attendees"] == [{"email": "alice@example.com"}]


def test_map_task_done_prefix(settings):
    task = NotionTask(
        notion_page_id="p2",
        task_name="Close ticket",
        due_date=date(2026, 3, 17),
        status="Done",
        assignees=[],
        google_id="evt-1",
    )
    payload = map_task_to_event(task, settings, {})
    assert payload.summary.startswith("✓ ")


def test_map_task_skips_invalid_attendee_email(settings):
    task = NotionTask(
        notion_page_id="p3",
        task_name="Sync notes",
        due_date=date(2026, 3, 17),
        status="Todo",
        assignees=["Bob"],
        google_id=None,
    )
    payload = map_task_to_event(task, settings, {"Bob": "invalid-email"})
    assert payload.attendees == []
