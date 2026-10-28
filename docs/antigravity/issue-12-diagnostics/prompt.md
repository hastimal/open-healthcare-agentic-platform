# Original public issue requirements

Source: https://github.com/hastimal/open-healthcare-agentic-platform/issues/12

## 1. Background
The platform provides a one-command demonstration launcher (`scripts/run_demo.py`) and development environment powered by Python 3.12, `uv`, Docker Compose, and native Ollama. Streamlining onboarding for contributors on diverse operating systems (Linux, macOS, Windows WSL2) will accelerate community contributions.

## 2. Problem Statement
First-time contributors occasionally encounter environment friction, such as Docker Desktop networking differences on Linux vs. macOS (`host.docker.internal`), missing Ollama models, or conflicting port bindings (e.g. port 3000 or 8000 already in use).

## 3. Objective
Enhance developer experience by adding cross-platform diagnostic checks to `scripts/run_demo.py`, providing interactive troubleshooting prompts, improving error messaging, and authoring a streamlined quickstart onboarding guide.

## 4. Current Implementation Context
- Launcher: `scripts/run_demo.py` (validates Docker, native Ollama, starts Compose, verifies health, opens browser).
- Sidebar Developer Hub in Streamlit UI: `src/healthcare_agents/ui/components.py`.
- Developer documentation in `CONTRIBUTING.md`.

## 5. Proposed Architecture or Approach
- Enhance `scripts/run_demo.py` with:
  - Port availability checking prior to Docker Compose startup (detects port conflicts on 8000, 8501, 3000, 9090, 3200, 4317, 4318).
  - Clear, color-coded troubleshooting guidance if native Ollama is missing or if `gemma4:e2b` is not installed.
  - Interactive or non-interactive flag support (`--check-only`, `--status`).
- Provide automated `make` or `uv run` shortcut tasks in `pyproject.toml` / `Makefile`.
- Expand `CONTRIBUTING.md` with operating-system specific setup tips (macOS Apple Silicon, Ubuntu/Debian Linux, Windows WSL2).

## 6. Suggested Implementation Steps
1. Add socket port conflict pre-checks in `scripts/run_demo.py`.
2. Add detailed diagnostic output explaining resolution when a check fails.
3. Add a dedicated troubleshooting section in `docs/developer-guide.md`.
4. Test launcher behavior on macOS and Linux environments.

## 7. Expected Deliverables
- Updated `scripts/run_demo.py`.
- Troubleshooting guide in `docs/developer-guide.md`.
- Enhanced `CONTRIBUTING.md`.

## 8. Acceptance Criteria
- [ ] `scripts/run_demo.py` detects port conflicts before starting Compose and displays actionable resolution advice.
- [ ] If Ollama or Gemma 4 is not available, the launcher prints clear instructions on how to install and serve them.
- [ ] All existing launcher flags (`--no-browser`) continue to operate without regressions.
- [ ] Setup documentation is verified on both macOS and Linux.
- [ ] All code formatting and test quality gates pass cleanly.

## 9. Testing Requirements
- Unit tests for launcher diagnostic helper functions.
- Simulated port conflict tests.

## 10. Relevant Files and Modules
- `scripts/run_demo.py`
- `CONTRIBUTING.md`
- `pyproject.toml`

## 11. Dependencies
- Depends on completed M8 baseline.

## 12. Out-of-Scope Items
- Rewriting or replacing `scripts/run_demo.py` with another launcher.

## 13. Difficulty
Beginner to Intermediate

## 14. Priority
Medium

## Contribution scope

Implement the diagnostics and developer documentation while preserving the existing launcher. Verify actual results and report unavailable OS/service checks honestly. This contribution is voluntary; no payment or release is requested.
