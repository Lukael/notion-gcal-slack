"""Integration tests for loop interval behavior."""

from datetime import datetime, timezone

from src.scheduler import SyncScheduler


def test_loop_runs_repeated_cycles(settings):
    calls = {"count": 0}
    monotonic = {"t": 0.0}

    def run_cycle(_):
        calls["count"] += 1
        return {"failed_count": 0}

    def mono():
        return monotonic["t"]

    def sleep_fn(seconds):
        monotonic["t"] += seconds

    scheduler = SyncScheduler(
        settings,
        run_cycle,
        logger=lambda _msg: None,
        sleep_fn=sleep_fn,
        monotonic_fn=mono,
        now_fn=lambda: datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    scheduler.run_loop(max_cycles=3)
    assert calls["count"] == 3
