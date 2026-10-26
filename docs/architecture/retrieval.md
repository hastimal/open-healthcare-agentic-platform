# Healthcare Data Retrieval & Grounding Architecture

This document covers the integration architecture, protocols, rate limits, and fallback strategies for healthcare data sources.

---

## 1. Supported Healthcare Sources

| Data Source | API Endpoint | Data Entity | Primary Key / Provenance |
| :--- | :--- | :--- | :--- |
| **NPPES** | CMS NPI Registry API | Healthcare Providers & Organizations | 10-digit NPI |
| **PubMed** | NCBI Entrez E-Utilities | Peer-reviewed biomedical literature | PubMed ID (`PMID`) |
| **MedlinePlus** | NLM MedlinePlus Search | Patient-friendly health education | NLM Topic URL |
| **CMS Hospital Compare** | CMS Provider Data Catalog | Facility quality & compliance metrics | CMS Certification Number (`CCN`) |

---

## 2. Resiliency & Parallel Fan-Out

External healthcare APIs can exhibit varying latency and transient failures. The `ParallelRetriever` provides:
- **Asynchronous Concurrency**: Non-blocking `asyncio.gather` with task isolation.
- **Configurable Timeouts**: Default 10.0s deadline per retrieval client.
- **Graceful Degradation**: If one source times out, other sources continue processing without aborting the overall user query.
- **Live vs. Fixture Mode**: Built-in mock fixtures enable deterministic testing and offline research without internet access.
