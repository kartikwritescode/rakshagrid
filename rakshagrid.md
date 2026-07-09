# Raksha Grid
### AI-Powered Digital Public Safety Intelligence Platform

**Theme:** Smart Cities / Public Safety / Digital Trust / Geospatial Law Enforcement
**Mission:** Shift India's fraud response from *reactive investigation* to *predictive interception* — stopping digital arrest scams and counterfeit currency at the point of contact, not the point of complaint.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Summary](#2-solution-summary)
3. [System Architecture](#3-system-architecture)
4. [Feature List](#4-feature-list)
5. [Tech Stack](#5-tech-stack)
6. [Module-by-Module Build Guide](#6-module-by-module-build-guide)
   - [Module 1: Digital Arrest Scam Detection](#module-1-digital-arrest-scam-detection--alerting)
   - [Module 2: Counterfeit Currency Identification](#module-2-counterfeit-currency-identification-agent)
   - [Module 3: Fraud Network Graph Intelligence](#module-3-fraud-network-graph-intelligence)
   - [Module 4: Geospatial Crime Pattern Intelligence](#module-4-geospatial-crime-pattern-intelligence)
   - [Module 5: Citizen Fraud Shield](#module-5-citizen-fraud-shield-multi-channel)
7. [How It All Links Together](#7-how-it-all-links-together)
8. [Wow-Factor Differentiators](#8-wow-factor-differentiators)
9. [Phased Build Plan (30 Days)](#9-phased-build-plan-30-days)
10. [Performance Targets (State of the Art)](#10-performance-targets-state-of-the-art)
11. [Master Reference Link Index](#11-master-reference-link-index)
12. [Team Roles](#12-team-roles)
13. [Disclaimers](#13-disclaimers)

---

## 1. Problem Statement

India recorded **1.14 million cybercrime complaints in 2023**, up 60% YoY. Within that:

- **Digital arrest scams** — fraudsters impersonate CBI/ED/Customs officers over video call, psychologically trap victims for days, and extract money before anyone can intervene. **₹1,776+ crore** lost in the first 9 months of 2024 alone.
- **Counterfeit currency (FICN)** — high-quality fake ₹500 notes now defeat manual bank-teller detection.
- **Fragmented intelligence** — financial transaction data, call records, and case reports live in silos across agencies, so fraud *rings* are rarely mapped — only individual complaints are filed.

The gap isn't evidence after the fact — it's **real-time detection and multi-agency intelligence fusion** before mass victimization occurs.

---

## 2. Solution Summary

**Raksha Grid** is a single platform with three user-facing surfaces sharing one intelligence core:

| Surface | Users | Core Job |
|---|---|---|
| **Citizen App** (Flutter) | General public | Check calls/messages/UPI IDs for fraud risk, scan currency, report scams |
| **LEA Command Center** (Web) | Police / cyber-cell officers | Geospatial hotspots, fraud network graphs, exportable case intelligence |
| **Bank/Merchant Tool** (Web + mobile) | Tellers, POS operators | Instant counterfeit note verification |

All three are powered by **5 AI modules** running behind one API gateway, described in detail in Section 6.

---

## 3. System Architecture

```
                              ┌───────────────────────────────────────┐
                              │              CLIENT LAYER               │
                              │                                          │
                              │  Flutter App     Next.js Command Center │
                              │  (citizens)        (LEA / officers)      │
                              │                                          │
                              │        Bank/Teller Web Widget            │
                              └───────────────────┬──────────────────────┘
                                                   │  HTTPS / WebSocket
                                                   ▼
                          ┌────────────────────────────────────────────┐
                          │         API GATEWAY (FastAPI)                │
                          │   Auth (Supabase) · Routing · Orchestration  │
                          └───┬─────────┬─────────┬─────────┬───────────┘
                              │         │         │         │
                 ┌────────────▼──┐ ┌────▼─────┐ ┌─▼────────┐ ┌▼─────────────┐
                 │ Scam Detection │ │Counterfeit│ │  Fraud    │ │  Geospatial   │
                 │ Service        │ │ CV Service│ │  Graph    │ │  Intel Service │
                 │ (NLP + LLM)    │ │ (CV/YOLO) │ │  Service  │ │  (Leaflet/GDAL)│
                 └────────┬───────┘ └────┬──────┘ └────┬─────┘ └───────┬───────┘
                          │              │             │               │
                          └──────┬───────┴──────┬──────┴───────┬───────┘
                                 ▼               ▼              ▼
                    ┌─────────────────────────────────────────────────────┐
                    │   Supabase Postgres  │  Neo4j (graph)  │  Redis      │
                    │   Object Storage     │  Vector DB (RAG for chatbot)  │
                    └─────────────────────────────────────────────────────┘
```

**Data flow in one sentence:** every citizen interaction (a call check, a note scan, a UPI lookup) produces a signal → the signal is scored by the relevant AI service → high-risk signals are logged as graph nodes/edges and geotagged points → the command center visualizes the aggregate picture in near real time.

---

## 4. Feature List

### Core (from the problem statement)
- Real-time digital arrest scam classifier with explainable verdicts
- On-device counterfeit currency scanner (works offline)
- Fraud network graph with community detection (mule-network mapping)
- Geospatial hotspot mapping + patrol prioritization
- Multilingual citizen chatbot (WhatsApp + app + web voice)

### Differentiators (Section 8 has full detail)
- Scan-before-you-pay UPI/phone-number risk check
- Officer/agency impersonation verification portal
- "Why was this flagged" explainability panel everywhere
- Real-time cooling-off intervention during an active call
- Deepfake investment-scam / fake celebrity endorsement detector
- Money-mule recruitment-ad scanner
- Silent family panic-button during a suspicious call
- Tamper-evident hash-chained intelligence packets
- Plug-and-play B2B/B2G verification API

---

## 5. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Mobile app | Flutter | Cross-platform, one codebase, great camera/offline support |
| Mobile ML | TensorFlow Lite | On-device, offline-capable inference |
| Backend | FastAPI (Python) | Native fit with ML/CV code, async, fast to build |
| Web dashboard | Next.js + TypeScript | Fast dev, great ecosystem, free hosting on Vercel |
| Auth + DB | Supabase (Postgres) | Free tier, built-in auth, storage, realtime |
| Graph DB | Neo4j AuraDB (free tier) / Community Edition | Purpose-built for network/fraud-ring queries |
| Cache/Queue | Redis + Celery | Free, handles async call-processing jobs |
| Maps | Leaflet + OpenStreetMap | Fully free, no per-request billing |
| Speech-to-Text | `faster-whisper` (open-source Whisper) | Free, self-hosted, good accuracy |
| Translation | AI4Bharat IndicTrans2 | Best-in-class free model for Indian languages |
| LLM API | Groq (Llama 3.3) primary, Gemini free tier backup | Fast + generous free quota |
| CV models | YOLOv8n, MobileNetV3/EfficientNet-B0 | Free/open, lightweight enough for mobile |
| OCR | EasyOCR / Tesseract | Free, good for serial-number reading |
| Vector DB (RAG) | Chroma / Qdrant | Free, self-hostable, simple API |
| Graph algorithms | networkx, Neo4j GDS | Free, well-documented |
| Hosting | Vercel (frontend), Render/Railway (backend), Oracle Cloud free VM (always-on services) | All free tiers |
| WhatsApp integration | Meta WhatsApp Cloud API | Genuinely free up to 1000 conversations/month |

### Optional paid upgrades (not required — flagged if you have budget)
| Tool | Upgrade it provides | Cost |
|---|---|---|
| Twilio | Real live phone-call ingestion instead of pasted transcripts | Trial credit usually covers a hackathon |
| Google Cloud Speech-to-Text | Better Indian-accent/code-switch accuracy than open Whisper | $300 GCP free trial |
| OpenAI Realtime API | Voice-to-voice live interception demo | Pay-per-use, a few dollars |
| Mapbox paid tier | Nicer satellite/hybrid map styling | Free tier is enough for a demo |

---

## 6. Module-by-Module Build Guide

---

### Module 1: Digital Arrest Scam Detection & Alerting

**What it does:** Ingests a call transcript, audio recording, or chat log and returns a real-time scam-risk score with an explanation of exactly which signals fired — before money changes hands.

**How it works (pipeline):**
1. **Speech-to-text** (if audio): `faster-whisper` converts call audio to transcript.
2. **Feature extraction** (rule-based, transparent): authority-impersonation lexicon ("CBI," "warrant," "video verification"), isolation/secrecy language, urgency + payment-channel-switch patterns (UPI/crypto/gift cards), caller-ID anomaly checks.
3. **Classifier**: a fine-tuned transformer (DistilBERT/IndicBERT) trained on labeled transcripts, backed by an LLM few-shot layer for novel patterns the fine-tuned model hasn't seen.
4. **Streaming scoring**: score updates every few seconds of a live/simulated call so you can demonstrate *lead time* before a transfer is requested.
5. **Output**: risk score + fired-feature explanation + auto-drafted alert format compatible with MHA/NCRB reporting fields.

**Build path — basic to advanced:**
- **Basic**: Keyword/regex lexicon scorer with weighted rules → threshold classifier. Buildable in a day, fully explainable.
- **Intermediate**: TF-IDF + Logistic Regression/SVM (scikit-learn) on your labeled dataset — fast, interpretable feature importances.
- **Advanced**: Fine-tune DistilBERT/IndicBERT for sequence classification; add an LLM fallback layer for borderline cases.
- **Stretch**: Streaming WebSocket scoring to simulate live-call interception; add voice anti-spoofing (ASVspoof-style open checkpoints) to flag AI-cloned voices.

**Data sources:**
| Source | Type | Link |
|---|---|---|
| I4C Advisories (official scam pattern documentation) | Real, public | https://i4c.mha.gov.in/advisories.aspx |
| MHA Digital Arrest Advisory (official PDF) | Real, public | https://cybercrime.gov.in/Webform/theme/resources/advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf |
| National Cybercrime Reporting Portal — Advisory Index | Real, public | https://cybercrime.gov.in/Webform/Advisory.aspx |
| Fraud Call India Dataset (Kaggle) | Real, labeled | https://www.kaggle.com/datasets/narayanyadav/fraud-call-india-dataset/code |
| Fraud Call Detection Model (Kaggle notebook, reference implementation) | Code reference | https://www.kaggle.com/code/nithya9404/fraud-call-detection-model/notebook |
| Kaggle discussion — fraud/scam call detection approaches | Community reference | https://www.kaggle.com/discussions/general/144802 |
| Scam and Non-Scam Call Conversation Dataset (Kaggle) | Real/curated | https://www.kaggle.com/datasets/teeconnie/scam-and-non-scam-call-conversation-dataset |
| BothBosu Scam-Dialogue Dataset (HuggingFace) — LLM-synthesized multi-turn scam/non-scam phone dialogues, Apache-2.0 licensed | Synthetic, labeled | https://huggingface.co/datasets/BothBosu/scam-dialogue/viewer |
| BYU-PCCL Scam Call Identification (research repo — LLM-derived + NLP feature pipeline for scam transcripts) | Reference architecture | https://github.com/BYU-PCCL/scam-call-identification |
| "AI Enabled Scam Call Detection" (OpenReview paper — ASR + Translation + Transformer + LLM + RAG architecture, benchmarks multiple approaches) | Research paper | https://openreview.net/pdf?id=IQGxkTCJmt |
| "Scam Calls Detection Using Machine Learning Approaches" (IEEE, LSTM baseline: 85.61% accuracy) | Research paper / benchmark | https://ieeexplore.ieee.org/document/10262695 |
| Text-similarity/plagiarism-style detection controls (useful reference for de-duplicating/validating synthetic transcript diversity) | Tooling reference | https://github.com/AlexMLyman/plagiarism_detector_controls |

> Use the two research papers above as your **benchmark to beat**: the IEEE paper's LSTM hits 85.61% accuracy; the OpenReview paper compares BERT, fine-tuned Gemma, and RAG+LLM approaches. Your hybrid rule+transformer+LLM pipeline should target beating the plain-LSTM baseline and cite these papers in your deck as prior art.

---

### Module 2: Counterfeit Currency Identification Agent

**What it does:** Computer-vision pipeline that verifies a currency note's authenticity via microprint, security-thread, and serial-number checks — deployable on a phone camera or teller desktop.

**How it works (pipeline):**
1. **Detection & crop**: YOLOv8n locates the note and identifies its denomination.
2. **Feature verification**: per-region classifiers/checks — microprint texture classifier, security-thread presence/continuity check, serial-number OCR (EasyOCR) validated against known RBI number-panel formats.
3. **Ensemble classifier**: EfficientNet-B0/MobileNetV3 combines whole-note and per-feature signals into a final real/fake verdict.
4. **On-device deployment**: quantized to TFLite for offline mobile use.

**Build path — basic to advanced:**
- **Basic**: Single CNN (transfer learning, MobileNetV2) — binary real/fake on the whole note image. Trainable in Colab free-tier GPU in under an hour.
- **Intermediate**: Two-stage — YOLOv8n crop/detect denomination first, then a per-denomination classifier (different denominations have different defect signatures).
- **Advanced**: Multi-feature ensemble with per-feature explainability (which specific security feature failed).
- **Stretch**: On-device TFLite for offline field use; document a cheap UV-LED hardware add-on as a roadmap item for the UV-feature-simulation gap.

**Data sources:**
| Source | Type | Link |
|---|---|---|
| Indian Currency Dataset (Apoorv Shekher) | Real images | https://www.kaggle.com/datasets/apoorvshekher/indian-currency-dataset |
| Fake Currency Dataset | Real + fake labeled | https://www.kaggle.com/datasets/lekhansaathvik/fake-currency-dataset |
| Indian Currency Notes Classifier | Real images | https://www.kaggle.com/datasets/gauravsahani/indian-currency-notes-classifier |
| Indian Currency Real vs Fake Notes Dataset | Real + fake labeled | https://www.kaggle.com/datasets/preetrank/indian-currency-real-vs-fake-notes-dataset |
| Indian Currency Notes (Shobhit) | Real images | https://www.kaggle.com/datasets/shobhit18th/indian-currency-notes |
| Indian Currency Note Images Dataset 2020 | Real images | https://www.kaggle.com/datasets/vishalmane109/indian-currency-note-images-dataset-2020 |
| Dataset of Indian and Thai Banknotes with YOLO Annotations (ScienceDirect / Mendeley) | Real, annotated | https://www.sciencedirect.com/science/article/pii/S2352340922002189 |
| Banknote Authentication Dataset | Real, feature-based | https://www.kaggle.com/datasets/gauravduttakiit/banknote |
| RBI Annual Report (official FICN seizure stats + genuine-note security-feature specs) | Real, official | https://www.rbi.org.in/Scripts/AnnualReportPublications.aspx |

> **Synthetic augmentation strategy**: real FICN (fake note) images are correctly not publicly distributed. Build your "fake" training class by augmenting genuine note images from the datasets above — simulate print defects, color shift, blurred/missing microprint, and absent security thread using OpenCV + Albumentations. This is the standard, published methodology in this research area — cite it confidently.

---

### Module 3: Fraud Network Graph Intelligence

**What it does:** Maps phone numbers, UPI IDs, bank accounts, and device fingerprints into a graph, then runs clustering/centrality algorithms to surface coordinated fraud rings and mule-account hubs.

**How it works (pipeline):**
1. **Entities**: victims, phone numbers, UPI IDs/accounts, device fingerprints, case reports.
2. **Edges**: shared-device links, transaction flow, number-reuse, temporal co-occurrence.
3. **Algorithms** (via `networkx` or Neo4j GDS): Louvain community detection → clusters = suspected fraud rings; betweenness/PageRank centrality → mule-account hubs; link prediction (Node2Vec) → suggests probable-but-unconfirmed connections.
4. **Output**: exportable "intelligence packet" (graph + evidence chain + confidence scores + timestamps) formatted for legal auditability.

**Build path — basic to advanced:**
- **Basic**: Static graph in `networkx`, visualize with matplotlib/Gephi.
- **Intermediate**: Load into Neo4j AuraDB (free tier), Cypher queries, basic Louvain community detection.
- **Advanced**: Add centrality analysis + Node2Vec link prediction.
- **Stretch**: Real-time graph growth — every new citizen report/UPI check (see Module 5 + Wow Factor) adds live nodes/edges, re-clustered periodically.

**Data sources:**
| Source | Type | Link |
|---|---|---|
| Crime in India Dataset (NCRB, full historical, 75+ CSVs) | Real, public | https://www.kaggle.com/datasets/rajanand/crime-in-india |
| RBI Annual Report (fraud typology stats, for calibrating synthetic realism) | Real, official | https://www.rbi.org.in/Scripts/AnnualReportPublications.aspx |

> Real fraud-account-level data isn't publicly available anywhere (correctly, for privacy/security reasons). Build a **synthetic entity-graph generator** in `networkx` that replicates known topological patterns (hub-and-spoke mule networks, layered laundering chains) documented in the RBI report and academic literature on money-mule network structure. Your clustering/centrality algorithms running on this synthetic-but-realistic graph are 100% real — be transparent about the data source in your deck.

---

### Module 4: Geospatial Crime Pattern Intelligence

**What it does:** Maps fraud complaints and counterfeit seizures geographically, detects emerging hotspots, and suggests patrol prioritization.

**How it works (pipeline):**
1. Real district-level crime data (NCRB) provides the base distribution.
2. Point-level complaint locations are generated synthetically using population-weighted sampling within real district boundaries.
3. **Analysis**: kernel density estimation for heatmaps, DBSCAN for hotspot clustering, a simple greedy allocator assigns patrol units to top-weighted hotspots.

**Build path — basic to advanced:**
- **Basic**: Static Leaflet map, plot synthetic points colored by crime type.
- **Intermediate**: Heatmap layer + time-slider; choropleth by district using real NCRB numbers as background.
- **Advanced**: DBSCAN-based algorithmic hotspot detection + greedy patrol-allocation optimizer.
- **Stretch**: Time-series forecasting (Prophet) per hotspot for predictive deployment.

**Data sources:**
| Source | Type | Link |
|---|---|---|
| Crime in India Dataset (NCRB, district-level, 2001+) | Real, public | https://www.kaggle.com/datasets/rajanand/crime-in-india |
| RBI Annual Report (FICN seizure geographic trends) | Real, official | https://www.rbi.org.in/Scripts/AnnualReportPublications.aspx |
| I4C Advisories (for categorizing complaint types accurately) | Real, public | https://i4c.mha.gov.in/advisories.aspx |

---

### Module 5: Citizen Fraud Shield (Multi-channel)

**What it does:** A conversational AI, reachable via app/WhatsApp/web-voice, that walks a citizen through a real-time fraud risk assessment and guides them to report via NCRP.

**How it works (pipeline):**
1. **RAG grounding**: advisory content from I4C/cybercrime.gov.in is chunked, embedded, and stored in a vector DB (Chroma/Qdrant) so the chatbot's advice is grounded in real official guidance, not hallucinated.
2. **Brain**: reuses Module 1's scam classifier to score whatever the citizen describes.
3. **Multilingual**: AI4Bharat IndicTrans2 translates between English core-model output and the citizen's chosen regional language.
4. **Channels**: Flutter app (richest UX), WhatsApp Cloud API (genuinely free tier, real integration), Web Speech API (browser-native, stands in for full IVR).

**Build path — basic to advanced:**
- **Basic**: Rule-based decision-tree chatbot — no ML, fast, reliable for common patterns.
- **Intermediate**: RAG pipeline (embed advisories → retrieve → LLM answers grounded in retrieved chunks).
- **Advanced**: Multi-turn slot-filling conversation + IndicTrans2 real-time translation layer.
- **Stretch**: Real WhatsApp Cloud API integration; Web Speech API voice demo.

**Data sources:**
| Source | Type | Link |
|---|---|---|
| I4C Advisories (RAG grounding content) | Real, public | https://i4c.mha.gov.in/advisories.aspx |
| MHA Digital Arrest Advisory PDF | Real, public | https://cybercrime.gov.in/Webform/theme/resources/advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf |
| National Cybercrime Reporting Portal Advisory Index | Real, public | https://cybercrime.gov.in/Webform/Advisory.aspx |
| AI4Bharat IndicTrans2 (22 Indian languages, open-source NMT) | Model/tool | https://github.com/AI4Bharat/IndicTrans2 |

---

## 7. How It All Links Together

Walk through a single end-to-end scenario to see the modules connect:

1. A citizen pastes a suspicious call transcript into the **Citizen App** (Module 5 UI).
2. The app calls the **Scam Detection Service** (Module 1) → returns a high risk score + explanation ("mentions arrest warrant, requests urgent UPI transfer, tells user not to disconnect").
3. The citizen also checks the UPI ID the caller gave them → the same request queries the **Fraud Graph Service** (Module 3) → the UPI ID is either flagged (already linked to prior reports) or added as a new node.
4. The verdict + transcript + UPI-check result are logged as a **case record** with GPS metadata (if shared) → feeds the **Geospatial Service** (Module 4), updating the district heatmap.
5. If the citizen visits a bank shortly after and is asked to withdraw cash, the teller scans any notes handed over using the **Counterfeit CV Service** (Module 2) on the same platform.
6. An officer opens the **LEA Command Center** → sees the new case pinned on the map, connected in the fraud graph to other reports sharing the same UPI ID or device fingerprint, and can export a signed **intelligence packet** (evidence chain + confidence scores) for the case file.

This is why all 5 modules sit behind **one API gateway and one shared database layer** — every module's output becomes another module's input.

---

## 8. Wow-Factor Differentiators

These go beyond the base brief and are what separate a "checklist submission" from a genuinely compelling platform.

| # | Feature | Why it matters | Effort |
|---|---|---|---|
| 1 | **Scan-Before-You-Pay** — instant UPI ID/phone/QR risk check | Turns the fraud graph into a daily-use citizen tool, increases data density with every check | Low |
| 2 | **Officer/Agency Impersonation Verification Portal** | Directly defeats the core mechanic of digital arrest scams (fake authority), not just detects it after | Low |
| 3 | **"Why Was This Flagged" Explainability Panel** everywhere | Builds trust, directly satisfies the evaluation criterion on auditability | Low |
| 4 | **Real-Time Cooling-Off Nudge** mid-call | Interrupts the scam *during* the psychological hold, not just after | Medium |
| 5 | **Deepfake Investment-Scam Detector** | Extends the platform to the other dominant current fraud category using the same voice/video pipeline | Medium |
| 6 | **Money-Mule Recruitment Monitor** | Addresses the supply chain of fraud networks upstream — few teams think this far back | Medium |
| 7 | **Silent Family Panic Button** | Breaks victim isolation without alerting the scammer; strong emotional demo moment | Low |
| 8 | **Tamper-Evident Hash-Chained Evidence** | Cheap to build, strengthens the "court-admissible" evaluation criterion | Low |
| 9 | **B2B/B2G Plug-and-Play Verification API** | Shows deployability beyond a hackathon demo — banks/telecoms could integrate directly | Low (mock integration is enough) |
| 10 | **Cyber Safety Score / Gamified Engagement** | Retention + community-reporting incentive | Low |

---

## 9. Phased Build Plan (30 Days)

The plan is sequenced so that **each phase produces a working, demoable increment** — nothing is left half-integrated until the final week.

### Phase 0 — Foundations (Days 1–2)
- Finalize architecture and repo structure
- Set up Supabase project, Neo4j AuraDB instance, Groq/Gemini API keys
- Scaffold FastAPI backend, Next.js dashboard, Flutter app shells
- **Must complete before anything else** — every module depends on the shared DB schema and API gateway skeleton

### Phase 1 — Data Foundation (Days 3–7)
- Source and label currency image dataset (Module 2 data sources above)
- Build/collect scam-transcript dataset — combine real advisory patterns with the Kaggle/HuggingFace datasets listed in Module 1, generate additional synthetic transcripts via LLM
- Pull real NCRB/data.gov.in crime data (Modules 3 & 4)
- Build the synthetic fraud-graph and geospatial-point generators
- **Why first**: every model in Phases 2–3 depends on this data existing and being labeled

### Phase 2 — Core Model Training (Days 8–14)
- Train currency CNN v1 → evaluate baseline accuracy (Module 2)
- Train scam classifier v1 (TF-IDF/LogReg baseline → then DistilBERT fine-tune) (Module 1)
- Load synthetic fraud graph into Neo4j, run first Louvain clustering pass (Module 3)
- Load geospatial data into Leaflet, build first heatmap (Module 4)
- **Milestone**: each module works standalone via notebook/API call — not yet integrated into the apps

### Phase 3 — Service Integration (Days 15–21)
- Wrap each trained model in a FastAPI microservice behind the API gateway
- Integrate Flutter app ↔ backend for scam-check and currency-check flows
- Integrate Next.js command center with the graph and geospatial services
- Build the RAG chatbot (Module 5) on top of the now-working scam classifier
- Add WhatsApp Cloud API channel
- **Why after Phase 2**: integration requires trained models to already exist; building UI against a stub API wastes time

### Phase 4 — Advanced Features & Differentiators (Days 22–25)
- Add streaming/real-time scoring (WebSockets) for the "lead time" demo
- Build UPI/QR risk-check (Wow Factor #1) — now possible since the fraud graph (Phase 2/3) exists
- Build officer-verification portal (Wow Factor #2)
- Add explainability panels across all UIs (Wow Factor #3)
- Add hash-chained intelligence-packet export (Wow Factor #8)
- **Why after Phase 3**: these features all sit on top of already-integrated core services

### Phase 5 — Testing, Metrics & Polish (Days 26–28)
- Build held-out labeled test sets for scam detection and currency CV → compute precision/recall/F1/confusion matrices (this is what the evaluation rubric scores directly)
- Tune classification thresholds to minimize false positives on citizen-facing tools
- UI/UX polish pass on all three surfaces
- Security/auth hardening, error handling, rate limiting

### Phase 6 — Demo & Submission (Days 29–30)
- Record the end-to-end demo video following the narrative in Section 7
- Finalize architecture diagram and presentation deck with real measured numbers
- Buffer day for last-minute fixes

**Dependency rule of thumb:** *Data → Models → Services → Integration → Differentiators → Metrics → Demo.* Never build a UI against a model that doesn't exist yet, and never skip building the labeled test sets — they're what the evaluation criteria actually score.

---

## 10. Performance Targets (State of the Art)

Use these published benchmarks as your bar to beat and to cite in your deck:

| Task | Published benchmark | Source |
|---|---|---|
| Scam call detection (LSTM baseline) | 85.61% accuracy | IEEE ICoICT 2023 — https://ieeexplore.ieee.org/document/10262695 |
| Scam call detection (BERT / fine-tuned LLM / RAG comparison) | Multiple architectures benchmarked | OpenReview — https://openreview.net/pdf?id=IQGxkTCJmt |
| Currency classification (CNN, 7 denominations) | Reference architecture for comparison | ResearchGate paper referenced alongside Kaggle datasets above |

**Your targets:**
- Scam detection: precision ≥ 90%, recall ≥ 85%, false-positive rate < 5% on citizen-facing verdicts (uncertain cases should fall back to "needs review," not a forced binary answer)
- Currency detection: ≥ 95% accuracy across all 7 denominations under varied lighting/print-quality conditions
- Fraud graph: demonstrate at least one correctly-recovered synthetic ring structure via Louvain clustering
- Geospatial: hotspot detection should visibly track the synthetic-but-realistic complaint density you generated

---

## 11. Master Reference Link Index

### Government / Official Data
- I4C Advisories — https://i4c.mha.gov.in/advisories.aspx
- MHA Digital Arrest Advisory (PDF) — https://cybercrime.gov.in/Webform/theme/resources/advisories/ADVISORYTAU-ADV-003DigitalArrest06.03.2025.pdf
- National Cybercrime Reporting Portal Advisory Index — https://cybercrime.gov.in/Webform/Advisory.aspx
- RBI Annual Report Publications — https://www.rbi.org.in/Scripts/AnnualReportPublications.aspx

### Scam/Fraud Call Detection — Datasets & Research
- Crime in India Dataset (NCRB) — https://www.kaggle.com/datasets/rajanand/crime-in-india
- Fraud Call India Dataset — https://www.kaggle.com/datasets/narayanyadav/fraud-call-india-dataset/code
- Fraud Call Detection Model (notebook) — https://www.kaggle.com/code/nithya9404/fraud-call-detection-model/notebook
- Kaggle discussion on fraud/scam detection — https://www.kaggle.com/discussions/general/144802
- BYU-PCCL Scam Call Identification (GitHub) — https://github.com/BYU-PCCL/scam-call-identification
- Text-similarity detection controls (reference tooling) — https://github.com/AlexMLyman/plagiarism_detector_controls
- Scam and Non-Scam Call Conversation Dataset — https://www.kaggle.com/datasets/teeconnie/scam-and-non-scam-call-conversation-dataset
- BothBosu Scam-Dialogue Dataset (HuggingFace) — https://huggingface.co/datasets/BothBosu/scam-dialogue/viewer
- "AI Enabled Scam Call Detection" (OpenReview) — https://openreview.net/pdf?id=IQGxkTCJmt
- "Scam Calls Detection Using Machine Learning Approaches" (IEEE) — https://ieeexplore.ieee.org/document/10262695

### Counterfeit Currency — Datasets
- Indian Currency Dataset (Apoorv Shekher) — https://www.kaggle.com/datasets/apoorvshekher/indian-currency-dataset
- Fake Currency Dataset — https://www.kaggle.com/datasets/lekhansaathvik/fake-currency-dataset
- Indian Currency Notes Classifier — https://www.kaggle.com/datasets/gauravsahani/indian-currency-notes-classifier
- Indian Currency Real vs Fake Notes Dataset — https://www.kaggle.com/datasets/preetrank/indian-currency-real-vs-fake-notes-dataset
- Indian Currency Notes (Shobhit) — https://www.kaggle.com/datasets/shobhit18th/indian-currency-notes
- Indian Currency Note Images Dataset 2020 — https://www.kaggle.com/datasets/vishalmane109/indian-currency-note-images-dataset-2020
- Indian & Thai Banknotes with YOLO Annotations — https://www.sciencedirect.com/science/article/pii/S2352340922002189
- Banknote Authentication Dataset — https://www.kaggle.com/datasets/gauravduttakiit/banknote

### Tools & Frameworks
- AI4Bharat IndicTrans2 — https://github.com/AI4Bharat/IndicTrans2
- Ultralytics YOLOv8 — https://github.com/ultralytics/ultralytics
- EasyOCR — https://github.com/JaidedAI/EasyOCR
- Albumentations — https://albumentations.ai
- Neo4j AuraDB Free — https://neo4j.com/cloud/aura-free/
- networkx — https://networkx.org
- Leaflet — https://leafletjs.com
- Supabase — https://supabase.com
- Groq Console — https://console.groq.com
- Chroma — https://www.trychroma.com
- WhatsApp Cloud API Docs — https://developers.facebook.com/docs/whatsapp/cloud-api

---

## 12. Team Roles

| Member | Skills | Primary Ownership |
|---|---|---|
| A | Flutter, Supabase, Firebase, ML/DL/NLP | Currency CV pipeline + on-device deployment, Flutter app, citizen chat UI |
| B | AI, Web Dev | Scam-detection NLP pipeline, RAG chatbot brain, multilingual integration, fraud-graph algorithms |
| C | Web Dev, Backend | FastAPI gateway, service orchestration, Next.js command center, Neo4j + geospatial integration, deployment |

Expect overlap during integration phases (3 and 4 especially) — pair up rather than working in strict isolation.

---

## 13. Disclaimers

- **Synthetic data is used deliberately** for fraud-network entities, geospatial complaint points, and part of the scam-transcript training set, because real victim/account-level data is not — and should not be — publicly accessible. This is standard, expected practice in this research area; be transparent about it rather than overclaiming real-data provenance.
- This platform does not currently integrate with live telecom infrastructure, real bank systems, or NCRB's backend — it is architected to support such integration (documented as roadmap items) but demos with transcripts, recordings, and mock APIs.
- All red-flag pattern categories used for scam detection are kept generic (authority impersonation, urgency, isolation, payment-channel switching) rather than literal scripts, both for better model generalization and to avoid producing content that could double as a scam playbook.
