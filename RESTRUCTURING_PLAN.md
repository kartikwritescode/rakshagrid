# 🛡️ Raksha Grid — Comprehensive Codebase Audit & Production Restructuring Plan

> **Document Version:** 1.0.0  
> **Date:** September 2026  
> **Target Status:** Production-Grade AI Public Safety & Crime Intelligence Platform  
> **Scope:** Monorepo Restructuring, Bug Inventory, Performance Bottlenecks, AI/ML De-mocking, Security Hardening, and Migration Roadmap.

---

## Executive Summary

**Raksha Grid** is intended to be a multi-tier AI public safety intelligence platform comprising:
1. **Module 1: Counterfeit Currency Identification** (Computer Vision / EfficientNet)
2. **Module 2: Scam Call Interceptor & Digital Arrest Detection** (Speech-to-Text Whisper + Stacking Ensemble + LLM Fallback)
3. **Module 3: Fraud Network Graph Intelligence** (Graph Centrality, Community Detection, Mule Ring Analysis)
4. **Module 4: Geospatial Crime Pattern Intelligence** (VigilGrid Haversine DBSCAN Hotspots + Patrol Allocation)
5. **Module 5: Citizen Fraud Shield** (Conversational Scam Advisory, Call/Transcript Scanning, Evidence Reporting)

### Current Codebase Assessment: **Critical Monorepo Disorder**
A thorough inspection of the repository reveals severe technical debt, architectural bifurcation, code duplication, and incomplete integrations:
- **Multiple Divergent Backends:** A legacy root-level backend (`main.py`, `config.py`, `schemas.py`) sits directly beside the modular backend (`backend/fastapi/app/`), while an entirely separate Express.js + MongoDB backend is dumped inside `et-AI/backend/`.
- **Duplicate Frontends & Component Cloning:** A Next.js application exists at `frontend/nextjs/`, while an older, nearly identical Next.js application sits in `et-AI/frontend/`, with duplicate components copy-pasted across both.
- **Checked-In Binary Weights & Git Bloat:** Over **66 MB** of binary `.h5` model files, checkpoints, and `.parquet` data files are committed directly into the Git repository, replicated 3 to 4 times across folders (`models/`, `module1_currency/`, `training_output/`).
- **Orphan Git Submodule / Broken Gitlink:** The directory `module4_crime` is tracked as a Git link (`160000`) with its own detached `.git` folder, but **no `.gitmodules` file exists**, making clean repository cloning fail.
- **Deceptive AI Mocks:** Critical capabilities advertised in documentation are actually mocked:
  - *Audio Deepfake Detection* is simply Whisper STT + text classification with `is_deepfake = (risk_band == 'high')`.
  - *Whisper STT Fallback* returns a hardcoded scam message when transcription fails, creating a false illusion that voice analysis worked.
  - *Crime Scene Media Prediction* (`/api/crime/predict`) returns hardcoded static JSON without analyzing anything.
  - *Graph Intelligence & Cluster Chat* rely on hardcoded static mock objects and `setTimeout` strings because the Express graph backend was never ported to FastAPI.
  - *Supabase Client* is an in-memory browser `localStorage` mock simulator.
- **Broken Tests & Protocol Regressions:** Existing tests in `tests/test_api.py` import the deprecated root `main.py`, test endpoints against old contracts, and fail against the new backend. `/api/scam/stream` was regressed from real Server-Sent Events (SSE) to synchronous JSON.

---

## 1. Monorepo Structural Audit & Duplication Analysis

### 1.1 Structural Sprawl & Conflicting Entry Points
The workspace contains conflicting files competing for the same responsibilities:

```
rakshagrid/ (Root)
│
├── main.py                     <-- DEPRECATED single-file FastAPI server
├── config.py                   <-- DEPRECATED flat configuration
├── schemas.py                  <-- DEPRECATED flat Pydantic models
├── Dockerfile                  <-- DEPRECATED Dockerfile running legacy "main:app"
├── requirements.txt            <-- BROKEN pip freeze (Numpy 2.2.6, Torch cu128, missing FastAPI/Uvicorn)
│
├── backend/fastapi/            <-- NEW modular backend (incomplete migration)
│   ├── app/
│   │   ├── main.py             <-- Active FastAPI factory
│   │   ├── config/settings.py  <-- Active settings
│   │   ├── routers/            <-- Active routers (scam, audio, crime, currency, health)
│   │   ├── services/           <-- Active services
│   │   └── schemas/            <-- Active schemas
│   ├── Dockerfile              <-- Copies entire root without .dockerignore
│   └── requirements.txt        <-- Active backend dependencies (Numpy 1.26.4, Torch 2.4.1)
│
├── et-AI/                      <-- ORPHAN REPOSITORY DUMP
│   ├── backend/                <-- Express.js + TypeScript + MongoDB + NetworkX graph scripts
│   └── frontend/               <-- Older Next.js frontend (components copied into frontend/nextjs)
│
├── models/                     <-- DUPLICATE ML CODE + 16.5MB currency_model.h5
├── module1_currency/           <-- DUPLICATE ML CODE + 3x 16.5MB h5 weights + notebooks
├── ml/module1_currency/        <-- Active Module 1 clean packaging
│
├── module4_crime/              <-- ORPHAN GIT REPO (mode 160000) with app.py, data/, geocode.py
├── ml/module4_crime/           <-- Active Module 4 clean packaging
│
├── utils/                      <-- DUPLICATE preprocessing & rules (mirrored in ml/module2)
├── shared/                     <-- Cross-cutting configs, logging, exceptions
├── training/                   <-- Root training scripts (eval_adversarial, train_ensemble, etc.)
├── training_output/            <-- Raw transformer checkpoints (checkpoint-450)
├── artifacts/                  <-- Model weights (tfidf, transformer, ensemble_meta)
├── storage/                    <-- Empty storage directories (storage/models/ has 0 files)
└── frontend/nextjs/            <-- Active Next.js 14 frontend
```

### 1.2 Redundancy Matrix

| Entity | Location A (Active / Target) | Location B (Legacy / Redundant) | Location C (Third Duplicate) | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **API Entry Point** | `backend/fastapi/app/main.py` | `main.py` (root) | `et-AI/backend/src/index.ts` | Delete root `main.py` & `et-AI/backend`; standardize on unified FastAPI. |
| **Settings / Config** | `backend/fastapi/app/config/settings.py` | `config.py` (root) | `module4_crime/config.py` | Consolidate into `apps/api/config` + Pydantic v2 `BaseSettings`. |
| **Pydantic Schemas** | `backend/fastapi/app/schemas/` | `schemas.py` (root) | — | Delete root `schemas.py`. |
| **Currency Model Code** | `ml/module1_currency/` | `models/currency_model.h5` | `module1_currency/` (root) | Consolidate into `packages/ai-currency/`; remove root `module1_currency` and `models/`. |
| **Currency Weights (.h5)** | `module1_currency/best_model_finetuned.h5` | `module1_currency/best_model_stage1.h5` | `models/currency_model.h5` | Purge duplicates (3x 16.5MB = ~50MB); store single production model in external store or DVC. |
| **Crime Engine Code** | `ml/module4_crime/` | `module4_crime/` (root git repo) | — | Remove root `module4_crime/` gitlink; integrate scripts into `packages/ai-crime/`. |
| **Crime Data (.parquet)** | `module4_crime/data/processed/points.parquet` | Fallback searches in 3 relative dirs | — | Standardize dataset storage location in `data/processed/points.parquet`. |
| **Scam Model Logic** | `ml/module2/` | `models/` (root) | `utils/` (root) | Delete root `models/` and `utils/`; keep clean `packages/ai-scam/`. |
| **Fraud Graph Logic** | *Missing in FastAPI* | `et-AI/backend/src/graph/` | `frontend/nextjs/src/pages/graph.tsx` (mock) | Port Python NetworkX graph analytics into FastAPI service; delete `et-AI/`. |
| **Frontend UI** | `frontend/nextjs/` | `et-AI/frontend/` | — | Delete `et-AI/frontend/`. |

---

## 2. In-Depth Bug, Logic Flaw & Deceptive Mock Inventory

### 2.1 Fake AI Implementations Masquerading as Working Features

#### Bug 1: Audio Deepfake Detection is a Sham
- **File:** `backend/fastapi/app/routers/audio_router.py` (Lines 35–38)
```python
res = scam_service.analyze_audio(temp_path)
res["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
res["is_deepfake"] = (res.get("risk_band") == "high")
return res
```
- **The Problem:** The endpoint `/api/audio/detect` advertises "Audio Deepfake Voice Biometrics". In reality, it only runs speech-to-text (Whisper) and text scam classification, setting `is_deepfake` to `true` whenever the *text content* of the call sounds like a scam! A real voice call with a scammer is marked "Deepfake", while an actual AI voice clone talking about the weather is marked "Safe".
- **Production Fix:** Integrate a genuine acoustic/spectral audio classification model (e.g., RawNet2, AASIST, or Wav2Vec2 fine-tuned on ASVspoof) analyzing spectral artifacts, pitch jitter, and synthetic vocoder phase anomalies.

#### Bug 2: Whisper STT Fallback Deceives the User
- **File:** `ml/module2/model/audio.py` (Lines 86–90)
```python
# Tier 4: Safe Fallback for offline/testing without crash
filename = os.path.basename(audio_path)
print(f"Using standard audio fallback transcript for {filename}")
return f"Hello, this is an automated security verification call regarding your account. Please confirm your details immediately."
```
- **The Problem:** If local Whisper fails and Groq API key is missing or fails, the system returns a hardcoded scam sentence! This sentence is fed into the text scam classifier, which triggers high risk and flags the call as an urgent scam. If a user uploads an audio clip of birds chirping with no API key, Raksha Grid declares it a Digital Arrest Scam.
- **Production Fix:** Fallbacks must raise an explicit `TranscriptionServiceUnavailableException` or return a status indicating transcription failed. Never synthesize scam text under the hood.

#### Bug 3: Crime Scene Prediction Endpoint is Hardcoded Mock
- **File:** `backend/fastapi/app/routers/crime_router.py` (Lines 47–65)
```python
@router.post("/predict", status_code=status.HTTP_200_OK)
async def predict_crime(file: UploadFile = File(None), ...):
    return {
        "status": "analyzed",
        "crime_type": crime_description,
        "category": "Cyber Crime",
        "confidence": 0.92,
        "location": city,
        "severity": "High",
        "processing_time_ms": round((time.time() - start_time) * 1000, 2),
        "filename": file.filename if file else None
    }
```
- **The Problem:** Accepts image/video uploads and immediately returns hardcoded `confidence: 0.92`, `severity: High` without processing the uploaded file.
- **Production Fix:** Either implement a real Vision Crime Scene analysis model (YOLOv8 / CLIP zero-shot classification for weapons, vandalism, forced entry) or decommission the placeholder route until implemented.

#### Bug 4: Fraud Graph Intelligence is Dead Code & Hardcoded Mocks
- **Files:** `frontend/nextjs/src/pages/graph.tsx` (Lines 48–60), `index.tsx` (Lines 54–68)
```typescript
const mockReports: Report[] = [
  { victimId: 'VIC-9021', victimName: 'Ramesh Kumar', phoneNumber: '+91 98765 43210', upiId: 'scam@okaxis', ... }
];
```
- **The Problem:** The entire Module 3 Graph Intelligence Engine exists only in unlinked Python scripts inside `et-AI/backend/src/graph/` (`analysis.py`, `graph_builder.py`). Because there is no FastAPI router for graph intelligence, the frontend hardcodes two static mock victim reports.
- **Production Fix:** Build a native `graph_router.py` in FastAPI wrapping NetworkX (or Neo4j) to compute PageRank, Betweenness Centrality, and Louvain community clusters dynamically from real reported incident records.

#### Bug 5: Fake Supabase Emulation in Browser LocalStorage
- **File:** `frontend/nextjs/src/lib/supabase.ts` (Lines 6–213)
- **The Problem:** Implements `MockSupabaseStorage`, `MockSupabaseQuery`, `MockSupabaseChannel`, and `MockSupabaseAuth` storing messages and user sessions in browser `localStorage` and dispatching synthetic DOM `CustomEvent`s. Any incident submitted in `ReportCrimeModal.tsx` vanishes when clearing browser cookies or switching browsers.
- **Production Fix:** Replace with real REST API endpoints on the FastAPI backend backed by PostgreSQL / Supabase, and handle file uploads via S3/MinIO presigned URLs or direct multipart upload to backend.

---

### 2.2 Core Logic, Protocol & Architecture Regressions

#### Bug 6: Real-time Streaming Interception Protocol Broken
- **Files:** `main.py` (legacy) vs `backend/fastapi/app/routers/scam_router.py` vs `tests/test_api.py`
  - In `main.py`: `/api/scam/stream` was an asynchronous generator returning `StreamingResponse(..., media_type="text/event-stream")` for Server-Sent Events (SSE).
  - In `scam_router.py`:
    ```python
    @router.post("/stream", status_code=status.HTTP_200_OK)
    def analyze_stream(payload: StreamRequest):
        return scam_service.analyze_stream(payload.transcript_chunks)
    ```
    It returns a static `list[dict]` in a single synchronous blocking response!
  - In `tests/test_api.py`:
    ```python
    assert "text/event-stream" in response.headers["content-type"]
    ```
  - **Result:** The modular backend completely broke real-time stream simulation and fails the test suite.

#### Bug 7: Conflicting Calibration Thresholds Across Modules
- In root `config.py`:
  - `DEFAULT_HIGH_THRESHOLD = 0.70`
  - `DEFAULT_MEDIUM_THRESHOLD = 0.35`
- In `ml/module2/config/scam_config.py` and `shared/constants/risk_bands.py`:
  - `DEFAULT_HIGH_THRESHOLD = 0.55`
  - `DEFAULT_LOW_THRESHOLD = 0.12`
- **Result:** Importing from different modules produces completely different risk verdicts (`high` vs `medium` vs `needs_review`) for the exact same numerical probability score!

#### Bug 8: Unstable Fragile Path Resolution for Model Artifacts
- **Files:** `ml/module1_currency/model/currency_net.py`, `ml/module2/config/scam_config.py`, `ml/module4_crime/config/crime_config.py`
  - Code uses hardcoded relative fallback lists:
    ```python
    legacy_path = os.path.join("module1_currency", "best_model_finetuned.h5")
    # and
    fallback_paths = [
        "module4_crime/data/processed/points.parquet",
        "module4_crime/data/processed_points.parquet",
        "data/processed_points.parquet"
    ]
    ```
  - If uvicorn is launched from any directory other than root, or inside Docker where directory structures differ, all fallback checks fail and models crash or re-initialize with random uninitialized weights!

#### Bug 9: Tests Target Deprecated Root Server
- **File:** `tests/test_api.py` (Line 3)
```python
from main import app  # <-- Targets root main.py, NOT backend.fastapi.app.main:app
```
- The test harness does not test the actual modular application, services, or routers. Testing passes on stale legacy code while the real application remains unverified.

#### Bug 10: Missing Leaflet Dependency in Frontend `package.json`
- **Files:** `frontend/nextjs/package.json`, `frontend/nextjs/src/components/LeafletCrimeMap.tsx`
  - `package.json` does NOT contain `leaflet` or `@types/leaflet`.
  - `LeafletCrimeMap.tsx` injects `<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">` into the DOM at runtime.
  - **Result:** Offline development fails, bundling cannot optimize Leaflet, and race conditions occur if the component mounts before the CDN script finishes downloading.

---

## 3. Performance, Scalability & Resource Bottlenecks

### 3.1 Unbounded HTML5 Canvas Simulation on the Main Thread
- **File:** `frontend/nextjs/src/components/GraphView.tsx` (Lines 107–166)
- **The Bottleneck:** Runs an $O(N^2)$ all-pairs repulsion physics loop on every single animation frame (`requestAnimationFrame`):
  ```typescript
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) { ... }
  }
  ```
- **Impact:** For a realistic fraud network with 500+ nodes and 1,200+ edges, this executes 125,000 force computations 60 times a second on the JavaScript UI thread, causing severe frame drops, UI freezes, and high CPU consumption on client machines.
- **Production Solution:** Offload graph layout computation to a Web Worker (or use WebGL-accelerated libraries like `Cosmograph` or `react-force-graph` with D3-force worker simulation), and freeze the simulation once node velocities drop below an equilibrium epsilon.

### 3.2 Massive Memory Footprint from Monolithic ML Loading
- **The Bottleneck:** PyTorch, TensorFlow, Hugging Face Transformers (`scam-transformer`), Faster-Whisper, Albumentations, and OpenCV are all imported within the same Python process.
- **Impact:**
  - A single worker process requires **3.5 GB to 5.5 GB of RAM**.
  - In a production setup running Uvicorn with 4 workers (`--workers 4`), the container requires **16+ GB of RAM** just to start up.
  - If a worker crashes under load, spawning a replacement worker takes 20–40 seconds due to loading multiple gigabytes of deep learning weights.
- **Production Solution:** Decouple ML inference into independent microservices or worker processes (or use Triton Inference Server / TorchServe / ONNX Runtime), allowing CPU-bound web APIs to scale horizontally with low memory while heavy GPU/inference nodes scale independently.

### 3.3 Synchronous Blocking I/O in Async Route Handlers
- **File:** `backend/fastapi/app/routers/audio_router.py`, `scam_router.py`
- Endpoints defined as `async def` call blocking CPU-intensive routines:
  ```python
  @router.post("/detect")
  async def detect_audio_deepfake(...):
      # scam_service.analyze_audio is SYNCHRONOUS and CPU/GPU bound!
      res = scam_service.analyze_audio(temp_path)
  ```
- **Impact:** In Python `asyncio`, calling synchronous CPU-heavy functions inside an `async def` function blocks the event loop! While one user is transcribing audio (10–30 seconds), **all other API requests to the server are completely blocked and timed out**.
- **Production Solution:** Run synchronous ML inference inside `run_in_threadpool(scam_service.analyze_audio, temp_path)` or define the endpoint as a standard `def` route so FastAPI automatically dispatches it to the internal thread pool.

### 3.4 Missing Docker Caching and Bloated Context
- **Files:** `backend/fastapi/Dockerfile`, `docker-compose.yml`
- There is **no `.dockerignore` file** in the project root.
- The backend Dockerfile executes:
  ```dockerfile
  COPY . /workspace
  ```
- **Impact:** Docker sends the entire project root to the Docker daemon on every build: `frontend/nextjs/node_modules/` (~350 MB), `et-AI/backend/node_modules/` (~200 MB), `.venv/` (~4 GB), `.git/` history, training checkpoints (`training_output/`), and datasets (`data/`).
- Docker build context exceeds **6 GB**, resulting in 15+ minute builds and gigabytes of wasted container image layers.

---

## 4. Security, Resilience & Compliance Vulnerabilities

1. **Stack Trace & Internal Exception Leakage:**
   - In `backend/fastapi/app/middleware/error_handler.py`:
     ```python
     return JSONResponse(status_code=500, content={"message": f"Internal Server Error: {str(exc)}"})
     ```
   - In production, internal file paths, database connection strings, or system errors are directly returned to untrusted clients.
2. **Permissive Insecure CORS Configuration:**
   - In `backend/fastapi/app/config/settings.py`:
     `CORS_ORIGINS = [..., "*"]` combined with `allow_credentials=True` in `middleware/cors.py`.
   - Modern browsers reject wildcard `*` with credentials enabled. In production, this allows arbitrary third-party origins to make authenticated cross-origin requests.
3. **Unauthenticated Law Enforcement Endpoints:**
   - Sensitive endpoints such as `/api/crime/patrol-allocation`, `/api/crime/hotspots`, and `/api/crime/incidents` are completely unauthenticated. Anyone on the public internet can inspect police patrol unit allocations and incident records.
4. **Unvalidated File Uploads:**
   - Audio and currency endpoints inspect only user-supplied file extensions (`.ogg`, `.png`) without verifying magic bytes (file signatures) or capping file upload sizes, leaving the server vulnerable to denial-of-service via large binary uploads or malicious payloads.
5. **Git Submodule Link Broken:**
   - Git object `160000 e05019... module4_crime` without a corresponding `.gitmodules` entry breaks automated CI/CD checkout pipelines (`git submodule update --init --recursive` fails with fatal errors).

---

## 5. Target Industry-Standard Monorepo Architecture

To transform Raksha Grid into an enterprise-ready, maintainable, and high-performance system, the entire codebase must be restructured into a **modular Clean Architecture Monorepo**:

```text
rakshagrid/
├── .github/
│   └── workflows/
│       ├── ci-backend.yml              # Python linting (Ruff), typing (Mypy), Pytest
│       ├── ci-frontend.yml             # Next.js ESLint, TypeScript check, unit tests
│       └── docker-build.yml            # Multi-stage container builds
├── .dockerignore                       # Excludes .venv, node_modules, cache, large datasets
├── .gitignore                          # Cleaned, standardized exclusions
├── docker-compose.yml                  # Unified multi-service local environment
│
├── apps/                               # Deployable Application Services
│   ├── api/                            # Central FastAPI Intelligence Gateway
│   │   ├── Dockerfile                  # Multi-stage production container
│   │   ├── requirements.txt            # Curated production dependencies
│   │   ├── src/
│   │   │   ├── main.py                 # FastAPI application factory
│   │   │   ├── config.py               # Pydantic v2 Settings (env validation)
│   │   │   ├── core/                   # Lifespan, security, dependencies, auth
│   │   │   ├── middleware/             # Rate limiting, CORS, error handling, telemetry
│   │   │   ├── routers/                # Versioned REST routers (/v1/scam, /v1/crime, etc.)
│   │   │   │   ├── v1/
│   │   │   │   │   ├── scam.py
│   │   │   │   │   ├── audio.py
│   │   │   │   │   ├── currency.py
│   │   │   │   │   ├── crime.py
│   │   │   │   │   ├── graph.py        # Native Fraud Graph API (PageRank, Clusters)
│   │   │   │   │   └── health.py
│   │   │   ├── services/               # Orchestration & business logic layer
│   │   │   └── schemas/                # Public Pydantic API DTOs
│   │
│   └── web/                            # Next.js 14 Production Web Dashboard
│       ├── Dockerfile                  # Node.js alpine standalone build
│       ├── package.json                # Includes leaflet, @types/leaflet, lucide-react
│       ├── src/
│       │   ├── app/ (or pages/)        # Unified, deduplicated routes
│       │   ├── components/             # Reusable UI component library
│       │   │   ├── map/                # Native Leaflet components (no unpkg CDN)
│       │   │   ├── graph/              # Optimized Graph viewer (worker simulation)
│       │   │   └── common/             # Cards, Modals, Navbars, Skeletons
│       │   ├── hooks/                  # Custom React query & mutation hooks
│       │   ├── services/               # Typed API client services
│       │   └── types/                  # TypeScript interface contracts
│
├── packages/                           # Reusable Internal Python Packages
│   ├── ai-scam/                        # Module 2: Scam Interceptor Engine
│   │   ├── src/
│   │   │   ├── rules/                  # Lexicon & heuristic rules engine
│   │   │   ├── feature_extraction/     # 9 engineered call features
│   │   │   ├── models/                 # TF-IDF, Transformer, Ensemble Meta-classifier
│   │   │   ├── stt/                    # Robust multi-tier Whisper audio transcription
│   │   │   ├── voice_biometrics/       # Real Acoustic Deepfake Detection Engine
│   │   │   └── llm/                    # Groq LLaMA fallback verifier
│   │   └── tests/                      # Dedicated package unit tests
│   │
│   ├── ai-currency/                    # Module 1: Banknote Authenticity Engine
│   │   ├── src/
│   │   │   ├── preprocessing/          # OpenCV / Albumentations normalization
│   │   │   ├── model/                  # EfficientNetB0 defect classifier
│   │   │   └── postprocessing/         # Probabilities & threshold calibration
│   │   └── tests/
│   │
│   ├── ai-crime/                       # Module 4: VigilGrid Geospatial Engine
│   │   ├── src/
│   │   │   ├── dbscan/                 # Haversine spatial clustering algorithm
│   │   │   ├── patrol/                 # Patrol unit optimization allocator
│   │   │   └── geocoding/              # Coordinate normalization & jitter
│   │   └── tests/
│   │
│   ├── ai-graph/                       # Module 3: Fraud Network Graph Engine
│   │   ├── src/
│   │   │   ├── builder/                # Entity-relation graph builder (Victim-Phone-UPI)
│   │   │   ├── analytics/              # PageRank, Betweenness, Louvain communities
│   │   │   └── generator/              # Synthetic graph telemetry generator
│   │   └── tests/
│   │
│   └── common/                         # Shared Cross-Cutting Utilities
│       ├── src/
│       │   ├── exceptions.py           # Domain exception hierarchy
│       │   ├── logging.py              # Structured JSON logging
│       │   ├── constants.py            # Global risk thresholds & enums
│       │   └── file_utils.py           # Safe I/O, hash verification, temp cleanup
│
├── pipelines/                          # MLOps & Offline Model Training
│   ├── training/                       # Offline training scripts
│   │   ├── train_scam_ensemble.py
│   │   ├── train_currency_cnn.py
│   │   └── calibrate_thresholds.py
│   └── evaluation/                     # Adversarial & benchmark evaluation scripts
│
├── data/                               # Dataset Storage (Tracked with DVC / Git LFS)
│   ├── raw/
│   ├── processed/
│   │   └── points.parquet              # Canonical geocoded incident dataset
│   └── README.md                       # Data dictionary & download instructions
│
├── storage/                            # Mounted Local Runtime Storage (Ignored in Git)
│   ├── models/                         # Local cached model weights (.h5, .joblib)
│   ├── uploads/                        # Temporary user uploads
│   └── outputs/                        # Exported analysis reports
│
├── tests/                              # Comprehensive End-to-End & Integration Tests
│   ├── e2e/
│   └── integration/
│
└── scripts/                            # Developer Experience Automation
    ├── dev.bat                         # Windows automated launcher
    ├── dev.sh                          # Linux/macOS launcher
    ├── setup.sh                        # One-command dependency bootstrap
    └── clean.sh                        # Cleans cache, dangling files, and logs
```

---

## 6. Migration Roadmap & Execution Plan

### Phase 1: Repository Hygiene & Dead Code Pruning
1. **Remove Duplicate / Deprecated Root Files:**
   - Delete root `main.py`, `config.py`, `schemas.py`, and root `Dockerfile`.
   - Replace root `requirements.txt` with a clean pinned root developer environment file.
2. **Purge Checked-In Binary Model Bloat:**
   - Delete `models/currency_model.h5`, `module1_currency/best_model_finetuned.h5`, `module1_currency/best_model_stage1.h5`, `module1_currency/currency_model.h5`.
   - Retain a single canonical `currency_model.h5` inside `storage/models/` and add `*.h5`, `*.keras`, `*.joblib` to `.gitignore`.
3. **Eliminate Orphan Submodule & Ghost Repositories:**
   - Remove root `module4_crime/` gitlink and copy needed geocode/jitter scripts into `packages/ai-crime/`.
   - Remove the entire unlinked `et-AI/` directory after migrating graph algorithms.
4. **Add Comprehensive `.dockerignore`:**
   - Exclude `.git`, `.venv`, `node_modules`, `training_output`, `data/sources`, `*.pyc`, `__pycache__`.

### Phase 2: Structural Monorepo Organization
1. **Establish Standard Folder Hierarchy:**
   - Create `apps/api/`, `apps/web/`, `packages/`, `pipelines/`, `data/`, and `tests/`.
   - Move `backend/fastapi/app/` into `apps/api/src/`.
   - Move `frontend/nextjs/` into `apps/web/`.
2. **Package Separation:**
   - Migrate `ml/module1_currency/` $\rightarrow$ `packages/ai-currency/`.
   - Migrate `ml/module2/` $\rightarrow$ `packages/ai-scam/`.
   - Migrate `ml/module4_crime/` $\rightarrow$ `packages/ai-crime/`.
   - Migrate `et-AI/backend/src/graph/` $\rightarrow$ `packages/ai-graph/`.
   - Consolidate `shared/` and root `utils/` $\rightarrow$ `packages/common/`.
3. **Python Package Configuration:**
   - Add `pyproject.toml` or editable package links (`pip install -e packages/common`, etc.) so imports use clean namespaces (`from rakshagrid.common import ...`).

### Phase 3: Backend Clean Architecture & Feature Completion
1. **Implement Native Fraud Graph API (Module 3):**
   - Create `graph_router.py` and `graph_service.py` exposing:
     - `GET /api/v1/graph/nodes` (Victim, Phone, UPI, Bank Account nodes).
     - `GET /api/v1/graph/centrality` (PageRank & Betweenness ranking suspicious mules).
     - `GET /api/v1/graph/clusters` (Louvain community detection for organized fraud syndicates).
2. **Restore Real-Time Streaming SSE Protocol:**
   - Refactor `/api/v1/scam/stream` to return an asynchronous `StreamingResponse(event_generator(), media_type="text/event-stream")`.
3. **De-mock Fake AI Services:**
   - Remove deceptive scam fallback in `audio.py`; return proper structured failure codes.
   - Separate Speech-to-Text from real Acoustic Voice Biometrics / Deepfake Detection.
   - Refactor `/api/v1/crime/predict` to either process media with an actual model or return HTTP 501 Not Implemented until ready.
4. **Hardening & Security:**
   - Fix CORS wildcard with credentials.
   - Standardize error responses to never expose raw stack traces in production (`{"error": true, "code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}`).
   - Add file upload validation (max size 25MB, MIME + magic byte verification).

### Phase 4: Frontend Modernization & Production Polish
1. **Install Leaflet via NPM:**
   - `npm install leaflet` and `npm install -D @types/leaflet`.
   - Remove dynamic `<script>` tag injection in `LeafletCrimeMap.tsx`; use standard React dynamic imports with `{ ssr: false }`.
2. **Connect Graph Explorer to Live Backend:**
   - Update `pages/graph.tsx` to fetch real nodes and links from `GET /api/v1/graph/nodes` instead of hardcoded `mockReports`.
3. **Optimize Graph Canvas Physics:**
   - Implement cooling decay schedule (`alphaTarget(0)`) so the physics engine stops rendering once nodes stabilize.
4. **Replace Fake Supabase with Real API Calls:**
   - Replace `lib/supabase.ts` mock with direct REST API integration into `/api/v1/reports` and `/api/v1/chat`.
5. **Dynamic Conversational Chat:**
   - Connect `chat.tsx` and `FraudShieldChat.tsx` to the backend LLM / Groq service for dynamic, context-aware fraud advisory responses instead of static timeouts.

### Phase 5: Testing, CI/CD & Production Readiness
1. **Fix and Expand Test Suite:**
   - Update `tests/` to target `apps/api/src/main.py:app`.
   - Add integration tests for all 5 modules (Scam, Currency, Graph, Crime, Audio).
   - Add end-to-end API test validation using `pytest-asyncio` and `httpx`.
2. **Multi-Stage Dockerfiles:**
   - Create optimized, lean Dockerfiles for `apps/api` (Python 3.11-slim, non-root user) and `apps/web` (Next.js standalone output).
3. **CI/CD Automation:**
   - Create GitHub Actions workflow for linting, type-checking, automated unit testing, and Docker image validation.

---

## 7. Immediate Actionable Checklist

- [ ] **Step 1:** Delete deprecated root files (`main.py`, `config.py`, `schemas.py`, `Dockerfile`).
- [ ] **Step 2:** Purge redundant binary `.h5` files from git tracking and add `*.h5`, `*.joblib`, `*.parquet` to `.gitignore`.
- [ ] **Step 3:** Remove orphan gitlink `module4_crime` and unlinked folder `et-AI`.
- [ ] **Step 4:** Create standard monorepo folder structure (`apps/`, `packages/`, `data/`, `pipelines/`).
- [ ] **Step 5:** Port Graph Intelligence Python logic from `et-AI` into a native FastAPI router.
- [ ] **Step 6:** Fix SSE streaming endpoint regression in `scam_router.py`.
- [ ] **Step 7:** Install `leaflet` directly in `frontend/nextjs/package.json` and remove CDN script tags.
- [ ] **Step 8:** Replace mock Supabase localStorage layer with real backend API calls.
- [ ] **Step 9:** Update test harness in `tests/test_api.py` to point to the active backend.
- [ ] **Step 10:** Create root `.dockerignore` and multi-stage production Dockerfiles.
