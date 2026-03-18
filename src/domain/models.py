"""Domain models for sync flow."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(slots=True)
class NotionTask:
    """Normalized Notion task data."""

    notion_page_id: str
    task_name: str
    due_date: date
    status: str
    assignees: list[str]
    google_id: str | None = None


@dataclass(slots=True)
class CalendarEventPayload:
    """Calendar event payload for create/update."""

    summary: str
    start_date: str
    end_date: str
    timezone: str
    attendees: list[dict[str, str]] = field(default_factory=list)

    def to_api_body(self) -> dict[str, Any]:
        """Convert to Google Calendar API body."""
        body: dict[str, Any] = {
            "summary": self.summary,
            "start": {"date": self.start_date, "timeZone": self.timezone},
            "end": {"date": self.end_date, "timeZone": self.timezone},
        }
        if self.attendees:
            body["attendees"] = self.attendees
        return body


@dataclass(slots=True)
class FailureRecord:
    """Per-item error for resilient sync."""

    notion_page_id: str
    operation: str
    error_message: str
    retry_eligible: bool = True
    error_code: str | None = None


@dataclass(slots=True)
class SyncRun:  # pylint: disable=too-many-instance-attributes
    """Single run aggregation."""

    run_id: str
    started_at: datetime
    total_items: int = 0
    created_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    failure_items: list[FailureRecord] = field(default_factory=list)


@dataclass(slots=True)
class LoopRunRecord:  # pylint: disable=too-many-instance-attributes
    """One scheduler cycle metadata."""

    run_id: str
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    status: str
    created_count: int = 0
    updated_count: int = 0
    failed_count: int = 0
    next_run_at: datetime | None = None


@dataclass(slots=True)
class ShutdownState:
    """Signal/shutdown lifecycle state."""

    signal_received: bool = False
    signal_name: str | None = None
    received_at: datetime | None = None
    safe_to_exit: bool = False
