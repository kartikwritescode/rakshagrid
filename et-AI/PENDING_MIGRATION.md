# ⚠️ Status: Pending Migration

## Reason for Retention

This directory (`et-AI/`) is retained because its Module 3 (Fraud Network Graph Intelligence) algorithms and synthetic datasets have **not yet been migrated** into the unified FastAPI backend / internal ML packages.

In accordance with Raksha Grid repository hygiene protocol:
> *"Remove the obsolete et-AI repository ONLY after extracting all required graph/backend/frontend functionality. If graph code is still required and has not yet been migrated, DO NOT delete it. Instead mark it as pending migration."*

## Components Slated for Migration

| Subsystem / File | Nature of Logic | Target Monorepo Destination |
| :--- | :--- | :--- |
| `backend/src/graph/analysis.py` | NetworkX PageRank, Louvain Community Detection, Betweenness Centrality | `packages/ai_graph/analysis.py` + FastAPI `graph_router.py` |
| `backend/src/graph/graph_builder.py` | Bipartite graph builder from incident reports | `packages/ai_graph/graph_builder.py` |
| `backend/src/graph/generator.py` | Graph telemetry generator | `packages/ai_graph/generator.py` |
| `backend/src/graph/synthetic_reports.json` | Sample victim-phone-UPI test reports | `data/synthetic_reports.json` |
| `backend/src/services/geminiService.ts` | Citizen Fraud Shield advisory RAG | FastAPI `/api/v1/shield` or Next.js route |
| `backend/src/models/Report.ts` | Victim incident report schema | Target PostgreSQL / Supabase incident table |

## Decommissioning Condition

Once Phase 2 (Package Separation) and Phase 3 (Backend Graph Integration) are completed and tests pass against native Python graph services, the entire `et-AI/` directory will be cleanly decommissioned.
