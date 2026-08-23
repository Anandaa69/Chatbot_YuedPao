---
title: Index Catalog & Master Navigation
date: 2026-08-23
tags: [yuedpao, index, navigation, sitemap, obsidian-vault]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 📚 Master Index & Sitemap - Chatbot Yuedpao

Welcome to **yuedpao_brain** — the Obsidian Knowledge Vault for **Chatbot Yuedpao** (LINE Official Account Chatbot for Yuedpao - ยืดเปล่า).

> [!NOTE]
> This Obsidian Knowledge Vault documents the complete architecture, NLP pipeline, database schemas, web scraping specifications, and evaluation rubrics for the Yuedpao LINE Chatbot.

---

## 📌 Master Navigation

### 1. 🚀 Project Overview & Business Requirements
- [[project-overview]] — Project background, brand specifications, business goals, and target user personas.
- [[project-architecture]] — Codebase Architecture blueprint (MVC + Services Layered Pattern).
- [[line-sdk-v3-spec]] — LINE Messaging API SDK v3 Enforcement Specification.

### 2. 🏗️ System Architecture & Routing
- [[architecture-tiered-router]] — 4-Tier Hierarchical Router System (Tier 0 Exact Match to Tier 3 Fallback/LLM).
- [[database-schema]] — SQLite / Supabase / JSONL data schemas for products, branches, FAQs, and user session cache.

### 3. 🧠 Thai NLP & Intelligent Processing
- [[nlp-spelling-correction]] — Hybrid Edit Distance (Candidate Generation) + Thai BERT (WangchanBERTa / mBERT Context Scoring), Soundex, Keyboard Proximity, and Entity Extraction.

### 4. 🎨 User Experience & Features
- [[core-features-rich-menu]] — 6-Grid Rich Menu structure and 6 Core Chatbot Features (Smart Fitting, Shopping/Promo, Store Locator O2O, After-Sales, Loyalty LIFF, Live Agent).
- [[carousel-randomization]] — Top 5 Carousel Fair Randomization algorithm, Session History Cache, and LINE Flex Message JSON specs.

### 5. 🕷️ Data Engineering & Scraping
- [[product-catalog-scraping]] — Web Scraping Pipeline for Yuedpao.com, Domain Vocabulary dictionary, Product Specifications, and Store Geolocations.

### 6. 📊 Evaluation & Quality Assurance
- [[rubric-evaluation-checkpoints]] — Project Evaluation Rubric (100%), Key Checkpoints, Edge Case Testing, and Latency Benchmarks.
- [[log]] — Chronological activity and development log.

---

## 🔗 Raw Source Documents
- [[sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao|Original PDF Specifications Document]]
