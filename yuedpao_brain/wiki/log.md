---
title: Project Activity Log
date: 2026-08-23
tags: [log, history, yuedpao]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 📅 Project Activity & Session Log - Chatbot Yuedpao

Backlink: [[index]]

## 📅 [2026-08-26] - Session 7: Coupon Ticket & Terms Modal Scraper (`04_coupon_scraper.ipynb`)

### 🎯 Key Accomplishments
1. **Coupon Ticket & Terms Modal Scraper (`notebooks/04_coupon_scraper.ipynb`)**:
   - Created dedicated Jupyter Notebook for scraping coupon containers (`class="w-full flex"`) and left ticket badges (`<div class="flex justify-center items-center flex-col gap-3">` with SVG icon `<g id="bxs:discount">`).
   - Implemented automated popup clicker targeting `<p ...>เงื่อนไขการใช้งาน</p>` to extract **Promo Codes** (e.g. `NEWMEMBER5`, `DIS1000YP1`, `YUEDPAO006`), **Validity Duration** (e.g. `24 ก.ค. 2026 10:00 - 31 ธ.ค. 2033 10:00`), and **Detailed Terms** (e.g. `เมื่อซื้อสินค้า 200 บาทขึ้นไป`).
2. **Database Integration (`coupons` Table)**:
   - Created `coupons` table in `yuedpao_chatbot.db` storing coupon ID, promo code, discount title, min spend, valid duration, detailed condition, eligibility tag, and raw container HTML.
3. **LINE Flex Message Generator**:
   - Implemented `build_line_flex_coupon_carousel()` converting extracted coupon records into LINE Flex Message (Carousel) JSON with `clipboard` action buttons for copying promo codes.

---

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


## 📅 [2026-08-25] - Session 7: Color-Aware Evaluation, Data Hygiene Cleanup & Production Intent Roadmap ADR

### 🎯 Key Accomplishments
1. **Color-Aware Evaluation Framework Implementation (`notebooks/intent_rank/rrf_test.ipynb`)**:
   - Upgraded evaluation framework to validate **`expected_color`** in addition to model keywords.
   - Re-benchmarked 200 QA scenarios across 5 categories and discovered that 15 out of 24 initial misses were **Wrong Color Matches** (model matched correctly, but color variant differed).
   - Added **Color Match Boosting (1.30x Multiplier)** in `rrf_hybrid_search` to prioritize user-requested colors.

2. **Data Hygiene Cleanup (100% SQLite DB Cleaning)**:
   - Discovered and cleaned **142 dirty product category rows** in `yuedpao_chatbot.db` where scraped HTML text (e.g. `ส่งฟรี*\n...`) contaminated SQLite `category` fields.
   - Cleaned all dirty category strings into standardized categories (`Polo`, `Oversize`, `Babytee`, `Crop`, `Running / Activewear`, `Sleeveless`, `กางเกงยีนส์`, `Pants & Shorts`, `Outerwear & Hoodies`, `Accessories`). Verified 0 dirty rows remain.

3. **Final Production Benchmark Results**:
   - **Precision@1**: **86.50%** (173/200 exact color & model top-1 hits!)
   - **Hit Rate@5**: **94.50%** (189/200 top-5 carousel exact hits!)
   - **MRR@5**: **0.8988**
   - **Typo Resilience Hit Rate@5**: **100.00%** (40/40)
   - **P95 Latency**: **44.60 ms**

4. **Production Intent Architecture Roadmap (ADR)**:
   - Finalized production Intent Architecture based on business reality and DB data availability (avoiding LLM dependency & un-scraped OCR images):
     - **🔥 Priority 1: `product_search`**: Specific search by spec, color, price limit, model & collection (handles model/collection search natively via 1.25x RRF Intent Boost).
     - **🎲 Priority 2: `random_recommendation`**: Fair Random Sampling of Top-5 recommendations using `get_fair_top5_recommendations()` excluding session history.
     - **🏷️ Priority 3: `promotion_discount`**: Promotion carousel displaying `End of year sale` and `ส่งฟรี` items from DB.
     - **💡 Optional (Low Priority): `fabric_comparison`**: Knowledge card explaining fabric benefits (Ultrasoft, Tailor Cool, Classic Cotton, Ecotech).
   - Confirmed Size Recommendation and Store Branch Locator are excluded from Scope due to website data being un-scraped image banners.

5. **Code & Test Suite Synchronization**:
   - Synchronized RRF Hybrid Search Engine (Document Expansion 2.0, Intent Boost, Color Boost, Smart Price Fallback) into production service file `app/services/product_service.py`.
   - Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).


### 💡 ADR: Tier 1 Rule-Based & Edit-Distance Routing for Promotion Intent (`promotion_discount`)
- **Decision**: Implemented a **Tier 1 Priority Rule + Tier 0 Edit-Distance** approach for the `promotion_discount` intent to achieve **< 5 ms sub-second latency** and 100% deterministic output.
- **Routing Rules**:
  1. **Daily Deals Trigger (`daily_deal`)**: Keywords `ประจำวัน`, `วันนี้`, `flash sale`, `แฟลชเซล` (with Edit-Distance typo tolerance e.g. `ดีลปะจำวัน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'daily_deal'` and return Daily Deals Carousel Card immediately.
  2. **Monthly Deals Trigger (`monthly_deal`)**: Keywords `ประจำเดือน`, `เดือนนี้`, `ดีลเดือน` (with Edit-Distance typo tolerance e.g. `ดีลปะจำเดือน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'monthly_deal'` and return Monthly Deals Carousel Card immediately.
  3. **Natural Language / Specific Spec Search**: If user asks open-ended or spec-specific promo queries (e.g. *"มีกางเกงยีนส์ลดราคาไหม"*), fall back to `PromotionService.search_promotions()` via RRF Hybrid Search (`yuedpao_promotions_e5` collection).


---

## 📌 Session 8: Promotion Scraper, Persistent ChromaDB & Typo Benchmark (2026-08-26)

### 1. Targeted Deep Promotion Scraper (`notebooks/03_promotion_scraper.ipynb`)
- Built deep detail scraper for Home Page `/countdown/...` links (Daily Deals & Monthly Deals).
- Navigated into individual product pages (`/physical/...`) to extract rich metadata: `description`, `colors`, `sizes_json`, `size_chart_url`, and `gallery_images_json`.
- Populated 13 rich promotional items into SQLite `promotions` table in `yuedpao_chatbot.db`.

### 2. Single Source of Truth DB Cleanup
- Deleted duplicate database `notebooks/yuedpao_chatbot.db` (30 KB).
- Re-routed all notebooks to use root master database `yuedpao_chatbot.db` (`../yuedpao_chatbot.db`).

### 3. Persistent ChromaDB Architecture (`data/chroma/`)
- Updated `ProductService` and `IntentService` to use `chromadb.PersistentClient(path="data/chroma")`.
- Untracked `data/chroma/` and `.vscode/` from Git index and added wildcard rules to `.gitignore`.
- Created persistent collections: `yuedpao_products_e5_search` (695 items), `yuedpao_promotions_e5` (13 items), and `intent_few_shot` (136 items).

### 4. Promotion Service Engine (`app/services/promotion_service.py`)
- Created `PromotionService` engine handling RRF Hybrid Search for promotion items and fast incremental indexing (< 0.5s).

### 5. Promotion Typo Resilience Benchmark Notebook (`notebooks/intent_rank/test_promotion_typo_intent.ipynb`)
- Created dedicated evaluation notebook for promotion queries with Thai typos.
- Enriched `domain_vocab.json` with promotion vocabulary (`ประจำวัน`, `ประจำเดือน`, `โปรโมชัน`, `ส่วนลด`, `คูปอง`, `แฟลชเซล`, `ดีลพิเศษ`).
- Added Tier 1 Promotion Priority Rule in `intent_service.py` and auto-sync guard for `intent_few_shot` collection.
- **Result:** Achieved **93.33% Accuracy** (14/15) and **< 1.5 ms Latency** on Thai promotion typo queries.
- **Verification:** Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).

---

### 📌 Session 9: Intent Classification Comparison & 5-Fold CV Leakage Fix (`compare_editdistance_vs_pure_bert.ipynb`)
- Created and upgraded dedicated experiment notebook `notebooks/intent_rank/compare_editdistance_vs_pure_bert.ipynb` evaluating 5 architectures:
  1. Method 1: Pure BERT (`intfloat/multilingual-e5-small`) on raw queries.
  2. Method 2: Edit Distance + BERT (Tier 0 spell correction pre-processing).
  3. Method 3: Tier 1 Priority Rules + Pure BERT.
  4. Method 4a: 4-Tier Pipeline (No Few-Shot ChromaDB Lookup).
  5. Method 4b: Full 4-Tier Pipeline (With 100% Leak-Free 5-Fold Stratified Cross-Validation Few-Shot Indexing).
- Resolved Data Leakage by isolating ChromaDB Few-Shot indexing to Train Folds (80%) and testing strictly on Test Folds (20%).
- Added Model Warmup step for precise sub-millisecond latency profiling.

---

### 📌 Session 10: LINE Bot SDK v3 & Flask Architecture Integration
1. **Flask Webhook Controller (`app/main.py` & `app/controllers/webhook_controller.py`)**:
   - Initialized Flask Webhook App with `/callback` POST endpoint supporting `linebot.v3.WebhookHandler` and `MessagingApi`.
   - Added mock mode handling for local development testing without real LINE Secret keys.
   - Added `/health` healthcheck route returning JSON server status.
2. **TieredRouter Integration (`app/services/tiered_router.py`)**:
   - Implemented `TieredRouter` dispatching user inquiries across 5 intents (`product_search`, `promotion_discount`, `random_recommendation`, `fabric_comparison`, `size_recommendation`).
3. **LINE Flex Message Views (`app/views/`)**:
   - `flex_carousel.py`: Built `build_product_flex_carousel()` (Top-5 products, 1:1 image aspect, maxLines 2) and `build_coupon_flex_carousel()` with `📋 คัดลอกโค้ด` (`clipboard` action).
   - `flex_fabric.py`: Built 4-Fabric technology guide card & standard size chart card.
   - `quick_replies.py`: Built interactive Quick Reply pills.
   - `rich_menu_views.py`: Built Rich Menu postback action mapping.
4. **Code Hygiene & Cleanup**:
   - Removed unused/redundant placeholder files (`app/services/nlp_spelling.py` and `app/controllers/admin_controller.py`).

---

### 📌 Session 13: Promotion Image URL & SVG Filter Fix
1. **SVG Image Filtering & Product Image Fallback ([app/services/promotion_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/promotion_service.py))**:
   - Resolved issue where images failed to render on LINE Flex Carousel for Daily Deals.
   - Identified root cause: `promotions` table stored SVG badge icon URLs (`https://www.yuedpao.com/images/free-delivery.svg`), which LINE Flex Messaging API `<hero><image>` cannot render.
   - Updated `PromotionService._load_promotions_from_db()` to `LEFT JOIN products` table, replacing SVG badge icons with actual product PNG/JPEG cover image URLs (`https://mp-static.yuedpao.com/...`).
2. **LINE Flex View SVG Guard ([app/views/flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py))**:
   - Added explicit fallback guard in `build_product_flex_carousel()` to intercept any remaining `.svg` or `free-delivery` URLs and replace them with standard YuedPao PNG cover images (`https://mp-static.yuedpao.com/images/logo.png`).
3. **Verification**:
   - Verified clean resolution of PNG/JPEG image URLs across all Daily Deals items.

---

### 📌 Session 14: Daily vs Monthly Deals Separation & 6th Pagination Card
1. **Daily Deals (`daily_deal`) vs Monthly Deals (`monthly_deal`) Separation**:
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


## 📅 [2026-08-25] - Session 7: Color-Aware Evaluation, Data Hygiene Cleanup & Production Intent Roadmap ADR

### 🎯 Key Accomplishments
1. **Color-Aware Evaluation Framework Implementation (`notebooks/intent_rank/rrf_test.ipynb`)**:
   - Upgraded evaluation framework to validate **`expected_color`** in addition to model keywords.
   - Re-benchmarked 200 QA scenarios across 5 categories and discovered that 15 out of 24 initial misses were **Wrong Color Matches** (model matched correctly, but color variant differed).
   - Added **Color Match Boosting (1.30x Multiplier)** in `rrf_hybrid_search` to prioritize user-requested colors.

2. **Data Hygiene Cleanup (100% SQLite DB Cleaning)**:
   - Discovered and cleaned **142 dirty product category rows** in `yuedpao_chatbot.db` where scraped HTML text (e.g. `ส่งฟรี*\n...`) contaminated SQLite `category` fields.
   - Cleaned all dirty category strings into standardized categories (`Polo`, `Oversize`, `Babytee`, `Crop`, `Running / Activewear`, `Sleeveless`, `กางเกงยีนส์`, `Pants & Shorts`, `Outerwear & Hoodies`, `Accessories`). Verified 0 dirty rows remain.

3. **Final Production Benchmark Results**:
   - **Precision@1**: **86.50%** (173/200 exact color & model top-1 hits!)
   - **Hit Rate@5**: **94.50%** (189/200 top-5 carousel exact hits!)
   - **MRR@5**: **0.8988**
   - **Typo Resilience Hit Rate@5**: **100.00%** (40/40)
   - **P95 Latency**: **44.60 ms**

4. **Production Intent Architecture Roadmap (ADR)**:
   - Finalized production Intent Architecture based on business reality and DB data availability (avoiding LLM dependency & un-scraped OCR images):
     - **🔥 Priority 1: `product_search`**: Specific search by spec, color, price limit, model & collection (handles model/collection search natively via 1.25x RRF Intent Boost).
     - **🎲 Priority 2: `random_recommendation`**: Fair Random Sampling of Top-5 recommendations using `get_fair_top5_recommendations()` excluding session history.
     - **🏷️ Priority 3: `promotion_discount`**: Promotion carousel displaying `End of year sale` and `ส่งฟรี` items from DB.
     - **💡 Optional (Low Priority): `fabric_comparison`**: Knowledge card explaining fabric benefits (Ultrasoft, Tailor Cool, Classic Cotton, Ecotech).
   - Confirmed Size Recommendation and Store Branch Locator are excluded from Scope due to website data being un-scraped image banners.

5. **Code & Test Suite Synchronization**:
   - Synchronized RRF Hybrid Search Engine (Document Expansion 2.0, Intent Boost, Color Boost, Smart Price Fallback) into production service file `app/services/product_service.py`.
   - Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).


### 💡 ADR: Tier 1 Rule-Based & Edit-Distance Routing for Promotion Intent (`promotion_discount`)
- **Decision**: Implemented a **Tier 1 Priority Rule + Tier 0 Edit-Distance** approach for the `promotion_discount` intent to achieve **< 5 ms sub-second latency** and 100% deterministic output.
- **Routing Rules**:
  1. **Daily Deals Trigger (`daily_deal`)**: Keywords `ประจำวัน`, `วันนี้`, `flash sale`, `แฟลชเซล` (with Edit-Distance typo tolerance e.g. `ดีลปะจำวัน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'daily_deal'` and return Daily Deals Carousel Card immediately.
  2. **Monthly Deals Trigger (`monthly_deal`)**: Keywords `ประจำเดือน`, `เดือนนี้`, `ดีลเดือน` (with Edit-Distance typo tolerance e.g. `ดีลปะจำเดือน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'monthly_deal'` and return Monthly Deals Carousel Card immediately.
  3. **Natural Language / Specific Spec Search**: If user asks open-ended or spec-specific promo queries (e.g. *"มีกางเกงยีนส์ลดราคาไหม"*), fall back to `PromotionService.search_promotions()` via RRF Hybrid Search (`yuedpao_promotions_e5` collection).


---

## 📌 Session 8: Promotion Scraper, Persistent ChromaDB & Typo Benchmark (2026-08-26)

### 1. Targeted Deep Promotion Scraper (`notebooks/03_promotion_scraper.ipynb`)
- Built deep detail scraper for Home Page `/countdown/...` links (Daily Deals & Monthly Deals).
- Navigated into individual product pages (`/physical/...`) to extract rich metadata: `description`, `colors`, `sizes_json`, `size_chart_url`, and `gallery_images_json`.
- Populated 13 rich promotional items into SQLite `promotions` table in `yuedpao_chatbot.db`.

### 2. Single Source of Truth DB Cleanup
- Deleted duplicate database `notebooks/yuedpao_chatbot.db` (30 KB).
- Re-routed all notebooks to use root master database `yuedpao_chatbot.db` (`../yuedpao_chatbot.db`).

### 3. Persistent ChromaDB Architecture (`data/chroma/`)
- Updated `ProductService` and `IntentService` to use `chromadb.PersistentClient(path="data/chroma")`.
- Untracked `data/chroma/` and `.vscode/` from Git index and added wildcard rules to `.gitignore`.
- Created persistent collections: `yuedpao_products_e5_search` (695 items), `yuedpao_promotions_e5` (13 items), and `intent_few_shot` (136 items).

### 4. Promotion Service Engine (`app/services/promotion_service.py`)
- Created `PromotionService` engine handling RRF Hybrid Search for promotion items and fast incremental indexing (< 0.5s).

### 5. Promotion Typo Resilience Benchmark Notebook (`notebooks/intent_rank/test_promotion_typo_intent.ipynb`)
- Created dedicated evaluation notebook for promotion queries with Thai typos.
- Enriched `domain_vocab.json` with promotion vocabulary (`ประจำวัน`, `ประจำเดือน`, `โปรโมชัน`, `ส่วนลด`, `คูปอง`, `แฟลชเซล`, `ดีลพิเศษ`).
- Added Tier 1 Promotion Priority Rule in `intent_service.py` and auto-sync guard for `intent_few_shot` collection.
- **Result:** Achieved **93.33% Accuracy** (14/15) and **< 1.5 ms Latency** on Thai promotion typo queries.
- **Verification:** Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).

---

### 📌 Session 9: Intent Classification Comparison & 5-Fold CV Leakage Fix (`compare_editdistance_vs_pure_bert.ipynb`)
- Created and upgraded dedicated experiment notebook `notebooks/intent_rank/compare_editdistance_vs_pure_bert.ipynb` evaluating 5 architectures:
  1. Method 1: Pure BERT (`intfloat/multilingual-e5-small`) on raw queries.
  2. Method 2: Edit Distance + BERT (Tier 0 spell correction pre-processing).
  3. Method 3: Tier 1 Priority Rules + Pure BERT.
  4. Method 4a: 4-Tier Pipeline (No Few-Shot ChromaDB Lookup).
  5. Method 4b: Full 4-Tier Pipeline (With 100% Leak-Free 5-Fold Stratified Cross-Validation Few-Shot Indexing).
- Resolved Data Leakage by isolating ChromaDB Few-Shot indexing to Train Folds (80%) and testing strictly on Test Folds (20%).
- Added Model Warmup step for precise sub-millisecond latency profiling.

---

### 📌 Session 10: LINE Bot SDK v3 & Flask Architecture Integration
1. **Flask Webhook Controller (`app/main.py` & `app/controllers/webhook_controller.py`)**:
   - Initialized Flask Webhook App with `/callback` POST endpoint supporting `linebot.v3.WebhookHandler` and `MessagingApi`.
   - Added mock mode handling for local development testing without real LINE Secret keys.
   - Added `/health` healthcheck route returning JSON server status.
2. **TieredRouter Integration (`app/services/tiered_router.py`)**:
   - Implemented `TieredRouter` dispatching user inquiries across 5 intents (`product_search`, `promotion_discount`, `random_recommendation`, `fabric_comparison`, `size_recommendation`).
3. **LINE Flex Message Views (`app/views/`)**:
   - `flex_carousel.py`: Built `build_product_flex_carousel()` (Top-5 products, 1:1 image aspect, maxLines 2) and `build_coupon_flex_carousel()` with `📋 คัดลอกโค้ด` (`clipboard` action).
   - `flex_fabric.py`: Built 4-Fabric technology guide card & standard size chart card.
   - `quick_replies.py`: Built interactive Quick Reply pills.
   - `rich_menu_views.py`: Built Rich Menu postback action mapping.
4. **Code Hygiene & Cleanup**:
   - Removed unused/redundant placeholder files (`app/services/nlp_spelling.py` and `app/controllers/admin_controller.py`).

---

### 📌 Session 13: Promotion Image URL & SVG Filter Fix
1. **SVG Image Filtering & Product Image Fallback ([app/services/promotion_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/promotion_service.py))**:
   - Resolved issue where images failed to render on LINE Flex Carousel for Daily Deals.
   - Identified root cause: `promotions` table stored SVG badge icon URLs (`https://www.yuedpao.com/images/free-delivery.svg`), which LINE Flex Messaging API `<hero><image>` cannot render.
   - Updated `PromotionService._load_promotions_from_db()` to `LEFT JOIN products` table, replacing SVG badge icons with actual product PNG/JPEG cover image URLs (`https://mp-static.yuedpao.com/...`).
2. **LINE Flex View SVG Guard ([app/views/flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py))**:
   - Added explicit fallback guard in `build_product_flex_carousel()` to intercept any remaining `.svg` or `free-delivery` URLs and replace them with standard YuedPao PNG cover images (`https://mp-static.yuedpao.com/images/logo.png`).
3. **Verification**:
   - Verified clean resolution of PNG/JPEG image URLs across all Daily Deals items.

---

### 📌 Session 14: Daily vs Monthly Deals Separation & 6th Pagination Card
1. **Daily Deals (`daily_deal`) vs Monthly Deals (`monthly_deal`) Separation**:
   - Updated `deal_type` in SQLite `promotions` table via script `app/scripts/update_deals.py` (`daily_deal` for items 1-6, `monthly_deal` for items 7-13).
   - Added `deal_type_filter` in `PromotionService.search_promotions()` to strictly isolate daily flash sale items when user asks for `"ประจำวัน"` or `"แฟลชเซล"`, and monthly promo items when user asks for `"ประจำเดือน"`.
2. **6th Pagination "Show More" Carousel Card ([app/views/flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py))**:
   - Added automatic 6th bubble card (`⏩ ดูเพิ่มเติม`) at the end of LINE Flex Carousel whenever query results exceed 5 items.
   - Card features remaining item count (e.g. `ยังมีดีลน่าสนใจอีก N รายการ`) and a `🌐 ดูทั้งหมดบนเว็บ` button to direct users to YuedPao's website.
3. **Verification**:
   - Verified 100% strict deal type isolation and clean rendering of 6th pagination card across test queries.

---

### 📌 Session 29: Targeted Out-of-Stock Heading Match Fix (`h4` / `h5`)
1. **Root Cause Analysis & Fix ([scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py))**:
   - **Discovered Trap**: In-stock product pages (such as `Milky Way`) contain a "สินค้าที่คุณอาจชอบ" (Recommended Products) grid carousel at the bottom of the page. Out-of-stock items in that footer carousel have `<span>สินค้าหมด</span>` badges.
   - Performing a naive global `"สินค้าหมด" in page_text` search caused in-stock pages to be falsely flagged as out of stock.
   - **Fix**: Updated `scrape_product_detail` to target specifically the main product out-of-stock heading element:
     ```python
     out_of_stock_h4 = soup.find(lambda tag: tag.name in ["h4", "h5"] and "สินค้าหมด" in tag.get_text())
     is_available = (out_of_stock_h4 is None)
     ```
2. **Verification & Testing**:
   - Tested live against `Dark Green` (Out of stock) -> `is_available = False` (`0`).
   - Tested live against `Milky Way` (In stock) -> `is_available = True` (`1`).
   - Tested live against `Worm Yellow` (In stock) -> `is_available = True` (`1`).
   - Full pytest suite passed clean (11/11 passed in 87s).














