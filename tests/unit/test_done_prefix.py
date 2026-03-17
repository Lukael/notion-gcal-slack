"""Unit tests for done status prefix."""

from datetime import date

from src.domain.models import NotionTask
from src.sync.mapper import map_task_to_event


def test_done_status_prefixes_title(settings):
    task = NotionTask(
        notion_page_id="done-1",
        task_name="Write docs",
        due_date=date(2026, 3, 18),
        status="Done",
        assignees=[],
        google_id="evt-2",
    )
    payload = map_task_to_event(task, settings, {})
    assert payload.summary == "✓ Write docs"
