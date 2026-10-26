# Grafana Dashboards

This guide covers Grafana visualization, dashboard navigation, and telemetry inspection.

---

## 1. Accessing Grafana

When running via Docker Compose or Kubernetes, Grafana is available at:
- **URL**: `http://localhost:3000`
- **Default Credentials**: `admin` / `admin` (or auto-login if anonymous access is enabled in dev)

---

## 2. Pre-Provisioned Dashboards

1. **Healthcare Operations Dashboard**:
   - Request rates by endpoint (`/api/v1/search`, `/health`).
   - Latency percentiles (p50, p95, p99).
   - Error rates and fallback activations.
2. **Multi-Agent Execution Dashboard**:
   - Query fan-out count per request.
   - External retrieval durations (NPPES vs. PubMed vs. MedlinePlus).
   - Validation success rate and token usage tracking.

---

## 3. Investigating Traces

Grafana is pre-configured with the **Tempo** datasource.
- Navigate to **Explore** -> Select **Tempo**.
- Enter a `trace_id` returned from an API search query.
- View the full waterfall execution of agents, retrievers, and LLM inference spans.
