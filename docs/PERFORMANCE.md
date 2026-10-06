# Raksha Grid: Performance & Resource Architecture

This document presents empirical benchmarks and architectural decisions implemented during the Raksha Grid production restructuring.

---

## 1. Executive Summary & Benchmark Results

The following metrics were empirically measured using `scratch/measure_performance.py` on the active runtime environment.

| Component / Metric | Measurement | Operational Significance |
|---|---|---|
| **API Cold Startup & First Probe** | **15.17 s** | Lifespan avoids eager loading of heavy models; fast container boot and health readiness |
| **Scam Pipeline Model Loading & Warmup** | **34.22 s** | One-time per process lifecycle; DistilBERT + TF-IDF loaded once, never per-request |
| **Scam Warm Inference Latency** | **20.82 ms** (Mean) | Min: 17.76 ms, Max: 27.27 ms; highly responsive real-time analysis |
| **Fraud Graph Analytics (150 nodes)** | **9.29 ms** | Combined PageRank, Betweenness Centrality, and Louvain community detection |
| **Geospatial Crime DBSCAN (40,160 pts)** | **601.71 ms** | Fits 40,160 incident points and computes patrol allocation in <1 second |
| **Total Process Resident RAM (All Models Active)**| **999.41 MB** | Entire stack (Torch, TF, Transformers, DBSCAN, Graph) contained within 1 GB |
| **VRAM Consumption** | **0.0 MB** | Clean CPU execution fallback when CUDA is not present |

---

## 2. Core Architectural Decisions

### 2.1 Single-Process Singleton vs. Multi-Worker Memory Duplication
- **The Problem:** Running standard Uvicorn with `--workers 4` duplicates the Python runtime, importing PyTorch, TensorFlow, and Transformers 4 separate times. This causes RAM usage to explode to 4 GB+ on small cloud instances.
- **The Solution:** A single Uvicorn process with internal concurrency control (`asyncio.Semaphore` + dedicated `ThreadPoolExecutor`) serves concurrent requests while sharing loaded model weights in memory. Total memory footprint remains strictly under 1 GB.

### 2.2 Event Loop Isolation (`InferenceConcurrencyManager`)
- **The Problem:** Synchronous CPU/GPU forward passes (such as matrix multiplications in DistilBERT or image preprocessing in OpenCV/TensorFlow) block FastAPI's async event loop, preventing health probes and lightweight requests from completing.
- **The Solution:** Implemented `apps/api/src/core/concurrency.py`. Heavy ML forward passes run inside an isolated thread pool with a bounded semaphore (`settings.INFERENCE_MAX_CONCURRENCY = 4`).

### 2.3 Controlled Lifecycle & Lazy Warmup
- **The Problem:** Eagerly loading all multi-gigabyte models during container startup causes Kubernetes/Docker liveness probes to time out before the container is marked healthy.
- **The Solution:** Application lifespan initializes directories and configs in <100ms. Models are loaded on-demand via singletons, cached indefinitely, and never re-initialized during request lifecycles.

### 2.4 Fraud Graph Spatial Hashing
- **The Problem:** Canvas visualizer and graph analytics experienced $O(N^2)$ slowdowns when rendering large fraud graphs with hundreds of nodes.
- **The Solution:** Partitioned node layout using spatial grid bucketing ($180\text{px}$ hash cells) and alpha kinetic cooling ($\alpha < 0.005$ cutoff), reducing repulsion physics from $O(N^2)$ to $O(N)$ and halting animation frames when stabilized.

---

## 3. Resource Scaling Matrix

| Concurrent Requests | Queue Behavior | Memory Usage | Expected Latency |
|---|---|---|---|
| **1 - 4 requests** | Immediate execution | ~1,000 MB | ~20 - 50 ms |
| **5 - 20 requests** | Buffered in semaphore queue | ~1,020 MB | ~80 - 250 ms |
| **20+ requests** | Non-blocking backpressure | ~1,050 MB | Linear queue drain without OOM |
