# Antigravity Milestone Documentation Index

This directory maintains the historical documentation, execution records, implementation details, and verification logs for all platform milestones according to the project rules defined in [AGENTS.md](../../AGENTS.md).

---

## Milestone Index

| Milestone | Target Tag | Description | Status |
|:---|:---|:---|:---|
| [M01-foundation](./M01-foundation/) | `v0.1.0-m01` | Repository Foundation, Python 3.12 Packaging, CLI, Tests & CI | Complete |
| [M02-gemma-ollama](./M02-gemma-ollama/) | `v0.2.0-m02` | Local Gemma 4 Serving via Ollama & Model Adapter Interface | Complete |
| [M03-langgraph-agents](./M03-langgraph-agents/) | `v0.3.0-m03` | LangGraph Multi-Agent Orchestration & Grounded Discovery | Complete |
| [M04A-nppes](./M04A-nppes/) | `v0.4.0-m04a` | Live Public NPPES NPI Registry Provider Discovery (API v2.1) | Complete |
| [M04B-pubmed](./M04B-pubmed/) | `v0.4.1-m04b` | Live PubMed Biomedical Research Literature Discovery | Complete |
| [M04C-cms](./M04C-cms/) | `v0.4.2-m04c` | CMS Provider Data Clinician & Facility Quality Metrics | Complete |
| [M04D-medlineplus](./M04D-medlineplus/) | `v0.4.3-m04d` | Live NLM MedlinePlus Patient Education & Health Topics | Complete |
| [M04E-unified-evidence](./M04E-unified-evidence/) | `v0.4.4-m04e` | Unified Evidence Normalization, Ranking, Deduplication & Provenance | Complete |
| [M05-fastapi-streamlit](./M05-fastapi-streamlit/) | `v0.5.0-m05` | FastAPI REST Service & Streamlit Interactive Web Application | Complete |
| [M06-docker-compose](./M06-docker-compose/) | `v0.6.0-m06` | Docker Compose Multi-Profile Containerization | Complete |
| [M06-1-ui-observability](./M06-1-ui-observability/) | `feature/m06-1-ui-observability` | UI Experience, Patient Education Formatting & Agent Execution Observability | Verified |
| [M07-parallel-query-fanout](./M07-parallel-query-fanout/) | `v0.7.0-m07` | Intelligent Query Fan-Out, Parallel Retrieval, Relevance & Workflow Graph | Complete |
| [M08-observability](./M08-observability/) | `v0.8.0-m08` | OpenTelemetry SDK, OTel Collector, Prometheus, Tempo & Grafana Dashboards | Complete |
| [M09-kubernetes](./M09-kubernetes/) | `v0.9.0-m09` | Kubernetes-Native Deployment, Kustomize, Kind Cluster & Observability | Complete |
| [M10-distribution](./M10-distribution/) | `v0.10.0-m10` | Helm, Packaging & One-Command Distribution (GHCR, Helm, PyPI CLI) | Complete |
| [M10.1-release-polish](./M10-distribution/07-release-polish-and-pypi-images.md) | `v0.10.1-m10.1` | PyPI README Images Fix, CLI Version Correction & Release Polish | Complete |
| [M10.2-documentation](./M10.2-documentation/11-final-acceptance.md) | `docs/m10-2-cncf-documentation-overhaul` | CNCF-Ready Documentation, Developer Experience & Final Quality Audit | Complete |

---

## Structure per Milestone

Incremental contributions also record their scope and evidence:

- [Issue 12: demo diagnostics](./issue-12-diagnostics/implementation.md),
  [requirements](./issue-12-diagnostics/prompt.md),
  [commands](./issue-12-diagnostics/commands.md) and
  [verification](./issue-12-diagnostics/verification.md).

Each milestone documentation folder contains:
1. `prompt.md`: Complete original prompt and requirements.
2. `commands.md`: Exact commands executed during development and validation.
3. `implementation.md`: File changes, package structure, and technical choices.
4. `verification.md`: Complete test outputs, coverage reports, package builds, and CI status.
