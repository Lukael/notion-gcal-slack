"""Performance validation scenario."""

from datetime import date
import time

from src.domain.models import NotionTask
from src.sync.orchestrator import SyncOrchestrator


def test_500_items_under_60_seconds(settings, notion_factory, calendar_factory):
    tasks = [
        NotionTask(
            notion_page_id=f"p-{idx}",
            task_name=f"Task {idx}",
            due_date=date(2026, 3, 17),
            status="Todo",
            assignees=[],
            google_id=None,
        )
        for idx in range(500)
    ]
    notion = notion_factory(tasks)
    calendar = calendar_factory()
    orchestrator = SyncOrchestrator(settings, notion_gateway=notion, calendar_gateway=calendar)

    started = time.perf_counter()
    result = orchestrator.run_once()
    elapsed = time.perf_counter() - started

    assert result.created_count == 500
    assert result.failed_count == 0
    assert elapsed < 60
