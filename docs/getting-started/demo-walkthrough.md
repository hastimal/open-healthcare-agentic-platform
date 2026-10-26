# Detailed Clinical Demo Walkthrough

This walkthrough demonstrates an evidence-grounded healthcare discovery query from initiation through multi-source retrieval, validation, and citation synthesis.

---

## 1. Clinical Discovery Scenario

**Target Query**:
> *"Find cardiologists treating heart failure in Boston, MA"*

### Objective
1. Locate licensed clinical cardiologists in Boston, MA.
2. Retrieve current peer-reviewed clinical research on heart failure interventions from PubMed.
3. Ground patient health education guidelines from MedlinePlus.
4. Execute deterministic validation to ensure evidence veracity.
5. Synthesize a unified, cited medical briefing.

---

## 2. Step-by-Step Execution

### Step 1: Preflight Verification
Verify environment readiness and inference connectivity:
```bash
uv run healthcare-agents check
```
Expected output:
```text
✅ Python Version: Python 3.12.x
✅ Inference Endpoint (Ollama): Model available
✅ Model 'gemma4:e2b': Model 'gemma4:e2b' found
```

### Step 2: Query Submission
Submit the search request via the REST API:
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Find cardiologists treating heart failure in Boston, MA"}'
```

### Step 3: Inspecting Execution Events
The response JSON contains an `execution_events` timeline detailing each agent step:
1. **Planner Agent**: Gemma 4 deconstructs the request into targeted sub-queries.
2. **NPPES Retrieval**: Connects to CMS NPI Registry to find matching provider records.
3. **PubMed Retrieval**: Queries NCBI for clinical trials on heart failure management.
4. **MedlinePlus Retrieval**: Fetches patient education summaries on cardiovascular disease.
5. **Deterministic Validator**: Verifies provider NPIs and schema conformance.
6. **Grounded Synthesis**: Gemma 4 generates a referenced synthesis.

---

## 3. Reviewing Citations and Provenance

Every factual claim in the generated answer includes an explicit marker:
- Providers: `[NPPES-Live: NPI:...]`
- Literature: `[PubMed-Live: PMID:40360446]`
- Patient Education: `[MedlinePlus-Live: MedlinePlus:heartdiseases]`

> **Notice**: This platform is designed strictly for research, educational, and developer exploration. It does not provide medical advice or establish a doctor-patient relationship.
