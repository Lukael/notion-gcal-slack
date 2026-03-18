"""Unit tests for scheduler module."""

from datetime import datetime, timezone

from src.scheduler import SyncScheduler


def test_scheduler_runs_expected_cycle_count(settings):
    logs: list[str] = []
    monotonic = {"t": 0.0}

    def mono():
        return monotonic["t"]

    def sleep_fn(seconds):
        monotonic["t"] += seconds

    def run_cycle(_):
        return {"failed_count": 0, "created_count": 1, "updated_count": 0}

    scheduler = SyncScheduler(
        settings,
        run_cycle,
        logger=logs.append,
        sleep_fn=sleep_fn,
        monotonic_fn=mono,
        now_fn=lambda: datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    result = scheduler.run_loop(max_cycles=3)
    assert result["cycles"] == 3
    assert result["failures"] == 0


def test_scheduler_shutdown_state_transitions(settings):
    scheduler = SyncScheduler(
        settings,
        lambda _: {"failed_count": 0},
        logger=lambda _msg: None,
        sleep_fn=lambda _s: None,
        monotonic_fn=lambda: 0.0,
        now_fn=lambda: datetime(2026, 3, 17, tzinfo=timezone.utc),
    )
    assert scheduler.shutdown.signal_received is False
    scheduler.shutdown.signal_received = True
    scheduler.run_loop(max_cycles=1)
    assert scheduler.shutdown.safe_to_exit is True


def test_scheduler_logs_drift_warning(settings):
    logs: list[str] = []
    settings.sync_interval_seconds = 10
    settings.drift_warning_seconds = 1
    monotonic = {"t": 0.0}

    def mono():
        return monotonic["t"]

    def sleep_fn(seconds):
        monotonic["t"] += seconds

    def run_cycle(_):
        monotonic["t"] += 20.0  # force drift
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
