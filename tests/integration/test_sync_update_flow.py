"""Integration test for update flow."""

from src.sync.orchestrator import SyncOrchestrator


def test_update_flow_patches_existing_event(
    settings, sample_update_task, notion_factory, calendar_factory
):
    notion = notion_factory([sample_update_task])
    calendar = calendar_factory()
    orchestrator = SyncOrchestrator(settings, notion_gateway=notion, calendar_gateway=calendar)

    result = orchestrator.run_once()

    assert result.created_count == 0
    assert result.updated_count == 1
    assert result.failed_count == 0
    assert len(calendar.updated) == 1
    assert calendar.updated[0][0] == "evt-abc"


def test_update_flow_recreates_when_event_not_found(
    settings, sample_update_task, notion_factory, calendar_factory
):
    notion = notion_factory([sample_update_task])
    calendar = calendar_factory(not_found_event_ids={"evt-abc"})
    orchestrator = SyncOrchestrator(settings, notion_gateway=notion, calendar_gateway=calendar)

    result = orchestrator.run_once()

    assert result.updated_count == 1
    assert result.failed_count == 0
    assert len(calendar.created) == 1
    assert notion.updated_ids[0][0] == "page-2"
