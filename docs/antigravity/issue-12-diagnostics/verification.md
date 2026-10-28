# Verification and limits

- Windows Python 3.13.14: 19 launcher tests pass. A real Docker-unavailable
  diagnostic invocation returns 1 without a traceback.
- Linux / WSL Python 3.12.3: launcher behavior and package integration are
  exercised by the offline pytest suite. Unit tests isolate Docker, Ollama and
  browser boundaries, with a real local socket conflict test.
- Ruff lint, Ruff formatting and strict mypy checks pass.
- Wheel and source distribution build successfully.
- New launcher tests fail on unchanged upstream main, confirming missing
  diagnostic modes/helpers and Windows output handling on that revision.

The final offline suite passes: **228 passed, 17 skipped, 2 deselected**, with
**90.11% coverage** and one upstream Starlette deprecation warning. The coverage
threshold remains 90%. The unchanged upstream checkout reproduced the earlier
89.99% result. A source-checkout version regression test now also checks that
missing installed package metadata falls back to the version in `pyproject.toml`,
guarding the earlier release/version onboarding problem.

The default telemetry configuration attempts to export to an absent local
collector during shutdown and prints connection/retry warnings. These are not
passing live-service checks. Full command results are in [commands.md](commands.md).

Docker Desktop's daemon is not running in this environment, so no full Compose
build/start or live Ollama inference is claimed. The Compose configuration itself
was parsed successfully with the real CLI. No macOS hardware was available:
the new macOS CI job must run after maintainer approval, and full macOS setup
verification remains a maintainer check. Live tests and unavailable Kubernetes
tool checks are reported separately, not counted as passing.

No clinical/retrieval behavior, PHI, credentials or model weights are changed.
Diagnostics do not print resolved Compose environment values. GitHub CI status
must be checked on the published PR; local checks do not imply CI has passed.

## Integration Polish Verification
- `test_run_demo.py`: 25 unit tests passed via `python -m unittest discover -s tests -p "test_run_demo.py" -v` in 0.012s.
- Regression tests added:
  - `test_detect_stale_ports_identifies_changed_container_bindings` (verifies detection of stale published ports)
  - `test_detect_stale_ports_clean_when_matching` (verifies no false positives on clean bindings)
  - `test_detect_missing_ports_identifies_unbound_expected_ports` (verifies detection when expected ports are missing)
  - `test_detect_missing_ports_empty_when_no_containers_running` (verifies clean state when no containers exist)
  - `test_detect_missing_ports_clean_when_all_bound` (verifies matching container publishers)
  - `test_port_conflicts_detection_logs_actionable_advice` (verifies conflict messaging and .env guidance)
- Full pytest suite: 238 passed, 15 skipped, 1 warning, 17 subtests passed with 90.11% total coverage (meets >=90.0% threshold).
- Linters: `ruff check .`, `ruff format --check .`, and `mypy src scripts/run_demo.py tests/test_run_demo.py` passed with 0 errors across 51 source files.
- Live macOS Docker Compose verification:
  - Docker daemon (v29.9.2) and Compose plugin (v5.6.1) active.
  - Successfully built and launched stack (`api`, `ui`, `otel-collector`, `prometheus`, `tempo`, `grafana`).
  - Readiness verified for FastAPI (`/health` -> HTTP 200), Streamlit UI (`/_stcore/health` -> HTTP 200), Prometheus (`/-/healthy` -> HTTP 200), Tempo (`/ready` -> HTTP 200), and Grafana (`/api/health` -> HTTP 200).
  - Validated live port override conflict detection: overriding `API_PORT=8006` while container published 8005 accurately triggered both `⚠️ Stale binding for api` and `⚠️ Missing binding for api: Compose config specifies 0.0.0.0:8006`.
  - Stack cleanly torn down with `docker compose down`.

