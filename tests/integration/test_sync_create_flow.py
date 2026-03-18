"""Integration test for create flow."""

from src.sync.orchestrator import SyncOrchestrator


def test_create_flow_creates_event_and_updates_notion(
    settings, sample_create_task, notion_factory, calendar_factory
):
    notion = notion_factory([sample_create_task])
    calendar = calendar_factory()
    orchestrator = SyncOrchestrator(settings, notion_gateway=notion, calendar_gateway=calendar)

    result = orchestrator.run_once()

    assert result.created_count == 1
    assert result.updated_count == 0
    assert result.failed_count == 0
    assert len(calendar.created) == 1
    assert notion.updated_ids[0][0] == "page-1"
