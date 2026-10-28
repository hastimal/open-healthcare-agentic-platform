"""Tests for healthcare-agents CLI."""

from unittest.mock import patch

import pytest

from healthcare_agents.cli import handle_health, main
from healthcare_agents.config import ConfigurationError


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify --version prints program version and exits with 0."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    from healthcare_agents import __version__

    assert (
        f"healthcare-agents {__version__}" in captured.out
        or f"healthcare-agents {__version__}" in captured.err
    )


def test_uninstalled_checkout_version_matches_project_metadata() -> None:
    """A source checkout without installed distributions must report the release version."""
    import runpy
    import tomllib
    from importlib.metadata import PackageNotFoundError
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
        package = runpy.run_path(str(root / "src" / "healthcare_agents" / "__init__.py"))
    assert package["__version__"] == metadata["project"]["version"]


def test_cli_health_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify health subcommand outputs health and configuration info."""
    exit_code = main(["health"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Status: healthy" in captured.out
    assert "Environment: development" in captured.out
    assert "Configured Model Provider: ollama" in captured.out


def test_cli_status_alias(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify status is a working alias for health."""
    exit_code = main(["status"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Status: healthy" in captured.out


def test_cli_health_verbose(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify health --verbose prints detailed settings."""
    exit_code = main(["health", "--verbose"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "App Name: open-healthcare-agentic-platform" in captured.out
    assert "Configured Model: gemma4:e2b" in captured.out
    assert "Ollama URL: http://localhost:11434" in captured.out


def test_cli_help_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify CLI prints help when --help flag is provided."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "usage: healthcare-agents" in captured.out
    assert "check" in captured.out
    assert "start" in captured.out


def test_cli_default_one_command_invocation() -> None:
    """Verify bare CLI invocation triggers default launcher."""
    with patch("healthcare_agents.cli.handle_start", return_value=0) as mock_start:
        exit_code = main([])
        assert exit_code == 0
        assert mock_start.called


def test_cli_health_configuration_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify health command handles configuration failure gracefully."""
    with patch("healthcare_agents.cli.get_settings", side_effect=ConfigurationError("bad config")):
        exit_code = handle_health()
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Configuration error: bad config" in captured.err


def test_cli_serve_subcommand() -> None:
    """Verify serve subcommand invokes uvicorn."""
    with patch("uvicorn.run") as mock_uvicorn:
        exit_code = main(["serve", "--host", "127.0.0.1", "--port", "8000"])
        assert exit_code == 0
        assert mock_uvicorn.called


def test_cli_ui_subcommand() -> None:
    """Verify ui subcommand invokes subprocess."""
    with patch("subprocess.call", return_value=0) as mock_sub:
        exit_code = main(["ui", "--port", "8501"])
        assert exit_code == 0
        assert mock_sub.called


def test_cli_check_subcommand() -> None:
    """Verify check subcommand invokes handle_check."""
    with patch("healthcare_agents.cli.handle_check", return_value=0) as mock_chk:
        exit_code = main(["check", "--api-port", "9000", "--ui-port", "9501"])
        assert exit_code == 0
        assert mock_chk.called


def test_cli_start_subcommand() -> None:
    """Verify start subcommand invokes handle_start."""
    with patch("healthcare_agents.cli.handle_start", return_value=0) as mock_start:
        exit_code = main(["start", "--no-browser"])
        assert exit_code == 0
        assert mock_start.called


def test_cli_stop_subcommand() -> None:
    """Verify stop subcommand invokes handle_stop."""
    with patch("healthcare_agents.cli.handle_stop", return_value=0) as mock_stop:
        exit_code = main(["stop"])
        assert exit_code == 0
        assert mock_stop.called


def test_cli_demo_subcommand() -> None:
    """Verify demo subcommand invokes handle_demo."""
    with patch("healthcare_agents.cli.handle_demo", return_value=0) as mock_demo:
        exit_code = main(["demo", "--no-browser"])
        assert exit_code == 0
        assert mock_demo.called


def test_handle_check_all_ok(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify handle_check outputs status and returns 0 when checks pass."""
    from healthcare_agents.cli import handle_check
    from healthcare_agents.launcher import CheckResult

    mock_res = [
        CheckResult("Python Version", True, "Python 3.12.0", ""),
        CheckResult("Port 8000 (FastAPI)", True, "Available", ""),
        CheckResult("Port 8501 (Streamlit)", True, "Available", ""),
        CheckResult("Inference Endpoint (Ollama)", True, "Reachable", ""),
        CheckResult("Model 'gemma4:e2b'", True, "Found", ""),
    ]
    with patch("healthcare_agents.launcher.run_prerequisite_checks", return_value=mock_res):
        code = handle_check()
        assert code == 0
        captured = capsys.readouterr()
        assert "All system prerequisites satisfied!" in captured.out


def test_handle_check_failure(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify handle_check returns 1 on critical failure."""
    from healthcare_agents.cli import handle_check
    from healthcare_agents.launcher import CheckResult

    mock_res = [
        CheckResult("Port 8000 (FastAPI)", False, "Busy", "Free port"),
    ]
    with patch("healthcare_agents.launcher.run_prerequisite_checks", return_value=mock_res):
        code = handle_check()
        assert code == 1
        captured = capsys.readouterr()
        assert "Remediation: Free port" in captured.out


def test_handle_start_success() -> None:
    """Verify handle_start delegates to start_native_services when checks pass."""
    from healthcare_agents.cli import handle_start
    from healthcare_agents.launcher import CheckResult

    mock_res = [CheckResult("Port 8000 (FastAPI)", True, "Available", "")]
    with (
        patch("healthcare_agents.launcher.run_prerequisite_checks", return_value=mock_res),
        patch("healthcare_agents.launcher.start_native_services", return_value=0) as mock_start,
    ):
        code = handle_start()
        assert code == 0
        assert mock_start.called


def test_handle_start_failure_on_port_conflict(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify handle_start refuses to start if ports are occupied."""
    from healthcare_agents.cli import handle_start
    from healthcare_agents.launcher import CheckResult

    mock_res = [CheckResult("Port 8000 (FastAPI)", False, "Port busy", "Change port")]
    with patch("healthcare_agents.launcher.run_prerequisite_checks", return_value=mock_res):
        code = handle_start()
        assert code == 1
        captured = capsys.readouterr()
        assert "Cannot start: Port busy" in captured.err


def test_handle_stop_and_demo() -> None:
    """Verify handle_stop and handle_demo delegate to launcher functions."""
    from healthcare_agents.cli import handle_demo, handle_stop

    with patch("healthcare_agents.launcher.stop_native_services", return_value=0) as mock_stop:
        assert handle_stop() == 0
        assert mock_stop.called

    with (
        patch("healthcare_agents.launcher.run_prerequisite_checks"),
        patch("healthcare_agents.launcher.start_native_services", return_value=0) as mock_start,
    ):
        assert handle_demo(no_browser=True) == 0
        assert mock_start.called
