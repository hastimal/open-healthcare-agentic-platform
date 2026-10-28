# Commands and raw verification output

Commands were run from the repository root. Linux uses Ubuntu 24.04 / Python
3.12.3 under WSL; Windows uses Python 3.13.14. Verification details and limitations
are recorded in [verification.md](verification.md).

```text
python -m unittest discover -s tests -p test_run_demo.py -v
Ran 19 tests in 0.011s
OK

ruff check .
All checks passed!

ruff format --check .
217 files already formatted

mypy src tests scripts/run_demo.py
Success: no issues found in 85 source files

python -m build
Successfully built open_healthcare_agentic_platform-0.10.2.tar.gz and open_healthcare_agentic_platform-0.10.2-py3-none-any.whl
```

Before the source-checkout version regression was added, the locked-environment
suite ran 227 passing tests but failed the coverage gate at 89.99%. A separate
unchanged-upstream checkout reproduced 89.99% (208 passing tests). No threshold
was lowered and no files were excluded to hide that result.

```text
pytest -m "not live" --cov=healthcare_agents --cov-report=term-missing
TOTAL                                                     4217    417    90%
Required test coverage of 90.0% reached. Total coverage: 90.11%
228 passed, 17 skipped, 2 deselected, 1 warning, 17 subtests passed in 36.55s
```

The final suite used dependencies from the unchanged `uv.lock`, installed with
`uv sync --frozen --extra dev --no-default-groups --python /usr/bin/python3.12`
and `UV_PROJECT_ENVIRONMENT=/opt/healthcare-12-locked`. The later attempt with
`OTEL_ENABLED=false` did not improve coverage; the final run uses the default
telemetry configuration. No runtime telemetry setting is changed by this PR.

```text
docker info --format '{{.OSType}}'
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine

docker compose config --format json
```

The configuration command succeeded and resolved API/UI plus all observability
publishers, including collector port 8889. Its full JSON is intentionally not
published because resolved Compose configuration can contain environment values.
The real Windows `--check-only --non-interactive` command returned 1 with Docker
startup instructions and no traceback, builds, service starts or browser opens.
