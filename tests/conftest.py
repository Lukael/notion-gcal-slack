"""Test bootstrap."""

from pathlib import Path
import sys

import json
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import Settings


@pytest.fixture
def settings(tmp_path):
    """Base settings fixture reusable across all tests."""
    contact_path = tmp_path / "contact.json"
    contact_path.write_text(json.dumps({"Alice": "alice@example.com"}), encoding="utf-8")
    return Settings(
        notion_token="test-token",
        notion_database_id="test-db",
        gcal_calendar_id="primary",
        timezone="Asia/Seoul",
        contact_file=str(contact_path),
        dry_run=False,
    )
