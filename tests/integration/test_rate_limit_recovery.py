"""Integration-like test for rate-limit retry policy."""

from src.config import Settings
from src.sync.notion_client import NotionGateway


def test_retry_backoff_recovers_after_rate_limit(monkeypatch):
    settings = Settings(
        notion_token="token",
        notion_database_id="db",
        max_retries=2,
        retry_base_seconds=0,
    )
    gateway = NotionGateway(settings)

    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("429 rate limit")
        return {"ok": True}

    monkeypatch.setattr("time.sleep", lambda _: None)
    result = gateway._retry(flaky)  # pylint: disable=protected-access

    assert result["ok"] is True
    assert calls["n"] == 2
