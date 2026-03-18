"""Notion API wrapper."""

from __future__ import annotations

import time
from typing import Any

from notion_client import Client as NotionClient

from src.config import Settings
from src.domain.models import NotionTask
from src.domain.validators import parse_notion_date


class NotionGateway:
    """Encapsulates Notion data-source operations."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = NotionClient(auth=settings.notion_token)

    def _retry(self, operation):  # pylint: disable=broad-exception-caught
        last_error = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                return operation()
            except Exception as exc:  # pylint: disable=broad-exception-caught  # pragma: no cover
                last_error = exc
                message = str(exc).lower()
                retriable = "rate limit" in message or "429" in message
                if not retriable or attempt >= self.settings.max_retries:
                    raise
                sleep_for = self.settings.retry_base_seconds * (2**attempt)
                time.sleep(sleep_for)
        raise RuntimeError("Retry failed unexpectedly") from last_error

    def query_tasks(self) -> list[NotionTask]:
        """Load all sync-target tasks with pagination."""
        results: list[dict[str, Any]] = []
        cursor = None

        while True:
            payload = {
                "data_source_id": self.settings.notion_database_id,
                "filter": {
                    "and": [
                        {"property": "Due Date", "date": {"is_not_empty": True}},
                    ]
                },
                "page_size": self.settings.page_size,
            }
            if cursor:
                payload["start_cursor"] = cursor
            resp = self._retry(lambda: self.client.data_sources.query(**payload))
            results.extend(resp.get("results", []))
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")

        return [self._to_task(page) for page in results if self._has_due_date(page)]

    def _has_due_date(self, page: dict[str, Any]) -> bool:
        date_prop = page.get("properties", {}).get("Due Date", {})
        return bool(date_prop.get("date", {}).get("start"))

    def _to_task(self, page: dict[str, Any]) -> NotionTask:
        props = page["properties"]
        title = "".join(x.get("plain_text", "") for x in props["Task Name"]["title"]).strip()
        due_start = props["Due Date"]["date"]["start"]
        status = (props.get("Status", {}).get("select") or {}).get("name", "Todo")
        assignees_prop = props.get("Assignees", {}).get("multi_select", [])
        assignees = [x.get("name", "") for x in assignees_prop if x.get("name")]
        google_id_text = props.get("Google ID", {}).get("rich_text", [])
        google_id = "".join(x.get("plain_text", "") for x in google_id_text).strip() or None
        return NotionTask(
            notion_page_id=page["id"],
            task_name=title or "(No title)",
            due_date=parse_notion_date(due_start, self.settings.timezone),
            status=status,
            assignees=assignees,
            google_id=google_id,
        )

    def update_google_id(self, page_id: str, google_id: str) -> None:
        """Persist Google event ID to Notion."""
        self._retry(
            lambda: self.client.pages.update(
                page_id=page_id,
                properties={
                    "Google ID": {"rich_text": [{"type": "text", "text": {"content": google_id}}]}
                },
            )
        )
