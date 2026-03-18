"""Integration test for failure recovery rate metric."""

import json
from datetime import datetime, timezone

from src.scheduler import SyncScheduler


def test_recovery_rate_is_logged(settings):
    logs: list[str] = []
    monotonic = {"t": 0.0}
    calls = {"count": 0}

    def mono():
        return monotonic["t"]

    def sleep_fn(seconds):
        monotonic["t"] += seconds

    def run_cycle(_):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("first fail")
        return {"failed_count": 0}

    scheduler = SyncScheduler(
        settings,
        run_cycle,
        logger=logs.append,
        sleep_fn=sleep_fn,
        monotonic_fn=mono,
        now_fn=lambda: datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    scheduler.run_loop(max_cycles=2)
    last_line = json.loads(logs[-1])
    assert last_line["event"] == "loop_stopped"
    assert last_line["recovery_rate"] == 1.0
