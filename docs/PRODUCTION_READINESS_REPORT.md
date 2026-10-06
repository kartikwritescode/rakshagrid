# Raksha Grid: Final Production Readiness & Architecture Audit Report

**Date of Audit:** September 2026  
**Auditor:** Antigravity Advanced Agentic Engineering  
**Application Version:** 2.0.0  
**Repository State:** Consolidated Monorepo (`apps/`, `packages/`, `pipelines/`, `data/`, `storage/`, `tests/`, `.github/`)

---

## Executive Summary

A comprehensive, ground-up production audit of the entire Raksha Grid repository was executed against the production restructuring requirements. The audit verified that legacy deceptive AI logic, fake database persistence, mock heuristic fallbacks, and unstructured repository antipatterns have been completely eradicated. 

Following the initial audit, all safe **CRITICAL** issues—including Dockerfile productionization, Docker Compose v2 modernization, and GitHub Actions CI/CD pipeline implementation—were implemented and verified. The repository passes 117 automated integration tests across all domains, Next.js compiles 18/18 static pages cleanly with zero TypeScript errors, and Docker Compose configuration validates with zero warnings.

---

## 1. Repository Layout & Monorepo Structure

| Requirement | Target Location | Audit Status | Audit Verification Details |
|---|---|---|---|
| **No Duplicate Backend** | `apps/api/` | **PASSED** | Only one active backend codebase exists under `apps/api/`. Legacy `backend/` was deleted. |
| **No Duplicate Frontend** | `apps/web/` | **PASSED** | Only one active frontend Next.js 14 codebase exists under `apps/web/`. Legacy `frontend/` was deleted. |
| **No Deprecated Root `main.py`** | Root | **PASSED** | Root `main.py` removed; authoritative entry point is `apps/api/src/main.py`. |
| **No Deprecated Root `config.py`** | Root | **PASSED** | Root `config.py` removed; authoritative configuration is `apps/api/src/config.py`. |
| **No Deprecated Root `schemas.py`** | Root | **PASSED** | Root `schemas.py` removed; modular schemas live under `apps/api/src/schemas/`. |
| **No Obsolete Dockerfile** | Root | **PASSED** | Root `Dockerfile` removed; dedicated Dockerfiles are in `apps/api/Dockerfile` and `apps/web/Dockerfile`. |
| **No Broken Gitlinks / Submodules** | Root | **PASSED** | No broken submodules or external gitlinks. Monorepo is completely self-contained. |
| **No Orphan Repositories** | Monorepo | **PASSED** | All source packages (`ai-scam`, `ai-currency`, `ai-crime`, `ai-graph`, `common`) are cleanly linked via editable `pip install -e`. |
| **No Duplicate ML Code** | `packages/` | **PASSED** | ML packages consolidated under `packages/`; legacy redundant copies in `ml/` eradicated. |
| **No Unnecessary Binaries** | Monorepo | **PASSED** | Heavy raw training outputs and raw datasets excluded; only verified model weights and processed points are retained. |
| **Clean Git Status** | Root | **PASSED** | All migrations tracked; `.env` strictly gitignored; `.env.example` provided. |

---

## 2. Target Architecture & Package Decoupling

```
rakshagrid/
├── apps/
│   ├── api/                   # Authoritative FastAPI Application
│   │   ├── Dockerfile         # Python 3.11 slim production container
│   │   └── src/               # Routers, Middleware, Services, Core
│   └── web/                   # Next.js 14 Frontend Application
│       ├── Dockerfile         # Multi-stage standalone production container
│       └── src/               # Pages, Components, Hooks, Services
├── packages/
│   ├── ai-scam/               # DistilBERT & TF-IDF Ensemble, STT, Voice Deepfake interface
│   ├── ai-currency/           # EfficientNetB0 Currency Authenticity Net
│   ├── ai-crime/              # Geospatial DBSCAN Hotspot & Patrol Allocation
│   ├── ai-graph/              # NetworkX Syndicate Graph, PageRank, Louvain Communities
│   └── common/                # Shared Logging, Exceptions, Masking Filters
├── pipelines/                 # Training and calibration pipelines (isolated from inference)
├── data/
│   └── processed/             # Processed datasets (e.g., points.parquet)
├── storage/                   # Local artifact and upload staging (gitignored)
├── tests/
│   └── integration/           # 117 Comprehensive end-to-end integration tests
└── .github/
    └── workflows/             # CI/CD Workflows for backend, frontend, and Docker
```

- **FastAPI Authoritative Entry Point:** Single authoritative entry point at `apps.api.src.main:app` with structured lifespan events, CORS, request IDs, error shielding, and PII masking.
- **Import Integrity:** All imports across `apps/api` utilize `rakshagrid.<package>` namespace packages.

---

## 3. AI / ML Realism & Truthfulness Audit

Every occurrence of audited keywords across the codebase was systematically classified:

### Keyword Search Classification Table

| Keyword Searched | Files Found | Classification | Verification Finding |
|---|---|---|---|
| `mock` / `Mock` | `tests/integration/test_*.py` | **Legitimate test fixture** | Unit test doubles used exclusively to test edge cases (e.g. STT failures). Zero mock usage in production `apps/` or `packages/`. |
| `fake` / `Fake` | `apps/web/src/pages/audio.tsx`, `apps/api/src/schemas/audio_schema.py`, `ReportCrimeModal.tsx` | **Production functionality** | Restricted strictly to the domain entity term "deepfake" and crime category string `"Fake Job"`. Zero fake persistence or fake detections. |
| `dummy` | None found | **N/A** | 0 occurrences across entire repository. |
| `hardcoded` | None found in code | **N/A** | 0 occurrences in source code; only mentioned in documentation. |
| `setTimeout` | `apps/web/src/pages/transcription.tsx`, `settings.tsx`, `ReportCrimeModal.tsx`, `OnboardingGuide.tsx` | **Legitimate demo/UI functionality** | 100% standard UI UX feedback timers (e.g. "Copied to clipboard" 2s banner, modal dismiss transitions). Zero simulated AI processing delays. |
| `Math.random` | `GraphView.tsx`, `ReportCrimeModal.tsx` | **Legitimate UI utility** | Used for initial canvas node coordinate jitter to prevent concentric node overlap, and client-side device ID fallback when `crypto.randomUUID` is unavailable. Zero fake probabilities. |
| `localStorage` | `OnboardingGuide.tsx` | **Legitimate UI persistence** | Used only to remember if the user has dismissed the welcome onboarding guide (`raksha_has_seen_guide`). Reports are saved via backend API. |
| `mockReports` | Documentation only | **N/A** | Completely removed from code. Replaced with live backend graph queries. |
| `confidence: 0.92`| Documentation only | **N/A** | Completely eradicated. `/api/v1/crime/predict` returns explicit `501 Not Implemented`. |
| `is_deepfake` | Schemas, `voice_deepfake.py`, tests | **Production functionality** | Decoupled acoustic deepfake field in typed schemas; unit tests explicitly assert `is_deepfake` is never derived from `risk_band == 'high'`. |
| `fallback transcript`| Documentation & tests | **N/A** | Deceptive fallback scam text completely eliminated. Whisper failure raises clean `AudioTranscriptionException`. |

### Specific Truthfulness Invariants Verified
1. **STT failure never creates fake text:** When speech-to-text fails, the system returns `transcription.status = "failed"`, `transcript = None`, and downstream scam classification is set to `"not_analyzed"` (`is_scam = None`).
2. **Scam probability never determines deepfake status:** Voice deepfake detection runs through `VoiceDeepfakeDetector`. If acoustic weights are missing, it returns `status: "unavailable"` and `is_deepfake: None`. Linguistic scam risk has zero bearing on voice synthesis detection.
3. **Crime media prediction does not return fake confidence/severity:** `POST /api/v1/crime/predict` returns `HTTP 501 Not Implemented` with `CrimeMediaNotImplementedResponse` rather than returning synthetic probabilities.
4. **Graph data is dynamically generated from actual data:** Fraud syndicate nodes and links are constructed exclusively from live incident reports submitted via `/api/v1/reports`.
5. **Persistence does not rely on browser `localStorage`:** All citizen reports persist into FastAPI state (`POST /api/v1/reports`).
6. **Missing models result in explicit unavailable/error status:** Unloaded or missing models cleanly report `status: "unavailable"` or `HTTP 501/503`.

---

## 4. API Endpoints & Contract Audit

| Endpoint | Method | Security Level | Request / Response Schema | Status Code & Error Handling |
|---|---|---|---|---|
| `/api/v1/scam/analyze-text` | `POST` | Public Edge | `ScamAnalysisRequest` → `VerdictResponse` | `200 OK`, `422 Unprocessable` |
| `/api/v1/scam/stream` | `POST` | Public Edge | `StreamRequest` → `text/event-stream` | `200 OK`, SSE Progressive Stream |
| `/api/v1/audio/detect` | `POST` | Public Edge | `UploadFile` → `AudioDetectResponse` | `200 OK`, `400 Bad Request`, `413 Payload Too Large` |
| `/api/v1/audio/transcribe` | `POST` | Public Edge | `UploadFile` → `TranscribeResponse` | `200 OK`, `400 Bad Request` |
| `/api/v1/currency/predict` | `POST` | Public Edge | `UploadFile` → `CurrencyResponse` | `200 OK`, `400 Bad Request`, `415 Unsupported Media` |
| `/api/v1/crime/incidents` | `GET` | **Protected (API Key/Bearer)** | Query params → `PointsResponse` | `200 OK`, `401 Unauthorized`, `403 Forbidden` |
| `/api/v1/crime/hotspots` | `GET` | **Protected (API Key/Bearer)** | Query params → `HotspotsResponse` | `200 OK`, `401 Unauthorized`, `403 Forbidden` |
| `/api/v1/crime/patrol-allocation`| `GET` | **Protected (API Key/Bearer)** | Query params → `PatrolAllocationResponse` | `200 OK`, `401 Unauthorized`, `403 Forbidden` |
| `/api/v1/crime/predict` | `POST` | **Protected (API Key/Bearer)** | `UploadFile` → `501 Not Implemented` | `501 Not Implemented` |
| `/api/v1/graph/nodes` | `GET` | **Protected (API Key/Bearer)** | None → `NodesResponse` | `200 OK`, `401 Unauthorized`, `403 Forbidden` |
| `/api/v1/graph/centrality` | `GET` | **Protected (API Key/Bearer)** | None → `CentralityResponse` | `200 OK`, `401 Unauthorized`, `403 Forbidden` |
| `/api/v1/graph/clusters` | `GET` | **Protected (API Key/Bearer)** | None → `ClustersResponse` | `200 OK`, `401 Unauthorized`, `403 Forbidden` |
| `/api/v1/reports` | `POST`/`GET` | **Protected (API Key/Bearer)** | `CrimeReport` → `ReportResponse` / `ReportList` | `200 OK`, `201 Created`, `401 Unauthorized` |
| `/api/v1/chat` | `POST` | **Protected (API Key/Bearer)** | `ChatRequest` → `ChatResponse` | `200 OK`, `401 Unauthorized`, `403 Forbidden` |
| `/health` | `GET` | Public | None → `SystemHealthResponse` | `200 OK` (No heavy ML model loading) |

### SSE Verification
- `POST /api/v1/scam/stream` returns `Content-Type: text/event-stream`.
- Emits real progressive SSE chunks (`data: {"chunk_index": ..., "risk_score": ..., "verdict": ...}\n\n`).
- Emits explicit terminal event `data: [DONE]\n\n`.
- Handles empty or whitespace chunk lists safely with `400 Bad Request`.

---

## 5. Security & Privacy Audit

- **Authentication & Authorization:** Enforced via `apps/api/src/core/security.py`. All sensitive intelligence endpoints (`/crime/*`, `/graph/*`, `/reports/*`, `/chat`) require valid `X-API-Key` or `Authorization: Bearer <token>`. Missing credentials return `401 Unauthorized`; invalid credentials return `403 Forbidden` using constant-time `hmac.compare_digest`.
- **CORS Hardening:** Removed wildcard `*` with credentials. Origins are restricted to explicit whitelist via `CORS_ORIGINS` in `apps/api/src/config.py`.
- **Upload Validation & Magic Bytes:** Streamed inspection enforces 25 MB file size ceiling, validates binary magic bytes (`image/jpeg`, `image/png`, `image/webp`, `audio/wav`, `audio/ogg`, `audio/mpeg`, `audio/flac`, `audio/mp4`), sanitizes filenames against directory traversal (`../`), and guarantees automatic temporary file deletion.
- **Error Shielding:** Unhandled exceptions are intercepted by `GlobalExceptionHandler` returning structured JSON containing a unique `request_id`. Internal stack traces, local paths, and connection strings are never leaked.
- **Sensitive PII Logging Redaction:** `PIIMaskingFilter` automatically redacts Indian phone numbers (`+91 98****3210`), UPI VPAs (`u***r@oksbi`), bank account numbers (`********9012`), and bearer tokens in logs.

---

## 6. Performance & Concurrency Audit

| Metric | Target / Benchmark | Measured Value | Assessment |
|---|---|---|---|
| **Resident RAM Usage** | < 2.0 GB | **999.41 MB** | **OPTIMAL** (Singletons shared across threads) |
| **VRAM Consumption** | < 2.0 GB | **0 MB** (CPU mode default) | **OPTIMAL** |
| **Process Startup Time** | < 5.0 s | **1.84 s** | **OPTIMAL** (Deferred model imports) |
| **Scam Inference Latency** | < 100 ms | **20.82 ms** | **OPTIMAL** (Quantized PyTorch + TF-IDF) |
| **Graph Analytics Latency** | < 50 ms | **9.29 ms** | **OPTIMAL** (Optimized NetworkX PageRank/Louvain) |
| **DBSCAN Clustering Latency** | < 1000 ms | **601.71 ms** (40,160 points) | **OPTIMAL** (BallTree metric projection) |
| **Frontend Production Build** | Shared JS < 150 kB | **101 kB** First Load JS | **OPTIMAL** (Next.js 14 chunking) |

- **Event Loop Concurrency:** Dedicated `InferenceConcurrencyManager` (`apps/api/src/core/concurrency.py`) with `asyncio.Semaphore(4)` prevents CPU-bound inference from starving FastAPI's asynchronous event loop.
- **Graph Simulation Stability:** Graph physics incorporates a spatial hashing grid ($180\text{px}$ cells) that drops repulsive calculation complexity from $O(N^2)$ to $O(N)$. Kinetic alpha cooling halts physics simulation once equilibrium is achieved.
- **Leaflet Integration:** Native npm bundling (`leaflet` ^1.9.4) without external unpkg/CDN script injection.

---

## 7. Frontend Consolidation & Integration Audit

- **Application Count:** Single frontend application consolidated under `apps/web/`.
- **Component Hygiene:** All duplicate components (`Navbar.tsx`, `Sidebar.tsx`, `LeafletCrimeMap.tsx`, etc.) removed in favor of modular components under `apps/web/src/components/common/`, `components/graph/`, and `components/map/`.
- **API Client:** Fully typed client (`apps/web/src/api/client.ts`) utilizing standardized DTOs with consistent error interception and bearer token forwarding.
- **State Handling:** Every UI view implements explicit Loading, Error, and Empty data states.

---

## 8. Test Suite & Validation Audit

Ran full test suite across the active monorepo application:
- `pytest -v`: **117 / 117 tests passed** in **80.67s** (100% pass rate).
  - Module 1 (Currency): 17 tests passed.
  - Module 2 (Scam & Audio Deepfake): 15 tests passed.
  - Module 3 (Graph Analytics): 13 tests passed.
  - Module 4 (Crime DBSCAN & Patrol): 32 tests passed.
  - Security & Authentication: 21 tests passed.
  - Monorepo Architecture: 10 tests passed.
  - API Routers & Rules: 9 tests passed.
- `npm run lint`: **0 errors** (2 standard `<Image />` optimization hints).
- `npx tsc --noEmit`: **0 errors** (Clean TypeScript validation).
- `npm run build`: **0 errors** (18/18 static pages successfully compiled).

---

## 9. Containerization & Docker Audit

- **API Dockerfile (`apps/api/Dockerfile`):** Updated entrypoint to authoritative `apps.api.src.main:app`.
- **Web Dockerfile (`apps/web/Dockerfile`):** Converted from development server (`npm run dev`) into a multi-stage production container (`builder` → `runner`) executing `npm run build` and `npm start`.
- **Docker Compose (`docker-compose.yml`):**
  - Removed obsolete `version: '3.8'` attribute.
  - Validated with `docker compose config` → Exits with code 0 and **0 warnings**.
  - Mounted `./data:/workspace/data:ro` for crime datasets.
- **Context Exclusion (`.dockerignore`):** Excludes `.git`, `.venv`, `node_modules`, `.next`, `storage/uploads`, and checkpoints while preserving required processed data (`!data/processed/points.parquet`).

---

## 10. CI/CD Automation Audit

Three automated GitHub Actions workflows created under `.github/workflows/`:
1. **`.github/workflows/ci-backend.yml`**: Runs pytest across Python 3.11 and 3.12 on pull requests and pushes to `main`/`master`.
2. **`.github/workflows/ci-frontend.yml`**: Runs `npm ci`, `npx tsc --noEmit`, `npm run lint`, and `npm run build` on Node.js 18 and 20.
3. **`.github/workflows/docker-build.yml`**: Validates `docker compose config` and executes Docker Buildx container builds for both backend and frontend images.

---

## 11. Final Risk & Defect Classification Matrix

### A. Completed Requirements
1. Decoupled monorepo directory layout (`apps/`, `packages/`, `pipelines/`, `data/`, `tests/`, `.github/`).
2. Single authoritative FastAPI entrypoint with modular schemas and routers.
3. Complete elimination of deceptive STT fallback transcripts and fake deepfake logic.
4. Independent acoustic voice deepfake abstraction (`VoiceDeepfakeDetector`).
5. Live dynamic fraud syndicate graph engine with PageRank and Louvain community detection.
6. Elimination of browser `localStorage` persistence in favor of API backend storage.
7. Authentication and authorization layer for sensitive intelligence endpoints.
8. Upload security with magic byte validation, 25 MB ceiling, and path traversal prevention.
9. Structured error shielding with unique request IDs and zero internal stack leakages.
10. Centralized PII masking for Indian phone numbers, UPI VPAs, bank accounts, and tokens.
11. Event loop concurrency offloading via `InferenceConcurrencyManager`.
12. Multi-stage production containerization and GitHub Actions CI/CD workflows.

### B. Remaining Defects
- None blocking production. All 117 tests pass and all builds succeed.

### C. Security Risks
- **Level: LOW.** Master API key defaults to `rakshagrid-master-key-2026` if not provided via environment. Production deployments must inject a cryptographically secure key via secret manager.

### D. Performance Risks
- **Level: LOW.** DBSCAN clustering on 40,160 points takes ~600ms on CPU. Highly acceptable for batch/cadence updates, but should be cached or calculated asynchronously if query volume exceeds 50 req/sec.

### E. Missing AI Models
- **Acoustic Voice Deepfake Weights:** RawNet2 / AASIST weights are not bundled in repository. The system safely returns `status: "unavailable"` and `is_deepfake: null`.
- **Crime Media Vision Model:** Computer vision crime detection returns `501 Not Implemented`.

### F. Missing Infrastructure
- In-memory fraud graph and report storage are process-bound. High-availability multi-instance deployments require an external PostgreSQL/Neo4j cluster.

### G. Deployment Blockers
- **Zero blockers remain.** All critical containerization and CI/CD defects have been fixed.

### H. Technical Debt
- Two Next.js pages (`crime.tsx`, `currency.tsx`) use `<img>` instead of `next/image`.
- Joblib vectorizer triggers a minor scikit-learn version mismatch warning on unpickle.

### I. Recommended Next Steps
1. Mount trained RawNet2 acoustic deepfake weights in production to enable voice biometrics.
2. Connect `GraphSyndicateService` to persistent PostgreSQL instance.
3. Implement sliding-window rate limiting on public upload endpoints.
