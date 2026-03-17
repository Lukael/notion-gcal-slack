"""CLI entrypoint for Notion -> Google Calendar sync."""

import argparse
import json

from src.config import Settings
from src.sync.orchestrator import run_to_dict


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Sync Notion tasks to Google Calendar")
    parser.add_argument("--once", action="store_true", help="Run single sync cycle (default)")
    return parser.parse_args()


def main() -> int:
    """Run application and print summary."""
    parse_args()
    settings = Settings()
    result = run_to_dict(settings)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
