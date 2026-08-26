---
trigger: always_on
description: Guidelines for Thai NLP Intent Classification and Hybrid Product Search Architecture in YuedPao Chatbot.
---

# 🇹🇭 Thai NLP & Hybrid Search Architecture Guidelines (YuedPao Chatbot)

## 1. Thai Spelling Correction & Corpus Selection
* **Rule:** Always use **Domain Vocab (~375 brand terms)** extracted from official website data for Edit Distance spelling correction instead of massive general Thai corpora (`pythainlp.corpus.thai_words` ~62,100 terms).
* **Rationale:** Domain Vocab processes in **~7.8 ms** per query (25x faster than 202 ms for general corpus) with 100% brand term accuracy.

## 2. 4-Tier Intent Classifier Engine (`app/services/intent_service.py`)
* **Rule:** Maintain the 4-tier hierarchical pipeline for Intent Classification:
  1. **Tier 0 (Spell & Clean):** Edit Distance via Domain Vocab + Thai Stopwords removal (preserve budget/size/fabric keywords: `ไม่เกิน`, `งบ`, `ราคา`, `อก`, `สูง`, `หนัก`, `ผ้า`).
  2. **Tier 1 (Priority Rules):** Regex & keyword triggers for explicit budget, body specs, and fabric comparison queries (< 1 ms latency).
  3. **Tier 2.5 (ChromaDB Few-Shot Vector Lookup):** Cosine similarity search ($\ge 0.70$) against `nlp_ground_truth.json` (125 examples).
  4. **Tier 3 (BERT Passage Fallback):** `intfloat/multilingual-e5-small` cosine similarity with static class passages.
* **Target Metric:** Maintain Accuracy $\ge 96\%$ with average pipeline latency $< 5\text{ ms}$.

## 3. Product Search Architecture (Hybrid Search Engine)
* **Rule:** Product Search in `app/services/product_service.py` must use **Hybrid Search (BM25 + ChromaDB Product Collection)** merged with **Reciprocal Rank Fusion (RRF)**:
  * **BM25:** Handles exact keyword matching for brand names, colors, sizes, and price boundaries.
  * **ChromaDB Product Vector:** Handles natural language semantic inquiries (e.g., *"เสื้อใส่วิ่งออกกำลังกาย เย็นสบาย ไม่ร้อน"*).
  * **RRF Fusion:** Combines ranks from both engines to yield Top-5 relevant items.

## 4. Windows Encoding Safeguard
* **Rule:** Any Python script or test runner executing on Windows CLI that handles Thai text output must explicitly set:
  ```python
  import sys
  sys.stdout.reconfigure(encoding='utf-8')
  ```

## 5. Tier 0 / RRF Query Separation Rule
* **Rule:** Tier 0 spell correction (`correct_spelling()`) must ONLY be used inside the **Intent Classification pipeline**. The raw unchanged query (`raw_query`) must ALWAYS be passed to RRF Hybrid Search.
  * ✅ Intent Classification: `raw_query` ──► `correct_spelling()` ──► Tier 1/2.5/3
  * ✅ Product Search: `raw_query` ──► `rrf_hybrid_search(raw_query)`
  * ❌ **DO NOT** pass `corrected_query` to RRF Hybrid Search directly.
* **Rationale:** `correct_spelling()` filters Thai stopwords, which destroys semantic context needed by BM25 and Vector Search, causing Hit Rate@5 to drop from 92% to 86% (Price Boundary queries collapse by -30%).

## 6. Document Expansion for Synonym & Persona Matching
* **Rule:** When indexing products into ChromaDB and BM25, inject Thai/English synonym aliases, color translations, and persona usage keywords directly into document composite text before indexing:
  * Fabric aliases: `Classic Cotton (ผ้าฝ้าย, ฝ้าย, ฝ้ายธรรมชาติ)`, `Ultrasoft (ผ้านุ่ม, นุ่มพิเศษ, ไม่ยับ, ไม่ต้องรีด)`, `Tailor Cool (ผ้าเย็น, ระบายอากาศ, ใส่ไม่ร้อน)`
  * Color aliases: `Cream (ครีม, สีครีม, Vanilla)`, `Mint (มิ้นท์, สีมิ้นท์, Mint Green)`, `Dark Gray (เทาเข้ม, เทาดำ)`
  * Style & Persona aliases: `Oversize (ทรงหลวม, อกใหญ่, ไหล่ตก, คนอ้วน, ตั้งครรภ์, ตัวใหญ่)`, `Kids (เด็ก, เสื้อเด็ก, ของขวัญเด็ก, เด็กอนุบาล)`, `Polo (ใส่ทำงาน, พนักงานบริษัท, สุภาพ, งานสังสรรค์)`
* **Rationale:** Document expansion allows BM25 and Vector Search to match synonym queries directly without altering the user's raw query string.

## 7. QA Benchmark Standard
* **Rule:** The canonical benchmark dataset for RRF search evaluation is `notebooks/intent_rank/qa_benchmark_100.json` (100 scenarios across 5 categories: Exact Model & Color, Natural Language Fabric Touch, Price Boundary, Typo Resilience, Target Persona).

## 8. Mandatory Obsidian Brain Logging Rule
* **Rule:** At the end of every work session or major architectural decision (ADR), the AI agent MUST automatically append a structured progress log entry to `yuedpao_brain/wiki/log.md`.
* **Rationale:** Preserves project context, system decisions, benchmark performance metrics, and database schema updates across agent conversations.

## 9. Coupon Ticket Scraping & Dual-Layer Indexing Standard
* **Rule:** Coupon data extracted from YuedPao web scrapers (`notebooks/04_coupon_scraper.ipynb`) must be persisted and indexed across two distinct layers:
  1. **Persistence Layer (SQLite `yuedpao_chatbot.db` - table `coupons`):** Store complete coupon records including `coupon_code`, `discount_title`, `min_spend`, `valid_duration`, `detailed_condition`, `eligibility_tag`, and `badge_svg_html`.
  2. **Search Indexing Layer (ChromaDB + BM25):** `PromotionService` (`reload_and_index()`) must load the `coupons` table into `self.documents` as structured passages (`passage: คูปองส่วนลด YuedPao: ... | โค้ดส่วนลด: ... | ...`) to build ChromaDB embeddings (`yuedpao_promotions_e5`) and BM25 corpus for real-time RRF Hybrid Search.
* **Scraper Interaction Guard:** Selenium scrapers targeting interactive modal popups (e.g., `<p>เงื่อนไขการใช้งาน</p>`) MUST dismiss cookie banner overlays (`document.querySelectorAll('button') ... 'ยอมรับทั้งหมด'`) prior to clicking terms links to prevent click interception.
* **LINE Flex UI Standard:** LINE Flex Carousel cards generated for coupons must provide a `clipboard` action button (`📋 คัดลอกโค้ด`) allowing users to tap and copy promo codes (e.g., `NEWMEMBER5`) directly to their device clipboard.


