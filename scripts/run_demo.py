#!/usr/bin/env python3
"""One-command demo launcher for the Open Healthcare Agentic Platform.

Runs cross-platform preflight diagnostics (Docker, native Ollama, required
model, port availability) before starting Docker Compose, then waits for the
API to become healthy and opens the Streamlit UI in a browser.

Usage:
    uv run python scripts/run_demo.py
    uv run python scripts/run_demo.py --non-interactive
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass

REQUIRED_PORTS: tuple[int, ...] = (8000, 8501, 3000, 9090, 3200, 4317, 4318)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
REQUIRED_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:e2b")
API_HEALTH_URL = os.environ.get("DEMO_API_HEALTH_URL", "http://localhost:8000/health")
UI_URL = os.environ.get("DEMO_UI_URL", "http://localhost:8501")
DEFAULT_HEALTH_TIMEOUT = 180.0

_RESET = "\033[0m"
_STYLES = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "bold": "\033[1m",
}

DOCKER_INSTALL_HINT = (
    "Install Docker Desktop (macOS/Windows) or Docker Engine (Linux): "
    "https://docs.docker.com/get-docker/\n"
    "Windows: run this launcher from a WSL2 distro with Docker Desktop WSL integration enabled."
)
DOCKER_DAEMON_HINT = (
    "Start Docker Desktop, or on Linux: sudo systemctl start docker\n"
    "Verify with: docker info"
)
COMPOSE_HINT = (
    "Install the Compose v2 plugin: https://docs.docker.com/compose/install/\n"
    "Verify with: docker compose version"
)
OLLAMA_INSTALL_HINTS = {
    "Darwin": "Install Ollama for macOS: https://ollama.com/download/mac (or: brew install ollama)",
    "Linux": "Install Ollama for Linux: curl -fsSL https://ollama.com/install.sh | sh",
    "Windows": (
        "Install Ollama for Windows: https://ollama.com/download/windows "
        "(inside WSL2, run the Linux installer in your distro instead)"
    ),
}


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def _color_enabled() -> bool:
    """Return True when ANSI colors should be emitted on stdout."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not sys.stdout.isatty():
        return False
    if platform.system() == "Windows":
        return bool(
            os.environ.get("WT_SESSION")
            or os.environ.get("ANSICON")
            or os.environ.get("ConEmuANSI") == "ON"
            or os.environ.get("TERM_PROGRAM")
        )
    return True


def paint(text: str, *styles: str) -> str:
    """Wrap ``text`` in ANSI styles when the terminal supports them."""
    if not _color_enabled():
        return text
    prefix = "".join(_STYLES[s] for s in styles if s in _STYLES)
    return f"{prefix}{text}{_RESET}" if prefix else text


def info(message: str) -> None:
    print(f"{paint('[info]', 'blue')} {message}")


def ok(message: str) -> None:
    print(f"{paint('[ ok ]', 'green')} {message}")


def warn(message: str) -> None:
    print(f"{paint('[warn]', 'yellow')} {message}")


def fail(message: str) -> None:
    print(f"{paint('[fail]', 'red', 'bold')} {message}")


def hint(message: str) -> None:
    print(f"       {paint(message, 'yellow')}")


def confirm(question: str, *, non_interactive: bool, default: bool = True) -> bool:
    """Ask a yes/no question, falling back to ``default`` when non-interactive."""
    if non_interactive:
        return default
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        answer = input(f"{paint('?', 'blue')} {question} {suffix} ").strip().lower()
    except EOFError:
        return default
    if not answer:
        return default
    return answer in {"y", "yes"}


# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
def port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Return True when ``port`` cannot be bound on the loopback interface."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return True
    return False


def find_busy_ports(ports: tuple[int, ...] = REQUIRED_PORTS) -> list[int]:
    """Return the subset of ``ports`` that are already bound."""
    return [port for port in ports if port_in_use(port)]


def port_hint(port: int) -> str:
    """Return an OS-appropriate command to inspect a busy port."""
    if platform.system() == "Windows":
        return f"netstat -ano | findstr :{port}   then   taskkill /PID <pid> /F"
    return f"lsof -nP -iTCP:{port} -sTCP:LISTEN   (or: ss -ltnp 'sport = :{port}')"


def check_docker() -> tuple[bool, str, str]:
    """Verify the Docker CLI, daemon and Compose v2 plugin are usable."""
    if shutil.which("docker") is None:
        return False, "docker CLI not found on PATH", DOCKER_INSTALL_HINT
    try:
        daemon = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError) as err:
        return False, f"failed to run `docker info`: {err}", DOCKER_INSTALL_HINT
    if daemon.returncode != 0:
        return False, "Docker daemon is not reachable", DOCKER_DAEMON_HINT
    try:
        compose = subprocess.run(
            ["docker", "compose", "version"], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError) as err:
        return False, f"failed to run `docker compose version`: {err}", COMPOSE_HINT
    if compose.returncode != 0:
        return False, "`docker compose` plugin is not available", COMPOSE_HINT
    return True, "Docker daemon and Compose plugin are available", ""


@dataclass
class OllamaStatus:
    """Outcome of the native Ollama preflight check."""

    state: str  # "ok" | "unreachable" | "missing_model"
    detail: str
    hint: str = ""


def _ollama_tags() -> list[str] | None:
    """Return installed model names, or None when Ollama is unreachable."""
    request = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags", method="GET")
    try:
        with urllib.request.urlopen(request, timeout=5.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError):
        return None
    names: list[str] = []
    for entry in payload.get("models", []):
        name = entry.get("name")
        if not name:
            continue
        names.append(name)
        if name.endswith(":latest"):
            names.append(name[: -len(":latest")])
    return names


def check_ollama() -> OllamaStatus:
    """Verify native Ollama is running and the required model is installed."""
    models = _ollama_tags()
    if models is None:
        install = OLLAMA_INSTALL_HINTS.get(
            platform.system(), "See https://ollama.com/download"
        )
        return OllamaStatus(
            "unreachable",
            f"native Ollama is not reachable at {OLLAMA_BASE_URL}",
            f"{install}\nThen start it with: ollama serve",
        )
    if REQUIRED_MODEL in models or f"{REQUIRED_MODEL}:latest" in models:
        return OllamaStatus("ok", f"Ollama is running and '{REQUIRED_MODEL}' is installed")
    return OllamaStatus(
        "missing_model",
        f"Ollama is running but model '{REQUIRED_MODEL}' is not installed",
        f"ollama pull {REQUIRED_MODEL}",
    )


def pull_model() -> bool:
    """Pull the required model via the Ollama CLI."""
    if shutil.which("ollama") is None:
        warn("`ollama` CLI not found on PATH; pull the model manually")
        return False
    try:
        subprocess.run(["ollama", "pull", REQUIRED_MODEL], check=True)
    except (OSError, subprocess.CalledProcessError) as err:
        warn(f"`ollama pull {REQUIRED_MODEL}` failed: {err}")
        return False
    return True


def platform_notes() -> None:
    """Print OS-specific networking notes that commonly trip up newcomers."""
    system = platform.system()
    if system == "Linux":
        info(
            "Linux detected: containers reach native Ollama via host.docker.internal, "
            'which needs extra_hosts: ["host.docker.internal:host-gateway"] in docker-compose.yml.'
        )
    elif system == "Windows":
        info(
            "Windows detected: run this launcher inside WSL2 with Docker Desktop WSL integration enabled."
        )


def wait_for_health(timeout: float, interval: float = 2.0) -> bool:
    """Poll the API health endpoint until it responds or ``timeout`` elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(API_HEALTH_URL, timeout=5.0) as response:
                if 200 <= response.status < 300:
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            pass
        time.sleep(interval)
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Launch the demo stack with cross-platform preflight checks."
    )
    parser.add_argument(
        "--non-interactive",
        "-y",
        action="store_true",
        help="never prompt; use the default answer for every question",
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="do not open the UI in a browser"
    )
    parser.add_argument(
        "--skip-ollama-check", action="store_true", help="skip native Ollama checks"
    )
    parser.add_argument(
        "--skip-port-check", action="store_true", help="skip port availability checks"
    )
    parser.add_argument(
        "--health-timeout",
        type=float,
        default=DEFAULT_HEALTH_TIMEOUT,
        help="seconds to wait for the API health endpoint (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    non_interactive = args.non_interactive or not sys.stdin.isatty()

    print(paint("Open Healthcare Agentic Platform - demo launcher", "bold"))
    print(
        f"Platform: {platform.system()} {platform.release()}  |  "
        f"Python: {platform.python_version()}"
    )
    print()

    info("Checking Docker ...")
    docker_ok, docker_detail, docker_hint = check_docker()
    if not docker_ok:
        fail(docker_detail)
        for line in docker_hint.splitlines():
            hint(line)
        return 1
    ok(docker_detail)
    platform_notes()

    if args.skip_ollama_check:
        warn("Skipping Ollama checks (--skip-ollama-check)")
    else:
        info("Checking native Ollama ...")
        status = check_ollama()
        if status.state == "ok":
            ok(status.detail)
        elif status.state == "missing_model":
            warn(status.detail)
            hint(status.hint)
            if confirm(f"Pull '{REQUIRED_MODEL}' now?", non_interactive=non_interactive):
                if not pull_model():
                    warn("Continuing without the model; inference will fail until it is pulled")
            else:
                warn("Continuing without the model; inference will fail until it is pulled")
        else:
            fail(status.detail)
            for line in status.hint.splitlines():
                hint(line)
            if not confirm(
                "Continue without native Ollama?",
                non_interactive=non_interactive,
                default=False,
            ):
                return 1

    if args.skip_port_check:
        warn("Skipping port checks (--skip-port-check)")
    else:
        info("Checking port availability ...")
        busy = find_busy_ports()
        if busy:
            fail(f"Port(s) already in use: {', '.join(str(p) for p in busy)}")
            for port in busy:
                hint(f"port {port}: {port_hint(port)}")
            hint("Stop the conflicting process, or change the matching port in .env")
            if not confirm(
                "Continue anyway?", non_interactive=non_interactive, default=False
            ):
                return 1
        else:
            ok(f"Ports free: {', '.join(str(p) for p in REQUIRED_PORTS)}")

    info("Starting Docker Compose stack ...")
    try:
        subprocess.run(["docker", "compose", "up", "-d", "--build"], check=True)
    except subprocess.CalledProcessError as err:
        fail(f"`docker compose up` failed with exit code {err.returncode}")
        hint("Inspect the logs with: docker compose logs --tail=100")
        return err.returncode or 1
    except OSError as err:
        fail(f"Could not run docker compose: {err}")
        return 1

    info(f"Waiting for the API to become healthy ({API_HEALTH_URL}) ...")
    if not wait_for_health(args.health_timeout):
        fail(f"API did not become healthy within {args.health_timeout:.0f}s")
        hint("Check the logs with: docker compose logs api")
        return 1
    ok("API is healthy")

    ok(f"UI available at {UI_URL}")
    if not args.no_browser:
        try:
            webbrowser.open(UI_URL)
        except Exception:  # pragma: no cover - browser availability varies
            warn(f"Could not open a browser automatically - visit {UI_URL}")

    print()
    print(paint("Demo is running. Stop it with: docker compose down", "bold"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
