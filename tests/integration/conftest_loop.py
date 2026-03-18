"""Fixtures for loop scheduler integration tests."""

from datetime import datetime, timezone
import json

import pytest

from src.config import Settings


@pytest.fixture
def loop_settings(tmp_path):
    contact_path = tmp_path / "contact.json"
    contact_path.write_text(json.dumps({"Alice": "alice@example.com"}), encoding="utf-8")
    return Settings(
        notion_token="token",
        notion_database_id="db",
        contact_file=str(contact_path),
        sync_interval_seconds=600,
        drift_warning_seconds=30,
        shutdown_timeout_seconds=30,
    )


@pytest.fixture
def fixed_now():
    base = datetime(2026, 3, 17, 0, 0, 0, tzinfo=timezone.utc)
    state = {"i": 0}

    def _now():
        state["i"] += 1
        return base

    return _now
