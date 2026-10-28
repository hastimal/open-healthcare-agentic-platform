# Local demo diagnostics

Install the development dependencies using [CONTRIBUTING.md](../CONTRIBUTING.md),
then check prerequisites before building containers:

```bash
uv run python scripts/run_demo.py --check-only
uv run python scripts/run_demo.py --no-browser --non-interactive
uv run python scripts/run_demo.py --status
```

`make demo-check`, `make demo` and `make demo-status` are optional shortcuts when
Make is installed. The Python commands work without Make.

## Modes and exit status

- The normal launcher checks Docker, Compose and published TCP ports before
  starting the existing stack. Port conflicts stop startup. Interactive terminals
  offer a retry; redirected input and `--non-interactive` never prompt.
- `--check-only` reads configuration, checks native Ollama/the configured model
  and probes published ports. It never starts containers or opens a browser.
- `--status` checks native Ollama and each of the five service health endpoints
  once. It never builds, starts, restarts or stops containers.
- Both query modes return 0 when all their checks pass, otherwise 1. Normal
  startup also returns 1 when Compose or a service readiness check fails.
- Missing native Ollama/model remains a warning during normal startup, preserving
  the existing fallback workflow. Query modes report it as an unmet prerequisite.

The launcher uses `docker compose config --format json` so `.env`, environment
overrides and host bindings match Compose. Ports already published by containers
in this Compose project are exempt from conflict checks. Other listeners are not.
The check is advisory: another process can claim a port between preflight and startup.

## Port conflicts

The error identifies the service and host port. Inspect the listener before
stopping anything:

```bash
# macOS or Linux
lsof -nP -iTCP:8000 -sTCP:LISTEN
# Windows PowerShell
netstat -ano | findstr :8000
```

For API/UI conflicts, change `API_PORT` or `STREAMLIT_PORT` in `.env` and rerun
the launcher. For observability ports, edit the published host port in
`docker-compose.yml`. The launcher also reads those mappings for health URLs.
It does not kill processes or alter configuration for you.

## Native Ollama and host networking

Install [Ollama](https://ollama.com/download), run `ollama serve`, and in another
terminal run `ollama pull gemma4:e2b` (or the model selected in Compose).
The native check uses `http://localhost:11434/api/tags` and requires that model,
rather than accepting any model with “gemma” in its name.

- **macOS / Apple Silicon:** start Docker Desktop and keep Ollama on the host
  for native Metal inference. Containers connect through `host.docker.internal`.
- **Ubuntu / Debian:** start Docker Engine and install the Compose v2 plugin.
  Preserve the repository's `host.docker.internal:host-gateway` mapping. If a
  host service only listens on loopback, ensure it is reachable from the Docker
  network using an appropriately scoped local configuration; avoid exposing it
  to untrusted networks.
- **Windows WSL2:** enable Docker Desktop integration for the selected distro
  and run the commands there. Confirm that native Ollama is reachable from that
  distro and from Docker; `localhost` can refer to different hosts depending on
  WSL networking mode. Diagnostics run in the environment invoking the launcher.

Health probes use three-second HTTP timeouts. Docker inspection commands have
15-second timeouts; Compose build/start has a ten-minute bound. Diagnostics do
not print the resolved environment, install models, or change Docker networking.
Colors are emitted only to interactive terminals; set `NO_COLOR=1` to disable them.
