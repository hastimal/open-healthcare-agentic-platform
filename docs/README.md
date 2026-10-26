# Open Healthcare Agentic Platform Documentation Index

Welcome to the documentation for the **Open Healthcare Agentic Platform**, an open-source, vendor-neutral, evidence-grounded AI platform for healthcare discovery and clinical research.

---

## Documentation Categories

### 🚀 Getting Started
- [Platform Installation & Quick Start](getting-started/installation.md): Installation options via PyPI, `uvx`, Docker Compose, Kubernetes, and Helm.
- [First Healthcare Agent Walkthrough](getting-started/first-demo.md): Quick start guide to running a clinical discovery query.
- [Detailed Clinical Demo Walkthrough](getting-started/demo-walkthrough.md): Comprehensive walkthrough of query planning, retrieval fan-out, citations, and traces.
- [CLI Reference Guide](getting-started/cli-reference.md): Complete reference for the `healthcare-agents` command line interface.
- [Configuration Reference](getting-started/configuration.md): Complete environment variables, inference models, and port settings.
- [Troubleshooting Guide](getting-started/troubleshooting.md): Diagnosing port conflicts, Ollama connectivity, Docker/K8s errors, and telemetry issues.

### 🏛️ Architecture & Core Concepts
- [Architecture Overview](architecture/overview.md): System architecture, multi-agent engine, and design principles.
- [Multi-Agent Orchestration](architecture/agents.md): Gemma 4 planner, parallel fan-out, and synthesis agents.
- [Healthcare Data Retrieval](architecture/retrieval.md): NPPES NPI Registry, PubMed, CMS Provider Data, and MedlinePlus integration.
- [AI Model Integration](architecture/models.md): Local Ollama serving, Gemma 4 models, and structured JSON output contracts.
- [Observability Architecture](architecture/observability.md): OpenTelemetry collector, tracing spans, and metric pipelines.
- [Deployment Architecture](architecture/deployment.md): Multi-arch container builds, non-root security, and cloud-native topologies.

### ☸️ Deployment & Cloud-Native
- [Kubernetes & Helm Deployment Guide](deployment/kubernetes.md): Declarative Kustomize manifests, Kind local testing, in-cluster `host-ollama-bridge`, and Helm OCI installation.

### 📊 Observability & Reliability
- [OpenTelemetry Observability Overview](observability/README.md): W3C distributed tracing, Prometheus metrics, Grafana dashboards, and Tempo trace explorer.
- [Grafana Dashboards](observability/grafana.md): Pre-provisioned dashboards, explore view, and metric widgets.
- [Prometheus Metrics](observability/prometheus.md): Exposed metric endpoints, PromQL queries, and scraping setups.
- [Tempo Distributed Traces](observability/tempo.md): Trace ingestion, span waterfalls, and query interfaces.
- [Observability Troubleshooting](observability/troubleshooting.md): Diagnosing missing spans, OTLP collector drops, and scrape timeouts.

### 🛠️ Development & Community
- [Contributor Guide](../CONTRIBUTING.md): Local development workflow, code standards, testing gates, and PR guidelines.
- [Local Development Guide](getting-started/development.md): Detailed local setup, testing commands, and package build workflows.
- [Historical Milestones Index](antigravity/README.md): Chronological execution records and verification evidence from M1 through M10.2.
