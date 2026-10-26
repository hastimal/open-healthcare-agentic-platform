# AI Model Integration Architecture

This document covers model serving, adapters, fallback mechanics, and local inference execution for Gemma 4.

---

## 1. Supported Model Families

The platform natively integrates with Google DeepMind's Gemma 4 open weights models served locally via Ollama:

1. **`gemma4:e2b`**:
   - Quantized lightweight parameter model.
   - Low latency (~500ms initial token), ideal for JSON schema planning, query decomposition, and fast answer synthesis.
2. **`gemma4:12b`**:
   - High-capacity 12-billion parameter model.
   - Deep biomedical comprehension, ideal for multifaceted clinical trial synthesis and comparative literature analysis.

---

## 2. Model Adapter Architecture (`healthcare_agents.models`)

- **`BaseModelAdapter`**: Abstract interface defining completion, structured schema generation, and health check contracts.
- **`OllamaAdapter`**: Async HTTP client communicating with Ollama `/api/generate` and `/api/tags`.
- **JSON Schema Enforcement**: Leverages Ollama's `format="json"` constraint combined with Pydantic schema validation to ensure predictable structured outputs from the Planner Agent.
- **Failover Logic**: When configured, if the primary model encounters timeouts or out-of-memory states, the system can automatically downgrade to fallback models.
