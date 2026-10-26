# Tempo Distributed Traces

This guide covers Grafana Tempo distributed tracing integration and trace inspection.

---

## 1. Accessing Tempo

- **HTTP Query Endpoint**: `http://localhost:3200`
- **Ready Endpoint**: `curl -s http://localhost:3200/ready`

---

## 2. Ingesting Traces

Traces are generated via OpenTelemetry and forwarded through the OTel Collector to Tempo:
1. Client makes request to `/api/v1/search`.
2. Trace context (`traceparent`) is propagated across agent tasks.
3. Spans are pushed asynchronously to `:4318/v1/traces`.
4. OTel Collector batches and exports spans to Tempo via OTLP gRPC/HTTP.

---

## 3. Querying Traces by ID

You can query Tempo directly using `curl`:
```bash
curl -s http://localhost:3200/api/traces/<trace_id>
```
Or view the trace visually in Grafana's Explore tab under the **Tempo** datasource.
