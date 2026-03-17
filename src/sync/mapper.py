"""Notion -> Calendar mapping logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import Settings
from src.domain.models import CalendarEventPayload, NotionTask
from src.domain.validators import all_day_end, is_valid_email


def load_contacts(path: str) -> dict[str, str]:
    """Load contact mapping file."""
    file_path = Path(path)
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def _build_attendees(assignees: list[str], contacts: dict[str, str]) -> list[dict[str, str]]:
    attendees: list[dict[str, str]] = []
    for assignee in assignees:
        email = contacts.get(assignee)
        if email and is_valid_email(email):
            attendees.append({"email": email})
    return attendees


def map_task_to_event(
    task: NotionTask, settings: Settings, contacts: dict[str, str]
) -> CalendarEventPayload:
    """Map notion task to all-day calendar payload."""
    title = task.task_name
    if task.status.lower() == "done":
        title = f"✓ {title}"
    start_date = task.due_date.isoformat()
    end_date = all_day_end(task.due_date).isoformat()
    attendees = _build_attendees(task.assignees, contacts)
    return CalendarEventPayload(
        summary=title,
        start_date=start_date,
        end_date=end_date,
        timezone=settings.timezone,
        attendees=attendees,
    )


def summarize_event(payload: CalendarEventPayload) -> dict[str, Any]:
    """Utility to expose body fields for tests/contract checks."""
    return payload.to_api_body()
