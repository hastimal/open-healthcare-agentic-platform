#!/usr/bin/env python3
"""Unified demonstration & development launcher for Open Healthcare Agentic Platform.

Validates Docker, native Ollama, and Gemma 4 model availability, starts the full Compose
stack (API, Streamlit, OpenTelemetry Collector, Prometheus, Tempo, Grafana), waits for
health/readiness, displays all service URLs, and opens Streamlit in the browser (unless
--no-browser is passed).
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from typing import Any, NamedTuple


class PublishedPort(NamedTuple):
    service: str
    host: str
    port: int
    target: int


def compose_json(*args: str) -> Any:
    """Read Compose state without printing configuration values or starting services."""
    try:
        result = subprocess.run(
            ["docker", "compose", *args, "--format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("Docker Compose did not respond; check Docker and Compose v2.") from exc
    if result.returncode:
        raise RuntimeError("Docker Compose failed; run 'docker compose config' to check setup.")
    try:
        if args == ("ps",):
            text = result.stdout.strip()
            return (
                json.loads(text)
                if text.startswith("[")
                else [json.loads(line) for line in text.splitlines() if line.strip()]
            )
        return json.loads(result.stdout)
    except ValueError as exc:
        raise RuntimeError("Could not read Docker Compose JSON; update to Compose v2.") from exc


def published_ports(config: dict[str, Any]) -> list[PublishedPort]:
    """Use resolved Compose ports, including .env and shell overrides."""
    ports = []
    for service, settings in config["services"].items():
        for entry in settings.get("ports", []):
            if entry.get("protocol", "tcp") != "tcp" or not entry.get("published"):
                continue
            try:
                port = int(entry["published"])
                target = int(entry["target"])
                if not 0 < port < 65536:
                    raise ValueError("invalid port")
            except (ValueError, TypeError, KeyError) as exc:
                raise RuntimeError(
                    f"Unsupported published port for {service}; check Compose config."
                ) from exc
            ports.append(PublishedPort(service, entry.get("host_ip") or "0.0.0.0", port, target))
    return ports


def owned_ports(containers: list[dict[str, Any]]) -> set[tuple[str, str, int]]:
    """Only exempt publishers reported by this Compose project."""
    return {
        (container["Service"], publisher["URL"], int(publisher["PublishedPort"]))
        for container in containers
        for publisher in container.get("Publishers") or []
        if publisher.get("Protocol", "tcp") == "tcp" and publisher.get("PublishedPort")
    }


def port_available(host: str, port: int) -> bool:
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    try:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
    except OSError:
        return False
    return True


def check_ports(ports: list[PublishedPort], owned: set[tuple[str, str, int]]) -> bool:
    available = True
    for item in ports:
        if (item.service, item.host, item.port) in owned:
            continue
        if not port_available(item.host, item.port):
            available = False
            log(f"❌ {item.service}: port {item.host}:{item.port} is unavailable.")
            log(f"   macOS/Linux: lsof -nP -iTCP:{item.port} -sTCP:LISTEN")
            log(f"   Windows: netstat -ano | findstr :{item.port}")
            log("   Stop the conflicting service yourself or change its Compose host port.")
            if item.service in ("api", "ui"):
                setting = "API_PORT" if item.service == "api" else "STREAMLIT_PORT"
                log(f"   Set {setting} in .env, then rerun the launcher.")
    return available


def check_ollama(model: str) -> bool:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3.0) as resp:
            data = json.load(resp)
        names = [entry.get("name") for entry in data.get("models", [])]
        expected = model if ":" in model else model + ":latest"
        if model in names or expected in names:
            log(f"✅ Native Ollama model {model} is available.")
            return True
        log(f"⚠️ Required Ollama model is missing. Run: ollama pull {model}")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        log(f"⚠️ Native Ollama check failed ({type(exc).__name__}).")
        log("   Install Ollama from https://ollama.com/download, then run: ollama serve")
        log(f"   In another terminal run: ollama pull {model}")
    log("   Linux/WSL2: enable Docker integration; containers use host.docker.internal.")
    log("   Keep the existing host-gateway mapping; ensure Ollama is reachable from Docker.")
    return False


def service_url(ports: list[PublishedPort], service: str, target: int) -> str:
    for item in ports:
        if item.service == service and item.target == target:
            host = "localhost" if item.host in ("0.0.0.0", "::") else item.host
            if ":" in host:
                host = f"[{host}]"
            return f"http://{host}:{item.port}"
    raise RuntimeError(f"Compose must publish {service} port {target} for the demo launcher.")


def url_ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=3.0) as response:
            return bool(response.status in (200, 204))
    except OSError:
        return False


def log(msg: str) -> None:
    text = f"[DEMO-LAUNCHER] {msg}"
    if sys.stdout.isatty() and "NO_COLOR" not in os.environ:
        color = "31" if msg.startswith("❌") else "33" if msg.startswith("⚠️") else "36"
        text = f"\033[{color}m{text}\033[0m"
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        # Redirected output on Windows may use a legacy code page.
        encoding = sys.stdout.encoding or "utf-8"
        print(text.encode(encoding, errors="replace").decode(encoding), flush=True)


def check_command(cmd: list[str]) -> bool:
    try:
        subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=15
        )
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def wait_for_url(url: str, timeout_seconds: float = 60.0, description: str = "") -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_seconds:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status in (200, 204):
                    log(f"✅ {description} is ready ({url})")
                    return True
        except Exception:
            time.sleep(2.0)
    log(f"⚠️ {description} was not ready within {timeout_seconds}s ({url})")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified one-command demo launcher for Open Healthcare Agentic Platform"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically open the Streamlit web application in the default browser",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check-only", action="store_true", help="Check prerequisites without starting services"
    )
    mode.add_argument(
        "--status",
        action="store_true",
        help="Check running service health without starting services",
    )
    parser.add_argument(
        "--non-interactive", action="store_true", help="Never prompt to retry diagnostics"
    )
    args = parser.parse_args()

    log("==================================================================")
    log("🚀 OPEN HEALTHCARE AGENTIC PLATFORM — DEMONSTRATION LAUNCHER")
    log("==================================================================")

    # 1. Check Docker
    if not check_command(["docker", "info"]):
        log("❌ Docker CLI/daemon is unavailable. Start Docker Desktop or Docker Engine.")
        log("   Windows: enable Docker Desktop's WSL2 integration for your distribution.")
        return 1
    log("✅ Docker daemon is active.")
    if not check_command(["docker", "compose", "version"]):
        log("❌ Docker Compose v2 is unavailable. Install the Docker Compose plugin.")
        return 1

    # Resolve the same .env, host bindings and project ownership as Compose startup.
    try:
        config = compose_json("config")
        ports = published_ports(config)
        api_url = service_url(ports, "api", 8000)
        ui_url = service_url(ports, "ui", 8501)
        prometheus_url = service_url(ports, "prometheus", 9090)
        tempo_url = service_url(ports, "tempo", 3200)
        grafana_url = service_url(ports, "grafana", 3000)
        model = config["services"]["api"].get("environment", {}).get("MODEL_NAME", "gemma4:e2b")
        owned = owned_ports(compose_json("ps"))
    except (RuntimeError, KeyError, TypeError, AttributeError, ValueError) as exc:
        log(f"❌ Could not inspect Compose setup: {exc}")
        return 1

    health_urls = {
        "Streamlit UI": ui_url + "/_stcore/health",
        "FastAPI Gateway": api_url + "/health",
        "Prometheus Engine": prometheus_url + "/-/healthy",
        "Grafana Tempo Tracing": tempo_url + "/ready",
        "Grafana Dashboards": grafana_url + "/api/health",
    }
    ollama_ready = check_ollama(model)
    if args.status:
        ready = ollama_ready
        for name, url in health_urls.items():
            healthy = url_ready(url)
            log(f"{'✅' if healthy else '❌'} {name}: {url}")
            ready = ready and healthy
        return 0 if ready else 1

    while not check_ports(ports, owned):
        if args.check_only or args.non_interactive or not sys.stdin.isatty():
            return 1
        try:
            retry = input("Fix the port conflict, then retry checks? [y/N] ")
        except (EOFError, KeyboardInterrupt):
            return 1
        if retry.strip().lower() != "y":
            return 1
    if args.check_only:
        log("✅ Port preflight passed; no services were started.")
        return 0 if ollama_ready else 1

    # 3. Start Docker Compose Stack
    log(
        "📦 Starting Docker Compose services (API, UI, OTel Collector, Prometheus, Tempo, Grafana)..."
    )
    try:
        res = subprocess.run(
            ["docker", "compose", "up", "-d", "--build"],
            check=False,
            timeout=600,
        )
    except (OSError, subprocess.SubprocessError):
        log("❌ Compose startup failed or timed out; inspect 'docker compose ps' and logs.")
        return 1
    if res.returncode != 0:
        log("❌ Failed to start Docker Compose stack.")
        return 1

    # 4. Wait for Service Readiness
    log("⏳ Verifying service health and readiness...")
    ui_ready = wait_for_url(
        health_urls["Streamlit UI"], timeout_seconds=45.0, description="Streamlit UI"
    )
    api_ready = wait_for_url(
        health_urls["FastAPI Gateway"], timeout_seconds=45.0, description="FastAPI Gateway"
    )
    prometheus_ready = wait_for_url(
        health_urls["Prometheus Engine"], timeout_seconds=30.0, description="Prometheus Engine"
    )
    tempo_ready = wait_for_url(
        health_urls["Grafana Tempo Tracing"],
        timeout_seconds=30.0,
        description="Grafana Tempo Tracing",
    )
    grafana_ready = wait_for_url(
        health_urls["Grafana Dashboards"], timeout_seconds=30.0, description="Grafana Dashboards"
    )
    if not all((ui_ready, api_ready, prometheus_ready, tempo_ready, grafana_ready)):
        log(
            "❌ Some services are not ready. Inspect 'docker compose ps' and 'docker compose logs'."
        )
        return 1

    # 5. Open browser if requested
    if not args.no_browser and ui_ready:
        log("🌐 Opening Streamlit UI in default web browser...")
        try:
            webbrowser.open(ui_url)
        except Exception as exc:
            log(f"⚠️ Could not open browser automatically: {exc}")

    # 6. Summary and URLs
    log("==================================================================")
    log("🎉 PLATFORM & OBSERVABILITY SERVICES READY")
    log("==================================================================")
    print(f"  • Streamlit Web UI:        {ui_url}")
    print(f"  • FastAPI API & Docs:      {api_url}/docs")
    print(f"  • Grafana Dashboards:      {grafana_url} (UID: healthcare-observability)")
    print(f"  • Prometheus Metrics:      {prometheus_url}")
    print(f"  • Tempo Tracing:           {tempo_url}")
    print("  • OTLP Exporter Endpoints: http://localhost:4318 (HTTP), localhost:4317 (gRPC)")
    log("==================================================================")
    log("Primary demonstration query:")
    log(
        '"Find the best pediatric dentists in Houston, Texas, and research pediatric dental anxiety."'
    )
    log("==================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
