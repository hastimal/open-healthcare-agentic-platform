# Quickstart

Get the demo running locally in a few minutes. For the full contributor guide
see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Docker Desktop (macOS/Windows) or Docker Engine + Compose v2 (Linux)
- Native [Ollama](https://ollama.com/download) with the `gemma4:e2b` model

```bash
ollama serve          # in its own terminal
ollama pull gemma4:e2b
```

## Run

```bash
uv sync
cp .env.example .env
uv run python scripts/run_demo.py
```

The launcher runs preflight checks before starting anything:

| Check | What it does |
| --- | --- |
| Docker | Confirms the CLI, daemon and Compose v2 plugin are usable |
| Ollama | Confirms native Ollama answers and the model is installed |
| Ports | Confirms 8000, 8501, 3000, 9090, 3200, 4317 and 4318 are free |

Every failure prints a colour-coded fix and, when interactive, asks whether to
continue. Use `--non-interactive` in CI or scripts, `--skip-ollama-check` and
`--skip-port-check` to bypass individual checks, and `--no-browser` to keep the
launcher from opening a tab.

## Troubleshooting

**Port already in use** — find and stop the process, or change the matching
port in `.env`:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN      # macOS / Linux
netstat -ano | findstr :8000          # Windows
```

**Ollama not reachable** — start it with `ollama serve` and confirm
`curl http://localhost:11434/api/tags` responds.

**Model missing** — run `ollama pull gemma4:e2b`.

**Linux containers cannot reach Ollama** — `host.docker.internal` is not
resolved by default. Add the host gateway mapping to the services that need it:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Windows** — run everything inside a WSL2 distro with Docker Desktop WSL
integration enabled.

## Stop

```bash
docker compose down
```
