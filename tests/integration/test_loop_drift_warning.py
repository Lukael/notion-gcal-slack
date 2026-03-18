"""Integration test for drift warning logs."""

from datetime import datetime, timezone

from src.scheduler import SyncScheduler


def test_drift_warning_logged_when_interval_exceeded(settings):
    logs: list[str] = []
    settings.sync_interval_seconds = 10
    settings.drift_warning_seconds = 1
    monotonic = {"t": 0.0}

    def mono():
        return monotonic["t"]

    def sleep_fn(seconds):
        monotonic["t"] += seconds

    def run_cycle(_):
        monotonic["t"] += 15
        return {"failed_count": 0}

    scheduler = SyncScheduler(
        settings,
        run_cycle,
        logger=logs.append,
        sleep_fn=sleep_fn,
        monotonic_fn=mono,
        now_fn=lambda: datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    scheduler.run_loop(max_cycles=1)
    assert any("drift_warning" in line for line in logs)
