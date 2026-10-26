# Local Development Guide

This document describes how to set up, build, test, and contribute to the Open Healthcare Agentic Platform locally.

---

## 1. Prerequisites

- **Python**: `>=3.11` (Python 3.12 recommended)
- **uv**: Fast Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Docker**: Docker Desktop or Docker Engine with Buildx
- **Kubernetes CLI**: `kubectl`, `helm`, and `kind` (optional for K8s testing)
- **Ollama**: Local model inference runtime (`brew install ollama` or official installer)

---

## 2. Environment Setup

Clone the repository and install all dependencies:
```bash
git clone https://github.com/hastimal/open-healthcare-agentic-platform.git
cd open-healthcare-agentic-platform

# Install project and development dependencies using uv
uv sync
```

---

## 3. Running Quality Gates

Before submitting any Pull Request, ensure all local checks pass:

```bash
# 1. Linting & Code Style
uv run ruff check .
uv run ruff format --check .

# 2. Static Typing
uv run mypy src tests

# 3. Unit and Offline Integration Tests (>= 90% coverage required)
uv run pytest -m "not live"

# 4. Helm Chart Validation
helm lint charts/open-healthcare
helm template test charts/open-healthcare

# 5. Packaging & Twine Check
uv build
uvx twine check dist/*
```

---

## 4. Running the Development Server

Start the API and UI locally in development mode:
```bash
# Verify environment dependencies
uv run healthcare-agents check

# Start API and UI concurrently
uv run healthcare-agents start
```
- Streamlit UI: `http://localhost:8501`
- FastAPI Swagger Docs: `http://localhost:8000/docs`
