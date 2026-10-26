# Configuration Reference

This guide details all configuration options for the Open Healthcare Agentic Platform across local CLI environments, Docker Compose, and Kubernetes/Helm deployments.

---

## 1. Environment Variables Overview

The platform uses Pydantic Settings (`healthcare_agents.config.Settings`) to load environment variables from `.env` files or process environment variables.

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Endpoint for Ollama LLM inference service |
| `DEFAULT_MODEL` | `gemma4:e2b` | Default LLM model identifier |
| `FALLBACK_MODEL` | `gemma4:12b` | Fallback model if primary model fails |
| `FASTAPI_HOST` | `0.0.0.0` | Bind host for FastAPI backend |
| `FASTAPI_PORT` | `8000` | Port for FastAPI service |
| `STREAMLIT_HOST` | `0.0.0.0` | Bind host for Streamlit UI |
| `STREAMLIT_PORT` | `8501` | Port for Streamlit UI |
| `RETRIEVAL_MODE` | `live` | Retrieval execution mode: `live` or `fixture` |
| `RETRIEVAL_TIMEOUT_SECONDS` | `10.0` | Timeout per external healthcare API call |
| `NPPES_API_URL` | `https://npiregistry.cms.hhs.gov/api/` | Base URL for CMS NPPES NPI Registry |
| `PUBMED_API_URL` | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/` | Base URL for NCBI E-Utilities |
| `MEDLINEPLUS_API_URL` | `https://wsearch.nlm.nih.gov/ws/query` | Base URL for MedlinePlus Web Search API |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:4318` | OpenTelemetry OTLP HTTP receiver endpoint |
| `OTEL_SERVICE_NAME` | `open-healthcare-platform` | OpenTelemetry service name resource attribute |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 2. Model Backend Configuration

The platform supports local inference via Ollama.

### Supported Models
- `gemma4:e2b`: Lightweight quantized Gemma 4 model optimized for fast planning and structured synthesis.
- `gemma4:12b`: 12-billion parameter model for deep synthesis and complex clinical reasoning.

### Host-to-Container Bridge
When running inside Docker or Kubernetes with an Ollama instance running on the host machine:
- **Docker Compose**: Set `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- **Kubernetes / Kind**: Use the `host-ollama-bridge` Service or set `OLLAMA_BASE_URL` to the bridge Service DNS name (`http://host-ollama-bridge.open-healthcare.svc.cluster.local:11434`).

---

## 3. Observability Configuration

Distributed tracing and metric scraping are configured via standard OpenTelemetry and Prometheus protocols:

- **FastAPI Traces**: Emitted via `opentelemetry-instrumentation-fastapi` to the OTLP HTTP receiver (`:4318/v1/traces`).
- **Prometheus Metrics**: Exposed on `/metrics` endpoint on FastAPI and scraped by Prometheus at port `9090`.
- **Tempo**: Receives traces from OTel Collector and stores them with a 24-hour block retention window.
- **Grafana**: Auto-provisions Prometheus and Tempo datasources and loads preconfigured healthcare dashboards.
