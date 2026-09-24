# 🛡️ Raksha Grid — Repository Hygiene & Git Cleanup Audit

**Document Version:** 1.0.0  
**Date:** September 2026  
**Status:** Completed  
**Scope:** Dead code removal, orphan gitlink resolution, model weight deduplication, git/docker hygiene, and baseline verification.

---

## 1. Executive Summary

This document certifies the successful completion of the **Repository Hygiene and Git Cleanup** phase for the Raksha Grid codebase. In accordance with strict constraints:
- **Zero Architectural Restructuring:** Directory hierarchy for active modules was preserved.
- **Zero API Changes:** Backend endpoints and request/response models remain unaltered.
- **Zero ML Logic Modifications:** Inference algorithms, heuristic rules, and postprocessors were preserved intact.
- **Runnable State Maintained:** Backend initialization succeeds cleanly, and all test suites pass with 100% success rate.

---

## 2. Deprecated Root File Verification & Removal

A comprehensive static analysis and import trace was performed across the entire repository prior to removal:

| File Removed | Type / Previous Role | Dependency Verification Findings | Action Taken |
| :--- | :--- | :--- | :--- |
| `main.py` | Legacy single-file FastAPI server | Exclusively exposed legacy Module 2 endpoints. Active application runs `backend.fastapi.app.main:app` (configured in `docker-compose.yml`, `scripts/dev.sh`, `scripts/dev.bat`, `README.md`). Superseded. | **Safely Deleted** |
| `config.py` | Flat legacy configuration | Contained hardcoded relative paths and conflicting thresholds (`DEFAULT_HIGH_THRESHOLD = 0.70`). Active application uses `backend/fastapi/app/config/settings.py` and `shared/configs/base_config.py`. Only legacy root prototypes imported it. | **Safely Deleted** |
| `schemas.py` | Flat legacy Pydantic models | Redundant schemas. Active backend schemas reside in `backend/fastapi/app/schemas/` (`scam_schema.py`, `currency_schema.py`, `crime_schema.py`). Only legacy root `main.py` imported it. | **Safely Deleted** |
| `Dockerfile` | Root Dockerfile | Built container targeting obsolete `uvicorn main:app` without CV/audio system libraries. Active multi-service deployment targets `backend/fastapi/Dockerfile` and `frontend/nextjs/Dockerfile`. | **Safely Deleted** |

### Test Harness Alignment
- `tests/test_rules.py`: Retargeted from deprecated duplicate `models.rules` to active `ml.module2.model.rules.score_lexicon`. Passes 3/3 tests (100%).
- `tests/test_api.py`: Retargeted from `main.py` to `backend.fastapi.app.main.app`. Updated response key validation (`modules` health key). Passes 4/4 tests (100%).

---

## 3. Orphan `module4_crime` Gitlink Resolution

### Git State Audit
- **Mode:** `160000` (gitlink / submodule entry)
- **Commit Reference:** `e05019eafcf129e5ccf03bb32751d5d27c37f8ac`
- **Issue:** No `.gitmodules` file existed in the repository. The commit was absent from the local object database, breaking submodule recursion and causing clone anomalies.
- **Working Tree State:** Directory `module4_crime/` on disk was completely empty.

### Code & Data Preservation Verification
- All Module 4 VigilGrid geospatial crime intelligence source files are fully preserved and operational in `ml/module4_crime/`:
  - `ml/module4_crime/model/hotspot_engine.py` (DBSCAN spatial clustering & patrol allocation)
  - `ml/module4_crime/preprocessing/geocode.py` (Coordinate validation)
  - `ml/module4_crime/preprocessing/jitter.py` (Visual perturbation)
  - `ml/module4_crime/config/crime_config.py` (Configuration)
  - `ml/module4_crime/predict.py` (Module entrypoint)
- Canonical geospatial dataset is preserved at `storage/outputs/processed_points.parquet` (1,827,108 bytes).

### Action Taken
- Purged broken mode 160000 gitlink from Git index via `git rm --cached module4_crime`.
- Cleaned dangling empty directory.

---

## 4. Preservation of `et-AI` (Pending Migration)

### Audit & Inspection
- Directory `et-AI/` contains an unintegrated prototype stack (Express.js backend + older Next.js frontend).
- **Critical Dependency:** `et-AI/backend/src/graph/` contains Module 3 Fraud Network Graph Intelligence logic:
  - `analysis.py`: NetworkX PageRank, Louvain Community Detection, Betweenness Centrality.
  - `graph_builder.py`: Bipartite graph constructor from incident records.
  - `generator.py`: Graph telemetry generator.
  - `synthetic_reports.json`: 56 KB test fixture of victim, phone, and UPI entity links.
- **Migration Status:** Graph intelligence has **not yet been migrated** to the FastAPI backend or a dedicated Python package.

### Action Taken
- In strict adherence to hygiene requirements: **The `et-AI/` directory was NOT deleted**.
- Created `et-AI/PENDING_MIGRATION.md` marking all graph and reporting assets slated for extraction in subsequent monorepo restructuring phases.

---

## 5. Model Weight Deduplication & Canonical Identification

### Deduplication Matrix
All identified `.h5` files were verified to be byte-for-byte identical via SHA-256 cryptographic hashing:
- **File Size:** 16,496,112 bytes (~16.5 MB each)
- **SHA-256 Hash:** `537FA4D3A0DFD4C26787B2C2A72AC2B4ECD1279BE9003D8312C38187AE2CA0A9`

| File Path | Status | Action Taken |
| :--- | :--- | :--- |
| `storage/models/currency_model.h5` | **CANONICAL PRODUCTION COPY** | **Preserved** (Referenced by `ml/module1_currency/config/currency_config.py`) |
| `models/currency_model.h5` | Redundant copy | **Deleted & untracked** |
| `models/currency_model.keras` | 6 KB empty container | **Deleted & untracked** |
| `models/currency_model/` | Redundant SavedModel PB export | **Deleted & untracked** |
| `module1_currency/currency_model.h5` | Redundant copy | **Deleted & untracked** |
| `module1_currency/best_model_finetuned.h5` | Redundant copy | **Deleted & untracked** |
| `module1_currency/best_model_stage1.h5` | Redundant copy | **Deleted & untracked** |
| `module1_currency/models/currency_model.h5` | Redundant copy | **Deleted & untracked** |
| `module1_currency/models/best_model_finetuned.h5` | Redundant copy | **Deleted & untracked** |
| `module1_currency/models/best_model_stage1.h5` | Redundant copy | **Deleted & untracked** |

### Preserved Source & Artifact Files
- `module1_currency/model.ipynb` (Notebook source retained)
- `artifacts/scam-transformer/model.safetensors` (267.8 MB)
- `artifacts/scam-transformer/quantized_model.pt` (138.7 MB)
- `artifacts/ensemble_meta.joblib` (671 bytes)
- `artifacts/tfidf_logreg.joblib` (24.8 KB)
- `artifacts/tfidf_vectorizer.joblib` (142.3 KB)
- `artifacts/calibrated_thresholds.json` (133 bytes)

### Model Deserialization Fix
- Resolved Joblib unpickling namespace constraint in `ml/module2/model/ensemble.py`: added dynamic module alias `sys.modules['models.ensemble'] = sys.modules[__name__]` prior to `joblib.load()`, allowing `ensemble_meta.joblib` to deserialize cleanly without requiring the legacy root `models/` directory or `config.py`.

---

## 6. Git & Docker Exclusion Hardening

### `.gitignore`
Updated with categorized exclusion rules:
```gitignore
# Environment & Secrets
.env
.env.*
.env*.local
*.env

# Python Virtual Environments & Packages
.venv/
...

# Python Cache & Bytecode
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Node.js & Frontend Next.js Build Outputs
node_modules/
.next/
out/
.next-boost/
.vercel/

# ML Model Weights & Artifacts (Ignore binary weights; keep source code & configs)
*.h5
*.keras
*.joblib
*.pt
*.pth
*.onnx
*.safetensors
*.npy
training_output/
storage/models/

# Datasets & Parquet Files
data/raw/
data/processed/
data/sources/
*.parquet

# Runtime Storage & Uploads
storage/uploads/
storage/outputs/
logs/
```

### Root `.dockerignore`
Configured with required clean build exclusions:
```dockerignore
.git
.venv
node_modules
.next
__pycache__
*.pyc
training_output
data/raw
storage/uploads
storage/outputs
.env
*.h5
*.keras
*.joblib
*.pt
*.pth
*.parquet
```

---

## 7. Cache Cleanup Summary

- Cleaned all `__pycache__` directories across the workspace:
  - `backend/fastapi/app/**/__pycache__`
  - `ml/**/__pycache__`
  - `shared/**/__pycache__`
  - `tests/__pycache__`
- Removed `.pytest_cache/`.
- Purged all compiled `.pyc`, `.pyo`, and `.pyd` bytecode files outside `.venv`.

---

## 8. Verification & System Health Report

### Automated Test Suite Execution
```bash
python -m pytest tests/
```
**Result:** `7 passed, 6 warnings in 7.67s` (100% pass rate)
- `tests/test_rules.py::test_legitimate_text` ✅ PASSED
- `tests/test_rules.py::test_digital_arrest_scam_text` ✅ PASSED
- `tests/test_rules.py::test_financial_fraud_text` ✅ PASSED
- `tests/test_api.py::test_health_endpoint` ✅ PASSED
- `tests/test_api.py::test_analyze_text_legit` ✅ PASSED
- `tests/test_api.py::test_analyze_text_scam` ✅ PASSED
- `tests/test_api.py::test_stream_endpoint` ✅ PASSED

### Active Backend Health Verification
```bash
python -c "from backend.fastapi.app.main import app; print(app.title)"
```
**Result:** `Raksha Grid Central Intelligence API` initialized successfully with all routers mounted.

### Runtime Artifact & Dataset Path Verification
- `currency_config.MODEL_PATH` $\rightarrow$ `storage/models/currency_model.h5` ✅ Verified exists
- `crime_config.PROCESSED_POINTS` $\rightarrow$ `storage/outputs/processed_points.parquet` ✅ Verified exists

### Git State
- Staged deletions for deprecated files, duplicate weights, and orphan gitlink.
- No unexpected source code or configuration files deleted or missing.
