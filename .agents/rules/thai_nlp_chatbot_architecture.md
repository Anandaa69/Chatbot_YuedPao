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
