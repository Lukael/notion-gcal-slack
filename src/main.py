"""CLI entrypoint for Notion -> Google Calendar sync."""

import argparse
import json

from src.config import Settings
from src.scheduler import SyncScheduler
from src.sync.orchestrator import run_to_dict


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Sync Notion tasks to Google Calendar")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Run single sync cycle")
    mode.add_argument("--loop", action="store_true", help="Run persistent loop mode (default)")
    parser.add_argument(
        "--max-cycles", type=int, default=None, help="Optional max cycles for test/debug"
    )
    return parser.parse_args()


def main() -> int:
    """Run application and print summary."""
    args = parse_args()
    settings = Settings()
    if args.once:
        result = run_to_dict(settings)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["failed_count"] == 0 else 1

    scheduler = SyncScheduler(settings, run_cycle=run_to_dict)
    loop_result = scheduler.run_loop(max_cycles=args.max_cycles)
    print(json.dumps(loop_result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
