"""Unit tests for Notion gateway."""

from src.config import Settings
from src.sync.notion_client import NotionGateway


class _FakeNotionClient:
    def __init__(self, auth):  # pylint: disable=unused-argument
        self.data_sources = self
        self.pages = self
        self._query_calls = 0

    def query(self, **_kwargs):
        self._query_calls += 1
        if self._query_calls == 1:
            return {
                "results": [
                    {
                        "id": "page-1",
                        "properties": {
                            "Task Name": {"title": [{"plain_text": "Task A"}]},
                            "Due Date": {"date": {"start": "2026-03-17"}},
                            "Status": {"select": {"name": "Todo"}},
                            "Assignees": {"multi_select": [{"name": "Alice"}]},
                            "Google ID": {"rich_text": []},
                        },
                    }
                ],
                "has_more": False,
            }
        return {"results": [], "has_more": False}

    def update(self, **_kwargs):
        return None


def _settings():
    return Settings(notion_token="token", notion_database_id="db")


def test_query_tasks_parses_notion_page(monkeypatch):
    monkeypatch.setattr("src.sync.notion_client.NotionClient", _FakeNotionClient)
    gateway = NotionGateway(_settings())
    tasks = gateway.query_tasks()
    assert len(tasks) == 1
    assert tasks[0].task_name == "Task A"
    assert tasks[0].google_id is None


def test_retry_raises_when_non_retriable(monkeypatch):
    monkeypatch.setattr("src.sync.notion_client.NotionClient", _FakeNotionClient)
    gateway = NotionGateway(_settings())

    def failing():
        raise RuntimeError("bad request")

    monkeypatch.setattr("time.sleep", lambda _: None)
    try:
        gateway._retry(failing)  # pylint: disable=protected-access
        assert False
    except RuntimeError as exc:
        assert "bad request" in str(exc)
