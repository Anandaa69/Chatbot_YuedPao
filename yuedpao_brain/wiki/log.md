---
title: Project Activity Log
date: 2026-08-23
tags: [log, history, yuedpao]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 📅 Project Activity & Session Log - Chatbot Yuedpao

Backlink: [[index]]

## 📅 [2026-08-27] - Session 33: Fair Random Sampling & Session History Integration (`session_history`) ADR

### 🎯 Key Accomplishments
1. **Router Session History Integration ([app/services/tiered_router.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/tiered_router.py))**:
   - Updated `TieredRouter.route_query(raw_query, session_history)` to accept user session history and pass it to `ProductService.get_fair_top5_recommendations(session_history=session_history)`.
   - Ensures user queries for repeated random recommendations (`random_recommendation`) filter out recently recommended product IDs (last 10 items) to guarantee 100% fresh recommendations.
2. **Automated Verification**:
   - Added `test_product_service_fair_random_sampling_session_history()` in [test_services.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_services.py) asserting zero overlap between consecutive sampling batches.
   - Confirmed test pass rate: **1 PASSED in 19.80s**.

---

## 📅 [2026-08-27] - Session 32: Multi-Intent Comprehensive Automated Test Suite (`tests/test_all_intents.py`) ADR

### 🎯 Key Accomplishments
1. **Multi-Intent Comprehensive Test Suite (`tests/test_all_intents.py`)**:
   - Created dedicated test file [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py) containing 12 automated unit tests across all 6 chatbot intents:
     - `product_search` (Model, color, price filter, popularity/sales volume boost, female preference/style vibe, category filtering for jeans & bags, typo resilience).
     - `coupon_ticket` (Carousel payload verification & `clipboard` action buttons).
     - `promotion_deal` (Daily flash sales & monthly promo deals isolation).
     - `random_recommendation` (Fair 5-item random sampling).
     - `fabric_comparison` (4-Fabric technology guide card).
     - `size_recommendation` (Height & weight size guide card).
2. **Intent Keyword Enrichment in `intent_service.py`**:
   - Expanded `product_triggers` in [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) with category and view keywords (`"อยากเห็น"`, `"กระเป๋า"`, `"กางเกง"`, `"ยีนส์"`, `"โปโล"`, `"ครอป"`, `"เบบี้ที"`).
   - Enriched `INTENT_PASSAGES["product_search"]` passage text to ensure 100% precision in Tier 3 BERT fallback.
3. **Verification & Benchmark Results**:
   - Executed `python -m pytest tests/test_all_intents.py -v`: **100% Pass Rate (12/12 PASSED in 39.60s)**.

---

## 📅 [2026-08-27] - Session 31: Popularity & Sales Volume Boost Search (`sales_vol_boost`) ADR

### 🎯 Key Accomplishments
1. **Sales Volume Database Field & Dynamic SQL Integration**:
   - Updated `ProductService._load_products_from_db()` in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) to dynamically extract `sales_volume` from SQLite `products` table.
   - Injected sales volume metadata into `self.products`, composite document text (`passage: ... | ยอดขาย: X ชิ้น สินค้าขายดี ยอดฮิต`), and ChromaDB `metadatas`.
2. **Popularity Keywords & Tier 1 Intent Routing**:
   - Defined `POPULAR_KEYWORDS` list covering Thai/English popular & best seller terms (`"ขายดี"`, `"ขายดีสุด"`, `"ฮิต"`, `"ฮิตๆ"`, `"ยอดฮิต"`, `"นิยม"`, `"ยอดนิยม"`, `"best seller"`, `"bestseller"`, `"top seller"`, `"ตัวขายดี"`, `"สินค้าขายดี"`, `"ตัวฮิต"`).
   - Updated Tier 1 Priority Rules in [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) to route popular queries directly to `product_search`.
3. **RRF Sales Volume Multiplier (`sales_vol_boost`)**:
   - Added `_detect_query_popular()` helper and log-scaled popularity boost `sales_vol_boost = 1.0 + min(np.log1p(sales_vol) * 0.25, 1.8)` (yielding up to **~2.65x multiplier** for top-selling items) in RRF Engine (`compute_rrf`).
   - Standard queries apply a minor tie-breaker boost (`1.0 + min(np.log1p(sales_vol) * 0.02, 0.15)`).
4. **Verification & Testing**:
   - Added `test_product_service_popular_sales_volume_search()` in [test_services.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_services.py). Confirmed 100% pass rate across automated unit tests.

---

## 📅 [2026-08-27] - Session 12: Female-First Preference Boost (`1.75x`) & Gender Preference RRF ADR

### 🎯 Key Accomplishments
1. **Gender Preference Match Boost (`gender_match_boost`)**:
   - Resolved issue where Unisex Polo shirts with high BM25 scores beat female-specific products (`Gender: female`) on queries like `"ขอดูเสื้อผู้หญิง..."`.
   - Introduced `gender_match_boost` (1.75x) in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) (`compute_rrf`):
     - When `requested_gender == "female"`, products with `Gender: female` receive a **1.75x boost** over `unisex` items.
     - When `requested_gender == "male"`, products with `Gender: male` receive a **1.75x boost** over `unisex` items.
2. **Polo Crop & Female Apparel Keyword Enrichment**:
   - Expanded `PERSONA_SYNONYMS` for `Polo` and `Crop` with `โปโลครอป`, `polo crop`, `ครอปโปโล`, `เสื้อผู้หญิง`.
3. **Verification Results**:
   - Re-tested `'ขอดูเสื้อผู้หญิงน่ารักๆ หน่อย'` and `'ขอดูเสื้อผู้หญิงสวยๆ หน่อย'`: Top 4 items rendered are 100% Female-specific products (`Gender: female`), completely eliminating Unisex Polo LongSleeve from the top ranks!

---

## 📅 [2026-08-27] - Session 11: Fashion Aesthetic & Style Vibe Understanding (`STYLE_VIBE_KEYWORDS_MAP`) ADR

### 🎯 Key Accomplishments
1. **Fashion Aesthetics & Vibe Architecture**:
   - Defined `STYLE_VIBE_KEYWORDS_MAP` in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) covering 3 primary aesthetic categories:
     - `cool`: `"เท่"`, `"เท่ๆ"`, `"สตรีท"`, `"วินเทจ"`, `"เสื้อฟอก"`, `"ยีนส์"`, `"คาร์โก้"`, `"คูล"`
     - `cute`: `"น่ารัก"`, `"น่ารักๆ"`, `"คิ้วท์"`, `"สดใส"`, `"หวานๆ"`, `"y2k"`
     - `chic`: `"สวย"`, `"สวยๆ"`, `"เรียบหรู"`, `"ดูดี"`, `"สุภาพ"`, `"ใส่ทำงาน"`, `"คัตติ้งเนี๊ยบ"`
2. **Document Expansion & Style Boost**:
   - Injected aesthetic synonyms into `PERSONA_SYNONYMS` for `Oversize`, `Polo`, `Crop`, `Babytee`, `Running Roulette`, and `Tie Dye`.
   - Added `_detect_query_style_vibes()` and `style_vibe_boost` (1.35x) in RRF Hybrid Search Engine (`compute_rrf`).
3. **Structured Debug Logging Upgrade**:
   - Enhanced `search_products()` and `TieredRouter` debug output to print `Gender Filter`, `Style Vibes`, `Intents`, `Colors`, `Max Price`, `Category`, and `Gender` attributes per rendered card.
4. **Verification & Testing**:
   - Added `test_product_service_style_vibe_matching()` in `tests/test_services.py`. All 8 unit tests passed cleanly.

---

## 📅 [2026-08-27] - Session 10: Thai Keyboard Typo Mapping & Demographic Demotion ADR

### 🎯 Key Accomplishments
1. **Thai Apparel Keyboard Typo Mapping (`intent_service.py`)**:
   - Resolved tokenization issue where PyThaiNLP split `"เสื้อบืด"` into `['เสื้อ', 'บืด']`, preventing standard Edit Distance from matching 8-char `"เสื้อยืด"`.
   - Added `TYPO_MAP` in `_correct_word()` handling common Thai typos: `"บืด"` ➔ `"ยืด"`, `"บึด"` ➔ `"ยืด"`, `"เสิ้อยืด"` ➔ `"เสื้อยืด"`, `"babytree"` ➔ `"babytee"`.
   - Verified `'ขอดูเสื้อบืดเท่ๆ'` now cleans perfectly to `'ดู เสื้อยืด เท่'`.

2. **Demographic Demotion Factors (`product_service.py`)**:
   - Resolved issue where broad adult queries (`"ขอดูเสื้อยืดหน่อย"`, `"เสื้อยืดเท่ๆ"`) returned Kids/Crop items in Top-5 due to short name matches.
   - Introduced `kids_boost` (0.15x) and `crop_boost` (0.40x) in `compute_rrf`: demotes Kids and Crop items unless explicitly searched for in the user query.

3. **End-to-End Search Verification**:
   - Re-ran live query `'ขอดูเสื้อบืดเท่ๆ'` through `TieredRouter`: Top-5 items returned 100% adult standard/oversize t-shirts with 0 Kids and 0 Crop items.

---

## 📅 [2026-08-27] - Session 9: Fix BabyTee Category & Style Misclassification ADR

### 🎯 Key Accomplishments
1. **Root Cause Analysis & Diagnosis**:
   - Diagnosed why 16 BabyTee products were incorrectly stored in `yuedpao_chatbot.db` with `category = 'Oversize'` and `style_fit = 'Unisex'`.
   - Identified 2 underlying issues:
     a) Scraper assigned `category = 'Oversize'` based on catalog menu URL names during lazy loading crawl.
     b) `_infer_style_fit()` and `_infer_category()` in [scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py) lacked explicit handlers for `babytee` / `เบบี้ที` keywords, defaulting to `Unisex`.
2. **Database Data Correction**:
   - Updated all 16 BabyTee products in `yuedpao_chatbot.db` setting `category = 'เสื้อยืด BabyTee'` and `style_fit = 'BabyTee'`.
3. **Scraper Service Code Upgrade**:
   - Updated `_infer_category()` and `_infer_style_fit()` in [scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py) adding explicit keyword checks for `babytee`, `เบบี้ที`, `crop`, and `ครอป`.
4. **Search Verification & Vector DB Refresh**:
   - Re-indexed ChromaDB and BM25 index via `ProductService`. Confirmed `BabyTee` search query returns Top-5 items with clean `Category: เสื้อยืด BabyTee` and `Style: BabyTee`.

---

## 📅 [2026-08-27] - Session 8: Product Availability Filtering (`is_available`) & Vector DB Re-indexing

### 🎯 Key Accomplishments
1. **Database Schema & `is_available` Column Support**:
   - Identified 287 out-of-stock / unavailable products out of 695 total products in `yuedpao_chatbot.db`.
   - Updated `ProductService._load_products_from_db()` in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) to inspect schema dynamically (`PRAGMA table_info(products)`) and filter products strictly `WHERE is_available = 1`.
2. **ChromaDB & BM25 Search Index Auto-Invalidation**:
   - Reduced active indexed document pool from 695 down to **408 active available products**.
   - Triggered clean auto-re-indexing of ChromaDB vector collection (`yuedpao_products_e5_search`) and BM25 index to prevent recommending out-of-stock items to users.
3. **Automated Unit Testing & Verification**:
   - Added `test_product_service_is_available_filtering()` in [test_services.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_services.py) asserting all loaded products have `is_available == 1`.
   - Verified 100% test pass rate across the service test suite.

---

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

### 📌 Session 30: Scraper Robustness, Concurrency, Prices & Sales Volume ADR
1. **Drawer Menu Crawling & Direct URL Fallback ([app/services/scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py))**:
   - Replaced brittle auto-generated CSS class `span.css-1dwwjt3` with semantic class fallbacks (`span.pointer-cursor` and `.MuiDrawer-paper span`) to withstand front-end MUI Emotion styling updates.
   - Fixed bug where categories without subcategories (e.g. `ACCESSORIES`, `RIB BRA`, `UNWEAR`) were completely skipped by capturing browser direct URL redirections (`page.url`) on drawer element click.
   - Prioritized collection-level landing pages (`ดูทั้งหมด`) to avoid redundant subcategory crawling, accelerating crawl speed by ~5x.
2. **Concurrent Category Scraping ([app/scripts/run_scraper.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/scripts/run_scraper.py))**:
   - Redesigned crawler pipeline from sequential category scraping to concurrent scraping using `asyncio.gather` controlled by `asyncio.Semaphore(3)`.
   - Utilizes separate browser context pages (`browser.new_context`) for memory-isolated concurrent network requests.
3. **Decimal Price Bug & Sales Volume Extraction**:
   - Fixed split decimal prices bug (e.g., 390.50 being split into integer arrays `[390, 50]` where `min` returned `50`) by using float-aware regular expression patterns.
   - Added `sales_volume` (INTEGER DEFAULT 0) column to `products` SQLite schema via auto-migration checks during DB initialization.
   - Shifted sales volume extraction from catalog-level (where it was not rendered by Yuedpao's client-side templates) to product detail page-level parser (`scrape_product_detail()`), supporting standard counts and thousands formats (e.g. `34 ขายแล้ว`, `1.2k ขายแล้ว`).
4. **Allowed Categories Filtering**:
   - Implemented `ALLOWED_MAIN_CATEGORIES` list containing the 28 standard categories requested by the user.
   - Bypasses temporary promotional, seasonal, and event categories (e.g. `CHRISTMAS 2025`, `End of year sale 50%`, `End of year sale 40%`, etc.) to prevent database pollution and redundant product scans.
5. **Verification & Testing**:
   - Verified parallel crawler execution with `--limit-categories 5 --limit 3 --force`: 8 categories (5 discovered + 3 fallbacks) scraped concurrently. Successfully parsed decimal prices (e.g. `390.00`, `990.00`) and sales volume counters into SQLite database.
   - Verified that the allowed categories filtering works perfectly by bypassing seasonal sales categories during menu structure flattening.
   - Verified detail-level sales volume parsing on live products (Sweater `3 ขายแล้ว`, Ultrasoft `34 ขายแล้ว`).
   - Verified that the full pytest suite (18/18 tests) passes clean.
