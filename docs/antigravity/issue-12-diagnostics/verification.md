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
