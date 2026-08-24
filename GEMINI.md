# 🤖 Chatbot YuedPao Project Context & Guidelines

## 📌 Active Architecture & NLP Standards

### 1. Intent Classification Engine (`app/services/intent_service.py`)
- **Architecture:** 4-Tier Pipeline (Tier 0: Domain Vocab Edit Distance -> Tier 1: Priority Rules -> Tier 2.5: ChromaDB Few-Shot -> Tier 3: BERT E5 Fallback).
- **Performance:** **96.80% Accuracy**, **4.01 ms Latency** on 125 Ground Truth queries.
- **Stopwords:** Filter Thai stopwords but preserve budget/size/fabric terms (`ไม่เกิน`, `งบ`, `ราคา`, `อก`, `สูง`, `หนัก`, `ผ้า`).

### 2. Product Search Engine (`app/services/product_service.py` & `yuedpao_chatbot.db`)
- **Search Pattern:** Hybrid Search combining **BM25 (Exact spec/keyword match)** and **ChromaDB Product Vector (Semantic natural language search)** merged via **Reciprocal Rank Fusion (RRF)**.

### 3. Notebooks & Benchmarks
- All NLP intent & edit distance experiments are maintained in `notebooks/intent_rank/`:
  - `02_intent_extraction.ipynb`
  - `intent_editdistance_and_bert.ipynb`
  - `bm25_chromadb.ipynb`

### 4. Encoding Safeguard
- Windows CLI scripts with Thai text output must include:
  `sys.stdout.reconfigure(encoding='utf-8')`
