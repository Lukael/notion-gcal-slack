"""Validation and parsing helpers."""

from datetime import date, datetime, timedelta, timezone
import re

from dateutil import parser as dtparser

KST = timezone(timedelta(hours=9))


def parse_notion_date(iso_value: str, tz_name: str = "Asia/Seoul") -> date:
    """Parse notion date/datetime into date with timezone fallback."""
    dt = dtparser.isoparse(iso_value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=KST if tz_name == "Asia/Seoul" else timezone.utc)
    return dt.date()


def all_day_end(start: date) -> date:
    """Google all-day end date is exclusive."""
    return start + timedelta(days=1)


def is_valid_email(value: str) -> bool:
    """Simple email format guard for attendee mapping."""
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value or ""))


def iso_now_kst() -> str:
    """RFC3339 timestamp in KST for sync metadata."""
    return datetime.now(KST).isoformat()
