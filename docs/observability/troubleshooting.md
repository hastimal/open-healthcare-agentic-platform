# Observability Troubleshooting Guide

This guide details steps to identify and resolve missing telemetry, unexported spans, and disconnected metric scrapers.

---

## 1. Traces Not Appearing in Tempo or Grafana

### Symptoms
- An API query completes, but searching for the `trace_id` in Tempo returns `404 Not Found`.

### Diagnostics
1. Check if the OpenTelemetry exporter is enabled in the API:
   ```bash
   # Check logs for OTLP exporter connection errors
   kubectl logs deployment/open-healthcare-api -n open-healthcare | grep -i otel
   ```
2. Verify OTel Collector is receiving spans:
   ```bash
   kubectl logs deployment/otel-collector -n open-healthcare
   ```
3. Test Tempo readiness directly:
   ```bash
   curl -s http://localhost:3200/ready
   ```

---

## 2. Missing Prometheus Metrics

### Symptoms
- Prometheus returns empty results for `healthcare_search_requests_total`.

### Diagnostics
1. Verify API exposes `/metrics`:
   ```bash
   curl -s http://localhost:8000/metrics | grep healthcare
   ```
2. Check Prometheus target scrape status:
   - Visit `http://localhost:9090/targets`.
   - Confirm endpoint `open-healthcare-api` has state `UP`.
