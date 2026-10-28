"""Offline launcher tests; process, HTTP and browser boundaries are isolated."""

from __future__ import annotations

import importlib.util
import io
import json
import socket
import subprocess
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_demo.py"
SPEC = importlib.util.spec_from_file_location("run_demo", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
run_demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_demo)


def config() -> dict[str, Any]:
    services: dict[str, Any] = {}
    for name, target in [
        ("api", 8000),
        ("ui", 8501),
        ("prometheus", 9090),
        ("tempo", 3200),
        ("grafana", 3000),
    ]:
        services[name] = {"ports": [{"published": str(target + 10000), "target": target}]}
    services["api"]["environment"] = {"MODEL_NAME": "gemma4:e2b"}
    return {"services": services}


class Response(io.BytesIO):
    status = 200


class DemoTests(unittest.TestCase):
    def command(self, args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if args == ["docker", "info"] or args == ["docker", "compose", "version"]:
            return subprocess.CompletedProcess(args, 0, "")
        if args == ["docker", "compose", "config", "--format", "json"]:
            return subprocess.CompletedProcess(args, 0, json.dumps(config()))
        if args == ["docker", "compose", "ps", "--format", "json"]:
            return subprocess.CompletedProcess(args, 0, "[]")
        if args == ["docker", "compose", "up", "-d", "--build"]:
            return subprocess.CompletedProcess(args, 0, "")
        raise AssertionError(f"Unexpected command: {args}")

    def response(self, url: Any, **kwargs: Any) -> Response:
        return Response(json.dumps({"models": [{"name": "gemma4:e2b"}]}).encode())

    def test_bound_socket_is_unavailable(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen(1)
            self.assertFalse(run_demo.port_available("127.0.0.1", sock.getsockname()[1]))

    def test_log_supports_legacy_windows_encoding(self) -> None:
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding="cp1252", write_through=True)
        with patch.object(run_demo.sys, "stdout", stream):
            run_demo.log("❌ Port unavailable")
        self.assertIn(b"Port unavailable", buffer.getvalue())

    def test_log_has_no_color_when_redirected(self) -> None:
        with patch.object(run_demo.sys, "stdout", io.StringIO()) as stream:
            run_demo.log("❌ Port unavailable")
            self.assertNotIn("\033[", stream.getvalue())

    def test_log_respects_no_color_in_terminal(self) -> None:
        with (
            patch.object(run_demo.sys, "stdout", io.StringIO()) as stream,
            patch.object(stream, "isatty", return_value=True),
            patch.dict(run_demo.os.environ, {"NO_COLOR": "1"}),
        ):
            run_demo.log("❌ Port unavailable")
            self.assertNotIn("\033[", stream.getvalue())

    def test_resolved_ports_and_ipv6_urls(self) -> None:
        value = config()
        value["services"]["api"]["ports"][0]["host_ip"] = "::1"
        ports = run_demo.published_ports(value)
        self.assertEqual(run_demo.service_url(ports, "api", 8000), "http://[::1]:18000")
        self.assertEqual(run_demo.service_url(ports, "ui", 8501), "http://localhost:18501")

    def test_invalid_port_rejected(self) -> None:
        value = config()
        for port in ["invalid", "8000-8010", "70000"]:
            with self.subTest(port=port):
                value["services"]["api"]["ports"][0]["published"] = port
                with self.assertRaises(RuntimeError):
                    run_demo.published_ports(value)

    def test_owned_port_exemption_is_scoped(self) -> None:
        port = run_demo.PublishedPort("api", "127.0.0.1", 8000, 8000)
        with patch.object(run_demo, "port_available", return_value=False) as probe:
            self.assertTrue(run_demo.check_ports([port], {("api", "127.0.0.1", 8000)}))
            probe.assert_not_called()
            self.assertFalse(run_demo.check_ports([port], {("other", "127.0.0.1", 8000)}))
            self.assertFalse(run_demo.check_ports([port], {("api", "127.0.0.2", 8000)}))

    def test_detect_stale_ports_identifies_changed_container_bindings(self) -> None:
        ports = [
            run_demo.PublishedPort("api", "0.0.0.0", 8000, 8000),
            run_demo.PublishedPort("ui", "0.0.0.0", 8501, 8501),
        ]
        # Container is publishing port 8001 instead of 8000
        containers = [
            {
                "Service": "api",
                "Publishers": [{"URL": "0.0.0.0", "PublishedPort": 8001, "Protocol": "tcp"}],
            },
            {
                "Service": "ui",
                "Publishers": [{"URL": "0.0.0.0", "PublishedPort": 8501, "Protocol": "tcp"}],
            },
        ]
        warnings = run_demo.detect_stale_ports(ports, containers)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Stale binding for api", warnings[0])
        self.assertIn("8001", warnings[0])

    def test_detect_stale_ports_clean_when_matching(self) -> None:
        ports = [run_demo.PublishedPort("api", "0.0.0.0", 8000, 8000)]
        containers = [
            {
                "Service": "api",
                "Publishers": [{"URL": "0.0.0.0", "PublishedPort": 8000, "Protocol": "tcp"}],
            }
        ]
        warnings = run_demo.detect_stale_ports(ports, containers)
        self.assertEqual(warnings, [])

    def test_detect_missing_ports_identifies_unbound_expected_ports(self) -> None:
        ports = [
            run_demo.PublishedPort("api", "0.0.0.0", 8000, 8000),
            run_demo.PublishedPort("ui", "0.0.0.0", 8501, 8501),
        ]
        # api container is running but has no publishers, or different publisher
        containers = [
            {"Service": "api", "Publishers": []},
            {
                "Service": "ui",
                "Publishers": [{"URL": "0.0.0.0", "PublishedPort": 8501, "Protocol": "tcp"}],
            },
        ]
        warnings = run_demo.detect_missing_ports(ports, containers)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Missing binding for api", warnings[0])
        self.assertIn("8000", warnings[0])

    def test_detect_missing_ports_empty_when_no_containers_running(self) -> None:
        ports = [run_demo.PublishedPort("api", "0.0.0.0", 8000, 8000)]
        warnings = run_demo.detect_missing_ports(ports, [])
        self.assertEqual(warnings, [])

    def test_detect_missing_ports_clean_when_all_bound(self) -> None:
        ports = [run_demo.PublishedPort("api", "0.0.0.0", 8000, 8000)]
        containers = [
            {
                "Service": "api",
                "Publishers": [{"URL": "0.0.0.0", "PublishedPort": 8000, "Protocol": "tcp"}],
            }
        ]
        warnings = run_demo.detect_missing_ports(ports, containers)
        self.assertEqual(warnings, [])

    def test_port_conflicts_detection_logs_actionable_advice(self) -> None:
        ports = [
            run_demo.PublishedPort("api", "0.0.0.0", 8000, 8000),
            run_demo.PublishedPort("grafana", "127.0.0.1", 3000, 3000),
        ]
        with (
            patch.object(run_demo, "port_available", side_effect=lambda h, p: p != 8000),
            patch.object(run_demo, "log") as mock_log,
        ):
            available = run_demo.check_ports(ports, set())
            self.assertFalse(available)
            logged = [call.args[0] for call in mock_log.call_args_list]
            self.assertTrue(any("api: port 0.0.0.0:8000 is unavailable" in msg for msg in logged))
            self.assertTrue(any("API_PORT in .env" in msg for msg in logged))

    def test_compose_ps_accepts_array_lines_and_empty_output(self) -> None:
        container = {
            "Service": "api",
            "Publishers": [
                {"URL": "0.0.0.0", "PublishedPort": 18000, "Protocol": "tcp"},
            ],
        }
        for raw in [json.dumps([container]), json.dumps(container) + "\n", ""]:
            with (
                self.subTest(raw=raw),
                patch.object(
                    run_demo.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess([], 0, raw),
                ),
            ):
                result = run_demo.owned_ports(run_demo.compose_json("ps"))
                self.assertEqual(result, {("api", "0.0.0.0", 18000)} if raw else set())

    def test_compose_errors_are_actionable_without_dumping_config(self) -> None:
        for response in [
            subprocess.CompletedProcess([], 1, "secret-value"),
            subprocess.CompletedProcess([], 0, "not-json"),
        ]:
            with (
                self.subTest(response=response),
                patch.object(
                    run_demo.subprocess,
                    "run",
                    return_value=response,
                ),
            ):
                with self.assertRaises(RuntimeError) as caught:
                    run_demo.compose_json("config")
                self.assertNotIn("secret-value", str(caught.exception))

    def test_missing_or_hung_commands(self) -> None:
        for error in [FileNotFoundError(), subprocess.TimeoutExpired("docker", 15)]:
            with (
                self.subTest(error=error),
                patch.object(
                    run_demo.subprocess,
                    "run",
                    side_effect=error,
                ),
            ):
                self.assertFalse(run_demo.check_command(["docker", "info"]))
                with self.assertRaises(RuntimeError):
                    run_demo.compose_json("config")

    def test_ollama_requires_configured_model(self) -> None:
        with patch.object(run_demo.urllib.request, "urlopen", side_effect=self.response):
            self.assertTrue(run_demo.check_ollama("gemma4:e2b"))
            self.assertFalse(run_demo.check_ollama("gemma4:other"))

    def test_ollama_missing_and_malformed(self) -> None:
        for body in [b"not-json", b'{"models": []}', b'{"models": null}']:
            with (
                self.subTest(body=body),
                patch.object(
                    run_demo.urllib.request,
                    "urlopen",
                    return_value=Response(body),
                ),
            ):
                self.assertFalse(run_demo.check_ollama("gemma4:e2b"))
        with patch.object(run_demo.urllib.request, "urlopen", side_effect=OSError):
            self.assertFalse(run_demo.check_ollama("gemma4:e2b"))

    def test_query_modes_never_start_compose_or_browser(self) -> None:
        for mode in ["--check-only", "--status"]:
            with (
                self.subTest(mode=mode),
                patch.object(
                    run_demo.sys,
                    "argv",
                    [str(SCRIPT), mode],
                ),
                patch.object(run_demo.subprocess, "run", side_effect=self.command) as command,
                patch.object(
                    run_demo.urllib.request,
                    "urlopen",
                    side_effect=self.response,
                ),
                patch.object(run_demo, "port_available", return_value=True),
                patch.object(
                    run_demo.webbrowser,
                    "open",
                ) as browser,
            ):
                self.assertEqual(run_demo.main(), 0)
                self.assertFalse(any("up" in call.args[0] for call in command.call_args_list))
                browser.assert_not_called()

    def test_port_conflict_blocks_launch_without_prompt_in_scripts(self) -> None:
        with (
            patch.object(run_demo.sys, "argv", [str(SCRIPT), "--non-interactive"]),
            patch.object(
                run_demo.subprocess,
                "run",
                side_effect=self.command,
            ) as command,
            patch.object(run_demo.urllib.request, "urlopen", side_effect=self.response),
            patch.object(
                run_demo,
                "port_available",
                return_value=False,
            ),
            patch("builtins.input") as prompt,
        ):
            self.assertEqual(run_demo.main(), 1)
            self.assertFalse(any("up" in call.args[0] for call in command.call_args_list))
            prompt.assert_not_called()

    def test_status_reports_unhealthy_without_wait_loop(self) -> None:
        with (
            patch.object(run_demo.sys, "argv", [str(SCRIPT), "--status"]),
            patch.object(
                run_demo.subprocess,
                "run",
                side_effect=self.command,
            ),
            patch.object(run_demo.urllib.request, "urlopen", side_effect=OSError),
            patch.object(
                run_demo.time,
                "sleep",
            ) as sleep,
        ):
            self.assertEqual(run_demo.main(), 1)
            sleep.assert_not_called()

    def test_no_browser_preserves_all_five_health_checks(self) -> None:
        with (
            patch.object(run_demo.sys, "argv", [str(SCRIPT), "--no-browser"]),
            patch.object(
                run_demo.subprocess,
                "run",
                side_effect=self.command,
            ) as command,
            patch.object(run_demo.urllib.request, "urlopen", side_effect=self.response) as http,
            patch.object(
                run_demo,
                "port_available",
                return_value=True,
            ),
            patch.object(run_demo.webbrowser, "open") as browser,
        ):
            self.assertEqual(run_demo.main(), 0)
            self.assertTrue(any("up" in call.args[0] for call in command.call_args_list))
            self.assertEqual(http.call_count, 6)  # Ollama + all five existing health endpoints.
            browser.assert_not_called()

    def test_missing_docker_exits_with_diagnostics(self) -> None:
        with (
            patch.object(run_demo.sys, "argv", [str(SCRIPT), "--check-only"]),
            patch.object(run_demo.subprocess, "run", side_effect=FileNotFoundError) as command,
        ):
            self.assertEqual(run_demo.main(), 1)
            self.assertEqual(command.call_count, 1)

    def test_missing_model_fails_check_only_but_preserves_normal_fallback(self) -> None:
        for mode in ["--check-only", "--no-browser"]:
            with (
                self.subTest(mode=mode),
                patch.object(run_demo.sys, "argv", [str(SCRIPT), mode]),
                patch.object(run_demo.subprocess, "run", side_effect=self.command) as command,
                patch.object(
                    run_demo.urllib.request,
                    "urlopen",
                    side_effect=lambda *args, **kwargs: Response(b'{"models": []}'),
                ),
                patch.object(run_demo, "port_available", return_value=True),
            ):
                self.assertEqual(run_demo.main(), 1 if mode == "--check-only" else 0)
                started = any("up" in call.args[0] for call in command.call_args_list)
                self.assertEqual(started, mode != "--check-only")

    def test_failed_readiness_does_not_report_success_or_open_browser(self) -> None:
        with (
            patch.object(run_demo.sys, "argv", [str(SCRIPT)]),
            patch.object(run_demo.subprocess, "run", side_effect=self.command),
            patch.object(run_demo.urllib.request, "urlopen", side_effect=self.response),
            patch.object(run_demo, "port_available", return_value=True),
            patch.object(run_demo, "wait_for_url", side_effect=[True, False, True, True, True]),
            patch.object(run_demo.webbrowser, "open") as browser,
        ):
            self.assertEqual(run_demo.main(), 1)
            browser.assert_not_called()


if __name__ == "__main__":
    unittest.main()
