"""Integration test for graceful signal shutdown behavior."""

from datetime import datetime, timezone

from src.scheduler import SyncScheduler


def test_signal_shutdown_stops_loop(settings):
    monotonic = {"t": 0.0}

    def mono():
        return monotonic["t"]

    def sleep_fn(seconds):
        monotonic["t"] += seconds

    scheduler = SyncScheduler(
        settings,
        lambda _: {"failed_count": 0},
        logger=lambda _msg: None,
        sleep_fn=sleep_fn,
        monotonic_fn=mono,
        now_fn=lambda: datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    scheduler.shutdown.signal_received = True
    result = scheduler.run_loop()
    assert result["cycles"] == 0
    assert scheduler.shutdown.safe_to_exit is True
