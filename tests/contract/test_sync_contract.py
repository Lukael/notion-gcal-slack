"""Contract tests for sync service interfaces."""

from datetime import date

from src.domain.models import CalendarEventPayload, FailureRecord, NotionTask
from src.sync.mapper import summarize_event


def test_create_path_contract_shape():
    """Create payload must expose required fields."""
    payload = CalendarEventPayload(
        summary="Task",
        start_date="2026-03-17",
        end_date="2026-03-18",
        timezone="Asia/Seoul",
        attendees=[{"email": "alice@example.com"}],
    )
    body = summarize_event(payload)
    assert body["summary"] == "Task"
    assert body["start"]["date"] == "2026-03-17"
    assert body["end"]["date"] == "2026-03-18"
    assert body["attendees"][0]["email"] == "alice@example.com"


def test_update_path_contract_shape():
    """Update contract uses existing Google event id."""
    task = NotionTask(
        notion_page_id="page",
        task_name="Review",
        due_date=date(2026, 3, 17),
        status="Done",
        assignees=[],
        google_id="evt-1",
    )
    assert task.google_id == "evt-1"


def test_error_record_schema_contract():
    """Failure records include mandatory fields from contract."""
    failure = FailureRecord(
        notion_page_id="page-1",
        operation="create",
        error_message="boom",
        retry_eligible=True,
    )
    assert failure.notion_page_id
    assert failure.operation in {"create", "update", "map_attendees"}
    assert failure.error_message
    assert isinstance(failure.retry_eligible, bool)
    assert failure.retry_eligible is True
