"""Sync orchestrator with failure isolation."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

from src.config import Settings
from src.domain.models import FailureRecord, SyncRun
from src.sync.calendar_client import CalendarGateway, EventNotFoundError
from src.sync.mapper import load_contacts, map_task_to_event
from src.sync.notion_client import NotionGateway


class SyncOrchestrator:  # pylint: disable=too-few-public-methods
    """Coordinates end-to-end sync."""

    def __init__(
        self,
        settings: Settings,
        notion_gateway: NotionGateway | None = None,
        calendar_gateway: CalendarGateway | None = None,
    ):
        self.settings = settings
        self.notion = notion_gateway or NotionGateway(settings)
        self.calendar = calendar_gateway or CalendarGateway(settings)

    def run_once(self) -> SyncRun:
        """Execute one sync cycle."""
        sync_run = SyncRun(run_id=str(uuid4()), started_at=datetime.now(timezone.utc))
        contacts = load_contacts(self.settings.contact_file)
        tasks = self.notion.query_tasks()
        sync_run.total_items = len(tasks)

        for task in tasks:
            payload = map_task_to_event(task, self.settings, contacts)
            operation = "create" if not task.google_id else "update"
            try:
                if self.settings.dry_run:
                    sync_run.skipped_count += 1
                    continue
                if not task.google_id:
                    event_id = self.calendar.create_event(payload)
                    self.notion.update_google_id(task.notion_page_id, event_id)
                    sync_run.created_count += 1
                else:
                    try:
                        self.calendar.update_event(task.google_id, payload)
                    except EventNotFoundError:
                        # Stale Google ID: recreate and overwrite Notion link.
                        recreated_id = self.calendar.create_event(payload)
                        self.notion.update_google_id(task.notion_page_id, recreated_id)
                    sync_run.updated_count += 1
            except Exception as exc:  # pylint: disable=broad-exception-caught  # pragma: no cover
                sync_run.failed_count += 1
                sync_run.failure_items.append(
                    FailureRecord(
                        notion_page_id=task.notion_page_id,
                        operation=operation,
                        error_message=str(exc),
                        retry_eligible=True,
                    )
                )
        return sync_run


def run_to_dict(settings: Settings) -> dict:
    """Convenience helper for CLI/tests."""
    result = SyncOrchestrator(settings).run_once()
    data = asdict(result)
    data["started_at"] = result.started_at.isoformat()
    return data
