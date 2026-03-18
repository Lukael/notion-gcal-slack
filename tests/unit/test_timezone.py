"""Unit tests for timezone fallback behavior."""

from src.domain.validators import parse_notion_date


def test_parse_notion_date_fallback_timezone():
    parsed = parse_notion_date("2026-03-17T10:00:00", "Asia/Seoul")
    assert parsed.isoformat() == "2026-03-17"


def test_parse_notion_date_from_date_literal():
    parsed = parse_notion_date("2026-03-17", "Asia/Seoul")
    assert parsed.isoformat() == "2026-03-17"
