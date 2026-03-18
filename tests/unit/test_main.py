"""CLI tests for main entrypoint."""

import argparse

from src import main as main_module


def test_main_returns_zero_on_no_failures(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "parse_args",
        lambda: argparse.Namespace(once=True, loop=False, max_cycles=None),
    )
    monkeypatch.setattr(main_module, "Settings", lambda: object())
    monkeypatch.setattr(
        main_module,
        "run_to_dict",
        lambda _settings: {
            "failed_count": 0,
            "created_count": 1,
            "updated_count": 0,
            "skipped_count": 0,
        },
    )
    code = main_module.main()
    assert code == 0


def test_main_returns_non_zero_on_failures(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "parse_args",
        lambda: argparse.Namespace(once=True, loop=False, max_cycles=None),
    )
    monkeypatch.setattr(main_module, "Settings", lambda: object())
    monkeypatch.setattr(main_module, "run_to_dict", lambda _settings: {"failed_count": 2})
    code = main_module.main()
    assert code == 1


def test_main_loop_mode_dispatches_scheduler(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "parse_args",
        lambda: argparse.Namespace(once=False, loop=True, max_cycles=1),
    )
    monkeypatch.setattr(main_module, "Settings", lambda: object())

    class DummyScheduler:
        def __init__(self, *_args, **_kwargs):
            pass

        def run_loop(self, max_cycles=None):
            assert max_cycles == 1
            return {"cycles": 1, "failures": 0, "recovery_rate": 1.0}

    monkeypatch.setattr(main_module, "SyncScheduler", DummyScheduler)
    code = main_module.main()
    assert code == 0
