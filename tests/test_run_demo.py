"""Tests for the demo launcher preflight helpers."""

from __future__ import annotations

import importlib.util
import socket
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_demo.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_demo", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_demo = _load()


def test_port_in_use_detects_bound_socket() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        assert run_demo.port_in_use(port) is True


def test_find_busy_ports_reports_only_busy_ports() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        port = sock.getsockname()[1]
        assert run_demo.find_busy_ports((port,)) == [port]


def test_confirm_non_interactive_uses_default() -> None:
    assert run_demo.confirm("go?", non_interactive=True, default=True) is True
    assert run_demo.confirm("go?", non_interactive=True, default=False) is False


def test_paint_respects_no_color(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    assert run_demo.paint("hello", "red", "bold") == "hello"


def test_port_hint_mentions_port() -> None:
    assert "8000" in run_demo.port_hint(8000)
