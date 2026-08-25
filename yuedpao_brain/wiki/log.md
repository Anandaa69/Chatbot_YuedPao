---
title: Project Activity Log
date: 2026-08-23
tags: [log, history, yuedpao]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 📅 Project Activity & Session Log - Chatbot Yuedpao

Backlink: [[index]]

## 📅 [2026-08-25] - Session 6: 200 QA Expansion, Enhanced Diagnostic Benchmarking & Price Smart Fallback ADR

### 🎯 Key Accomplishments
1. **QA Benchmark Expansion (100 -> 200 Scenarios)**:
   - Created `notebooks/intent_rank/qa_benchmark_200.json` expanding dataset to 200 QA scenarios across 5 categories (40 per category): Exact Model & Color, Natural Language Fabric Touch, Price Boundary, Typo Resilience (with realistic Thai typing errors), Target Persona.

2. **Diagnostic Evaluation Report Overhaul (`notebooks/intent_rank/rrf_test.ipynb`)**:
   - Added `Ground Truth` & `Max Price` columns for complete visibility during debugging.
   - Added candidate display showing exact matched item name and rank (`Matched / Top-1 Item (Rank #X)`).
   - Added `RRF Score` and `Vector Cosine Similarity Score` to quantify retrieval confidence.
   - Introduced `Precision@1` (Top-1 Accuracy: **82.50%**) alongside `Hit Rate@5` (**90.00%**), `MRR@5` (**0.8600**), and P95 Latency (**53.22 ms**).
   - Implemented Automated Error Categorization: Categorized all 20 misses into 17 Semantic Ranking Misalignments (> Top 5) and 3 Price Exceeded cases.

3. **Price Boundary & Smart Fallback Strategy (ADR)**:
   - Investigated 3 Price Boundary misses (`QA-58` Jeans $\le 400\text{฿}$, `QA-59` Babytee $\le 150\text{฿}$, `QA-145` Tailor Cool $\le 380\text{฿}$). Confirmed Hard Filter (`price <= max_price`) correctly executed, but catalog minimum prices are 790฿, 190฿, 490฿.
   - Formulated **Smart Fallback Strategy**: When hard price filter yields 0 items, system automatically relaxes price constraint to fetch closest matching catalog items and responds with an informative, user-friendly recommendation message on LINE UI.

---

## 📅 [2026-08-25] - Session 5: RRF Hybrid Search Optimization, 100 QA Benchmark & Document Expansion

### 🎯 Key Accomplishments
1. **QA Benchmark Dataset & Evaluation Infrastructure Rebuild**:
   - Created `notebooks/intent_rank/qa_benchmark_100.json` containing 100 ground-truth scenarios across 5 categories (20 each): Exact Model & Color, Natural Language Fabric Touch, Price Boundary, Typo Resilience, Target Persona.
   - Rebuilt `notebooks/intent_rank/rrf_test.ipynb` with 9 complete steps including 100 QA dataset evaluation (Hit Rate@5, MRR@5, P95 Latency, per-category breakdown).

2. **RRF Query Pipeline Constraint Validated**:
   - Discovered and validated that Tier 0 `correct_spelling()` must NOT pre-process queries before RRF Hybrid Search (degrades Hit Rate@5 from 92% to 86% due to stopword removal stripping price/size terms).
   - Saved as Section 5 in `.agents/rules/thai_nlp_chatbot_architecture.md`.

3. **Document Expansion Implementation**:
   - Implemented Document Expansion in Step 3 of `rrf_test.ipynb` injecting Thai/English synonym aliases, color translations, and persona usage keywords directly into composite document passages (`passage: ...`).
   - Saved as Section 6 (Document Expansion) and Section 7 (QA Benchmark Standard) in `.agents/rules/thai_nlp_chatbot_architecture.md`.

4. **Embedding Model Experimentation**:
   - Tested `mrp/SimCSE-model-WangchanBERTa-V2` vs `intfloat/multilingual-e5-small`. Confirmed `multilingual-e5-small` remains optimal for semantic retrieval; restored notebook to `multilingual-e5-small`.

### ⏳ Current Status & Next Action Steps
- **Notebook State**: `notebooks/intent_rank/rrf_test.ipynb` is clean, updated with Document Expansion + 100 QA dataset + `intfloat/multilingual-e5-small`, ready for execution.
- **Next Steps when returning**:
  1. Open and run `rrf_test.ipynb` (or execute via script) to measure new Hit Rate@5 with Document Expansion.
  2. Implement SQL/Python Post-filtering for Price Boundary queries in `app/services/product_service.py`.

---

## 📅 [2026-08-25] - Session 4: Unified Rules Synchronization & Obsidian-Graphify Workflow Enforcement

### 🎯 Key Accomplishments
1. **Rule System Unification & Synchronization**:
   - Created `[[obsidian_graphify.md]]` defining the dual knowledge-code workflow: Obsidian Vault (`yuedpao_brain/`) for domain requirements & ADRs, Graphify (`graphify-out/`) for execution call-graphs & module dependencies.
   - Synchronized all 7 system rule files across both `.gemini/rules/` and `.agents/rules/`: `obsidian_graphify.md`, `obsidian_wiki.md`, `graphify.md`, `thai_nlp_chatbot_architecture.md`, `rubric_priority.md`, `line_bot_sdk.md`, and `testing.md`.
2. **Root Context & Enforcement Verification**:
   - Updated root `GEMINI.md` to enforce the complete rule set.
   - Executed `python -m pytest` test suite to verify 100% pass rate.

---

## 📅 [2026-08-23] - Session 3: MVC + Services Folder Skeleton Setup & Architecture Documented

### 🎯 Key Accomplishments
1. **MVC + Services Skeleton Generation**:
   - Created `app/` folder structure: `models/`, `views/`, `controllers/`, `services/`.
   - Created `tests/` folder structure: `test_models.py`, `test_views.py`, `test_services.py`.
   - Initialized `notebooks/01_test_scraper.ipynb` for Scraper POC.
2. **Knowledge Vault Blueprint Sync**:
   - Created `[[project-architecture]]` note in `yuedpao_brain/wiki/` detailing the responsibility of each layer.
   - Updated `[[index]]` sitemap.

---

## 📅 [2026-08-23] - Session 2: Migration to yuedpao_brain Vault & Obsidian Skill Alignment

### 🎯 Key Accomplishments
1. **Vault Migration & Restructuring**:
   - Migrated knowledge base from legacy `Wiki` path to **`yuedpao_brain/`** Knowledge Vault.
   - Initialized `.obsidian/` configuration folder (`app.json`, `core-plugins.json`, `graph.json`) enabling out-of-the-box Obsidian app compatibility.
2. **System Rules Sync**:
   - Updated `.gemini/rules/obsidian_wiki.md` to reference `yuedpao_brain/` path.
   - Updated `.gemini/rules/graphify.md` and `.gemini/rules/testing.md`.
3. **Obsidian Skill & Graph Network**:
   - Linked notes with bidirectional `[[Wikilinks]]`, tags, YAML properties, and GitHub/Obsidian callouts.

---

## 📅 [2026-08-23] - Session 1: Project Initialization & Knowledge Base Customization

### 🎯 Key Accomplishments
1. **Source Document Ingestion**:
   - Ingested raw PDF specification `ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.pdf` into `yuedpao_brain/sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md`.
2. **System Rules & Configuration Alignment**:
   - Customised `.gemini/rules/obsidian_wiki.md` to reflect Yuedpao system components, domain dictionary, and wiki conventions.
   - Updated `.gemini/rules/graphify.md` to list core system nodes (`TieredRouter`, `EditDistanceBERT`, `YuedpaoScraper`, `LineFlexBuilder`, `ProductDatabase`).
   - Configured `.gemini/rules/testing.md` for 4-tier router, candidate generation, scraper fallback, and Flex Message validation.
   - Updated `yuedpao_brain/GEMINI_BRAIN.md` schema definition.
3. **Comprehensive Knowledge Base Build**:
   - Created `[[index]]` sitemap.
   - Built `[[project-overview]]`, `[[architecture-tiered-router]]`, `[[nlp-spelling-correction]]`, `[[core-features-rich-menu]]`, `[[product-catalog-scraping]]`, `[[carousel-randomization]]`, `[[rubric-evaluation-checkpoints]]`, and `[[database-schema]]`.
