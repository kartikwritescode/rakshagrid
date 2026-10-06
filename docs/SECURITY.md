# Raksha Grid: Security Architecture & Threat Mitigation Guide

This document details the production security controls, authentication safeguards, input validation pipelines, and remaining threat mitigations for Raksha Grid.

---

## 1. Authentication & Authorization Controls

### 1.1 Protected Endpoints & Sensitivity Classification
All endpoints exposing public-safety intelligence, citizen reports, syndicate topologies, or administrative capabilities are strictly protected:

| Sensitivity Tier | Endpoints | Access Guard |
|---|---|---|
| **Tier 1: High Sensitivity** | `/api/v1/crime/incidents`, `/api/v1/crime/hotspots`, `/api/v1/crime/patrol-allocation` | Requires `X-API-Key` or `Authorization: Bearer <token>` |
| **Tier 1: High Sensitivity** | `/api/v1/graph/*` (`/nodes`, `/centrality`, `/clusters`, `/`) | Requires `X-API-Key` or `Authorization: Bearer <token>` |
| **Tier 1: High Sensitivity** | `/api/v1/reports/*` (`POST /`, `GET /`, `GET /{id}`) | Requires `X-API-Key` or `Authorization: Bearer <token>` |
| **Tier 1: High Sensitivity** | `/api/v1/chat` (AI Advisory Engine) | Requires `X-API-Key` or `Authorization: Bearer <token>` |
| **Tier 2: Public / Edge** | `/health`, `/docs`, `/openapi.json`, `/api/v1/currency/predict`, `/api/v1/audio/detect` | Open citizen edge processing (subject to upload rate limits) |

### 1.2 Authentication Mechanics
- **Credential Support:** Dual header ingestion supporting `X-API-Key: <key>` and standard RFC 6750 `Authorization: Bearer <token>`.
- **Timing Attack Mitigation:** Constant-time cryptographic comparison via `hmac.compare_digest` to prevent side-channel timing analysis.
- **HTTP Status Codes:**
  - `401 Unauthorized`: Returned when authentication credentials are completely missing or empty.
  - `403 Forbidden`: Returned when credentials are supplied but fail authorization comparison.
  - `WWW-Authenticate: Bearer, ApiKey` challenge header included on 401 challenges.

---

## 2. CORS Policy & Cross-Origin Protections

- **Wildcard Disallowance:** The `*` wildcard origin is strictly forbidden and actively filtered out when `allow_credentials=True`.
- **Environment Ingestion:** Allowed origins are loaded from `CORS_ORIGINS` (comma-delimited), defaulting to explicit localhost dev ports (`http://localhost:3000,http://127.0.0.1:3000`).
- **Allowed Methods & Headers:** Restricted to `GET, POST, PUT, DELETE, PATCH, OPTIONS` with strict header allowlisting (`Content-Type, Authorization, X-API-Key, X-Request-ID, Accept`).

---

## 3. File Upload Security & Malware Defense

Upload endpoints (`/api/v1/currency/predict`, `/api/v1/audio/detect`, `/api/v1/audio/transcribe`) implement defense-in-depth:

```
Uploaded File
     │
     ├── 1. Chunked Stream Read -> Enforces 25 MB hard ceiling (HTTP 413)
     │
     ├── 2. Path Traversal Neutralization -> Strips '..', '/', '\', and rejects null bytes
     │
     ├── 3. Extension Whitelist -> Checks against {.jpg, .jpeg, .png, .webp} or {.wav, .mp3, .ogg, .flac, .m4a}
     │
     ├── 4. Magic Byte Verification -> Inspects genuine binary signatures (never trusts client Content-Type)
     │
     └── 5. Auto-Cleaning Temp Files -> Context manager guarantees immediate unlinking in finally blocks
```

---

## 4. Error Shielding & Information Leakage Prevention

- **Stack Trace Suppression:** Unhandled internal server errors (`500`) log full tracebacks to internal server logs while returning generic, safe responses:
  ```json
  {
    "error": true,
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred. Please contact system support.",
    "request_id": "req-20260924-..."
  }
  ```
- **Internal Path Neutralization:** Absolute filesystem paths (`C:\...`, `/home/...`), connection strings, database credentials, and internal model paths are never returned to clients.
- **Request ID Tracing:** Every error response contains a cryptographically unique `request_id` header and payload field for correlating client bug reports with server logs.

---

## 5. Privacy & Automated PII Masking

The centralized logger in `packages/common/rakshagrid/common/logging/logger.py` includes a `PIIMaskingFilter`:
- **Phone Numbers:** Masked to preserve only telecom circle and trailing verification digits (`+91 98****3210`).
- **UPI IDs:** Redacted to protect citizen identity (`u***r@oksbi`).
- **Bank Accounts:** Obfuscated to last 4 digits (`********9012`).
- **Auth Tokens:** Bearer tokens and API keys are replaced with `[REDACTED]`.

---

## 6. ML Concurrency & DoS Prevention

- **Event Loop Isolation:** Heavy matrix multiplications (TensorFlow, PyTorch, Whisper STT) are offloaded to an isolated worker thread pool via `apps/api/src/core/concurrency.py`.
- **Semaphore Throttling:** Bounded to `settings.INFERENCE_MAX_CONCURRENCY = 4` to prevent GPU VRAM exhaustion or memory starvation under DDoS conditions.
- **Model Singletons:** All ML weights are loaded once per process and shared across threads.

---

## 7. Remaining Production Security Recommendations

1. **IP Rate Limiting:** Implement token-bucket or sliding-window rate limiting (e.g., `slowapi` or Redis-backed API gateway) on `/api/v1/currency/predict` and `/api/v1/scam/analyze-text` to throttle volumetric abuse.
2. **PostgreSQL Row-Level Security (RLS):** When migrating the in-memory graph service to PostgreSQL, configure RLS to partition sensitive citizen incident reports by investigating precinct jurisdiction.
3. **ClamAV Antivirus Scanning:** For enterprise deployments receiving arbitrary user attachments, pipe uploaded image/audio streams through a local ClamAV daemon sidecar prior to model inference.
4. **Key Rotation & Vault:** Store `API_KEY` and `GROQ_API_KEY` in AWS Secrets Manager or HashiCorp Vault with automated 90-day rotation schedules.
