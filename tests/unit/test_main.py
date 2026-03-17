"""CLI tests for main entrypoint."""

from src import main as main_module


def test_main_returns_zero_on_no_failures(monkeypatch):
    monkeypatch.setattr(main_module, "parse_args", lambda: None)
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
    monkeypatch.setattr(main_module, "parse_args", lambda: None)
    monkeypatch.setattr(main_module, "Settings", lambda: object())
    monkeypatch.setattr(main_module, "run_to_dict", lambda _settings: {"failed_count": 2})
    code = main_module.main()
    assert code == 1
