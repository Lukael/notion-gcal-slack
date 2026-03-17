"""Ensure no reverse sync write happens for update branch."""

from src.sync.orchestrator import SyncOrchestrator


def test_update_does_not_write_back_google_id(
    settings, sample_update_task, notion_factory, calendar_factory
):
    notion = notion_factory([sample_update_task])
    calendar = calendar_factory()

    result = SyncOrchestrator(settings, notion_gateway=notion, calendar_gateway=calendar).run_once()

    assert result.updated_count == 1
    assert notion.updated_ids == []
