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
