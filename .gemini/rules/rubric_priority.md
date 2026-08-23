# 🏆 Primary Priority Rule: Rubric Score Criteria (100% Evaluation Standard)

> **CRITICAL MANDATE**: All code writing, module architecture, NLP handlers, web scrapers, and test suites in this project MUST STRICTLY align with the 5 Rubric Criteria and 3 Key Checkpoints below. Achieving "ดีมาก (4–5 คะแนน)" across all dimensions is the HIGHEST PRIORITY.

---

## 🎯 5 Core Evaluation Dimensions (100% Total)

### 1. Web Scraping & Data Pipeline (25% Weight)
- **Target**: Complete data extraction, robust Data Cleaning, precise Attribute extraction (price, name, images, variants, specs), rate limiting (`time.sleep`), and graceful error handling for missing values without web crashes.

### 2. NLP Command Processing (25% Weight)
- **Target**: Intent and Entity extraction accuracy **> 85%**. Robust handling of complex queries, spoken language, and typos via 4-Tier Router + Hybrid Edit Distance ($ED \le 2$) + WangchanBERTa context ranking.

### 3. Top 5 Carousel Logic & Randomization (20% Weight)
- **Target**: Exact 5-item carousel filter. Fair random sampling (`random.sample`), session cache deduplication preventing back-to-back duplicate displays, smooth sliding UI, and zero infinite loops.

### 4. LINE Interface & Chat UX (15% Weight)
- **Target**: Strict LINE SDK v3 Pydantic models. Aspect ratio fixed `aspectRatio: "1:1"` / `"4:3"`, text truncation `maxLines: 2`, responsive Quick Replies (`[🎲 สุ่มใหม่]`), zero JSON errors.

### 5. Code Quality & Performance (15% Weight)
- **Target**: Clean MVC + Services Layered Architecture (`models/`, `views/`, `controllers/`, `services/`), comprehensive error handling, total response latency **< 1.5 - 2.0 seconds** (target sub-second 100–300 ms).

---

## 🧪 3 Key Test Checkpoints (Mandatory Verification)

1. **Scraping Robustness**: Verify system resilience against HTML structure changes and missing values with fallback defaults (`try-except`).
2. **NLP Latency & Edge Cases**: Benchmark response time (< 1.5s total) across compound Thai queries, typos, and edge cases.
3. **Randomization Fairness**: Verify session history cache excludes recently shown items, ensuring zero repetitive sampling loops.
