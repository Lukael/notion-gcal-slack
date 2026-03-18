"""Loop scheduler for persistent container execution."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import signal
import time
from typing import Callable
from uuid import uuid4

from src.config import Settings
from src.domain.models import LoopRunRecord, ShutdownState


class SyncScheduler:  # pylint: disable=too-few-public-methods
    """Run sync cycles on a fixed interval."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        settings: Settings,
        run_cycle: Callable[[Settings], dict],
        *,
        logger: Callable[[str], None] = print,
        sleep_fn: Callable[[float], None] = time.sleep,
        monotonic_fn: Callable[[], float] = time.monotonic,
        now_fn: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ):
        self.settings = settings
        self.run_cycle = run_cycle
        self.logger = logger
        self.sleep_fn = sleep_fn
        self.monotonic_fn = monotonic_fn
        self.now_fn = now_fn
        self.shutdown = ShutdownState()
        self._install_signal_handlers()

    def _install_signal_handlers(self) -> None:
        def handler(signum, _frame):
            self.shutdown.signal_received = True
            self.shutdown.signal_name = signal.Signals(signum).name
            self.shutdown.received_at = self.now_fn()
            self.logger(
                json.dumps(
                    {
                        "event": "shutdown_signal_received",
                        "signal": self.shutdown.signal_name,
                        "received_at": self.shutdown.received_at.isoformat(),
                    },
                    ensure_ascii=False,
                )
            )

        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)

    def _sleep_interruptible(self, total_seconds: float) -> None:
        remaining = max(0.0, total_seconds)
        while remaining > 0 and not self.shutdown.signal_received:
            chunk = min(1.0, remaining)
            self.sleep_fn(chunk)
            remaining -= chunk

    def run_loop(  # pylint: disable=too-many-locals
        self, max_cycles: int | None = None
    ) -> dict[str, float]:
        """Run cycles until stopped."""
        cycle_index = 0
        failures = 0
        successful_after_failure = 0
        prev_failed = False
        next_run_mono = self.monotonic_fn()

        while not self.shutdown.signal_received:
            if max_cycles is not None and cycle_index >= max_cycles:
                break
            cycle_index += 1
            run_id = str(uuid4())
            started_at = self.now_fn()
            start_mono = self.monotonic_fn()
            self.logger(
                json.dumps(
                    {
                        "event": "cycle_started",
                        "run_id": run_id,
                        "started_at": started_at.isoformat(),
                    },
                    ensure_ascii=False,
                )
            )
            status = "success"
            result = {"created_count": 0, "updated_count": 0, "failed_count": 0}
            try:
                result = self.run_cycle(self.settings)
                if result.get("failed_count", 0) > 0:
                    status = "failed"
            except Exception as exc:  # pylint: disable=broad-exception-caught
                status = "failed"
                result = {"created_count": 0, "updated_count": 0, "failed_count": 1}
                self.logger(
                    json.dumps({"event": "cycle_exception", "run_id": run_id, "error": str(exc)})
                )

            finished_at = self.now_fn()
            duration = self.monotonic_fn() - start_mono

            if status == "failed":
                failures += 1
                prev_failed = True
            else:
                if prev_failed:
                    successful_after_failure += 1
                prev_failed = False

            next_run_mono += self.settings.sync_interval_seconds
            sleep_for = next_run_mono - self.monotonic_fn()
            next_run_at = self.now_fn() + timedelta(seconds=max(0.0, sleep_for))

            record = LoopRunRecord(
                run_id=run_id,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                status=status,
                created_count=result.get("created_count", 0),
                updated_count=result.get("updated_count", 0),
                failed_count=result.get("failed_count", 0),
                next_run_at=next_run_at,
            )
            self.logger(
                json.dumps(
                    {
                        "event": "cycle_finished",
                        "run_id": record.run_id,
                        "started_at": record.started_at.isoformat(),
                        "finished_at": record.finished_at.isoformat(),
                        "duration_seconds": record.duration_seconds,
                        "status": record.status,
                        "created_count": record.created_count,
                        "updated_count": record.updated_count,
                        "failed_count": record.failed_count,
                        "next_run_at": (
                            record.next_run_at.isoformat() if record.next_run_at else None
                        ),
                    },
                    ensure_ascii=False,
                )
            )

            if sleep_for < -float(self.settings.drift_warning_seconds):
                self.logger(
                    json.dumps(
                        {
                            "event": "drift_warning",
                            "run_id": run_id,
                            "drift_seconds": round(abs(sleep_for), 3),
                            "threshold_seconds": self.settings.drift_warning_seconds,
                        },
                        ensure_ascii=False,
                    )
                )
                sleep_for = 0

            if not self.shutdown.signal_received:
                self._sleep_interruptible(sleep_for)

        self.shutdown.safe_to_exit = True
        recovery_rate = (successful_after_failure / failures) if failures > 0 else 1.0
        self.logger(
            json.dumps(
                {
                    "event": "loop_stopped",
                    "cycles": cycle_index,
                    "failures": failures,
                    "successful_after_failure": successful_after_failure,
                    "recovery_rate": recovery_rate,
                    "signal": self.shutdown.signal_name,
                    "safe_to_exit": self.shutdown.safe_to_exit,
                },
                ensure_ascii=False,
            )
        )
        return {"cycles": cycle_index, "failures": failures, "recovery_rate": recovery_rate}
