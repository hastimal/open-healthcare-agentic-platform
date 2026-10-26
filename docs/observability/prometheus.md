# Prometheus Metrics

This guide covers Prometheus metric collection, scraping configuration, and custom healthcare metrics.

---

## 1. Accessing Prometheus

- **URL**: `http://localhost:9090`
- **Health Check**: `curl -s http://localhost:9090/-/healthy`

---

## 2. Key Healthcare Platform Metrics

| Metric Name | Type | Description |
| :--- | :--- | :--- |
| `healthcare_search_requests_total` | Counter | Total healthcare search queries processed |
| `healthcare_retrieval_duration_seconds` | Histogram | Latency distribution of external healthcare API calls |
| `healthcare_agent_execution_seconds` | Histogram | Duration of multi-agent stages (Planner, Synthesizer) |
| `healthcare_validation_failures_total` | Counter | Deterministic validation rule violations caught |
| `gen_ai_client_token_usage_total` | Counter | Token consumption for local inference |

---

## 3. Querying Metrics

To query total search requests in Prometheus:
```promql
healthcare_search_requests_total
```
To calculate p95 search latency:
```promql
histogram_quantile(0.95, sum(rate(healthcare_agent_execution_seconds_bucket[5m])) by (le))
```
