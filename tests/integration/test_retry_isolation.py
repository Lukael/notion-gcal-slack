"""Integration test for failure isolation and retry behavior."""

from datetime import date

from src.domain.models import NotionTask
from src.sync.orchestrator import SyncOrchestrator


def test_item_failure_does_not_stop_whole_run(settings, notion_factory, calendar_factory):
    failing = NotionTask(
        notion_page_id="p-fail",
        task_name="Fail item",
        due_date=date(2026, 3, 17),
        status="Todo",
        assignees=[],
        google_id=None,
    )
    success = NotionTask(
        notion_page_id="p-ok",
        task_name="Success item",
        due_date=date(2026, 3, 17),
        status="Todo",
        assignees=[],
        google_id=None,
    )
    notion = notion_factory([failing, success])
    calendar = calendar_factory(fail_on={"Fail item"})
    orchestrator = SyncOrchestrator(settings, notion_gateway=notion, calendar_gateway=calendar)

    result = orchestrator.run_once()

    assert result.failed_count == 1
    assert result.created_count == 1
    assert result.failure_items[0].retry_eligible is True
