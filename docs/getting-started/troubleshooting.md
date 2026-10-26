# Troubleshooting Guide

This guide covers common errors, edge cases, and diagnostic procedures for the Open Healthcare Agentic Platform.

---

## 1. CLI and Local Runtime Issues

### Error: Port already in use
```text
❌ Port 8000 (FastAPI): Port 8000 is already in use
❌ Port 8501 (Streamlit): Port 8501 is already in use
```
**Cause**: Another instance of the platform or an existing service is already listening on ports 8000 or 8501.  
**Resolution**:
1. Check what process is using the ports:
   ```bash
   lsof -i :8000
   lsof -i :8501
   ```
2. If running via the launcher, gracefully stop it:
   ```bash
   uv run healthcare-agents stop
   ```
3. Or specify custom ports:
   ```bash
   uv run healthcare-agents start --api-port 8080 --ui-port 8502
   ```

---

### Error: Ollama connection refused
```text
❌ Inference Endpoint (Ollama): Connection refused at http://localhost:11434
```
**Cause**: The Ollama inference daemon is not running on the local host.  
**Resolution**:
1. Start the Ollama service:
   ```bash
   ollama serve
   ```
2. Verify model availability:
   ```bash
   ollama list
   ```
3. If model `gemma4:e2b` is missing:
   ```bash
   ollama pull gemma4:e2b
   ```

---

## 2. Docker Compose Issues

### Containers fail to communicate with Ollama on host
```text
httpx.ConnectError: [Errno 111] Connection refused
```
**Cause**: Container cannot resolve `host.docker.internal` or host firewall blocks port 11434.  
**Resolution**:
1. Ensure Ollama is configured to listen on all interfaces:
   ```bash
   OLLAMA_HOST=0.0.0.0:11434 ollama serve
   ```
2. In `docker-compose.yml`, verify `extra_hosts` has `host.docker.internal:host-gateway`.

---

## 3. Kubernetes / Kind Deployment Issues

### Pods in CrashLoopBackOff or ImagePullBackOff
```bash
kubectl get pods -n open-healthcare
```
**Resolution**:
1. Inspect pod events:
   ```bash
   kubectl describe pod <pod-name> -n open-healthcare
   ```
2. If using local Kind cluster without internet pull access:
   ```bash
   kind load docker-image ghcr.io/hastimal/open-healthcare-api:0.10.1 --name open-healthcare
   kind load docker-image ghcr.io/hastimal/open-healthcare-ui:0.10.1 --name open-healthcare
   ```

---

## 4. Observability & Telemetry Issues

### Traces not showing up in Tempo / Grafana
1. Verify the OpenTelemetry Collector is running:
   ```bash
   kubectl logs deployment/otel-collector -n open-healthcare
   ```
2. Verify Tempo is healthy:
   ```bash
   curl -s http://localhost:3200/ready
   ```
3. In Grafana Explore (`http://localhost:3000`), select datasource **Tempo** and enter the `trace_id` returned in the search API response JSON.
