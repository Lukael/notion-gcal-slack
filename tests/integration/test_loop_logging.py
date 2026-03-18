"""Integration test for cycle summary logging."""

import json
from datetime import datetime, timezone

from src.scheduler import SyncScheduler


def test_cycle_summary_logging_has_required_fields(settings):
    logs: list[str] = []
    monotonic = {"t": 0.0}

    def mono():
        return monotonic["t"]

    def sleep_fn(seconds):
        monotonic["t"] += seconds

    scheduler = SyncScheduler(
        settings,
        lambda _: {"failed_count": 0, "created_count": 1, "updated_count": 1},
        logger=logs.append,
        sleep_fn=sleep_fn,
        monotonic_fn=mono,
        now_fn=lambda: datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    scheduler.run_loop(max_cycles=1)

    finished = [json.loads(line) for line in logs if '"event": "cycle_finished"' in line][0]
    assert "run_id" in finished
    assert "started_at" in finished
    assert "finished_at" in finished
    assert "next_run_at" in finished
