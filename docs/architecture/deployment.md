# Deployment Architecture

This document describes deployment options for the Open Healthcare Agentic Platform across Docker, Kubernetes, and Helm.

---

## 1. Container Architecture

The platform provides multi-arch container images (`linux/amd64`, `linux/arm64`) published to GitHub Container Registry (GHCR):
- `ghcr.io/hastimal/open-healthcare-api:0.10.1`: FastAPI backend and multi-agent core.
- `ghcr.io/hastimal/open-healthcare-ui:0.10.1`: Streamlit web interface.

Images run as unprivileged non-root users (`appuser:10001`) with read-only root filesystems where applicable.

---

## 2. Kubernetes and Helm Architecture

The Helm chart (`charts/open-healthcare`) bundles:
- `open-healthcare-api`: Deployment & Service with liveness (`/health`) and readiness (`/ready`) probes.
- `open-healthcare-ui`: Deployment & Service exposing Streamlit on port 8501.
- `otel-collector`: OpenTelemetry Collector daemon forwarding traces to Tempo.
- `prometheus`: Scrapes metrics from `/metrics` endpoints.
- `tempo`: Distributed tracing storage.
- `grafana`: Visual dashboards pre-provisioned with Prometheus & Tempo datasources.
- `host-ollama-bridge`: Connects in-cluster pods to host-based Ollama inference.
