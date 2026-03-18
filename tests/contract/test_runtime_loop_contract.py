"""Contract tests for runtime loop behavior."""

from src import main as main_module


def test_parse_args_defaults_to_loop(monkeypatch):
    monkeypatch.setattr(
        main_module.argparse.ArgumentParser,
        "parse_args",
        lambda _self: main_module.argparse.Namespace(once=False, loop=False, max_cycles=None),
    )
    args = main_module.parse_args()
    assert args.once is False
    assert args.loop is False


def test_parse_args_once_mode(monkeypatch):
    monkeypatch.setattr(
        main_module.argparse.ArgumentParser,
        "parse_args",
        lambda _self: main_module.argparse.Namespace(once=True, loop=False, max_cycles=None),
    )
    args = main_module.parse_args()
    assert args.once is True
