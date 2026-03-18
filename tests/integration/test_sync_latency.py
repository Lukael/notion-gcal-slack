"""Latency SLO verification scenario."""

import time

from src.sync.orchestrator import SyncOrchestrator


def test_create_update_latency_under_one_minute(
    settings, sample_create_task, sample_update_task, notion_factory, calendar_factory
):
    notion = notion_factory([sample_create_task, sample_update_task])
    calendar = calendar_factory()
    orchestrator = SyncOrchestrator(settings, notion_gateway=notion, calendar_gateway=calendar)

    started = time.perf_counter()
    result = orchestrator.run_once()
    elapsed = time.perf_counter() - started

    assert result.failed_count == 0
    assert elapsed < 60
