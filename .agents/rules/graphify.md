# 🕸️ Graphify Architecture & Maintenance Rules - Chatbot Yuedpao

## 1. Mandatory Context & Architecture Reading
- **Mandatory Inspection**: Before modifying any codebase modules or routing logic, inspect `graphify-out/GRAPH_REPORT.md` (or `graphify-out/graph.json`) to understand service flows across `scraper/`, `nlp/`, `line_bot/`, and `database/`.
- **Core System Nodes**: Pay special attention to key system components:
  - `TieredRouter` (Tier 0 to Tier 3 dispatch logic)
  - `EditDistanceBERT` (Candidate Generation & BERT Context Scoring)
  - `YuedpaoScraper` (Product catalog & branch scraping pipeline)
  - `LineFlexBuilder` (Flex Message Carousel & Quick Reply builder)
  - `ProductDatabase` (SQLite / Supabase data access layer & Fair Top 5 Randomization)

## 2. Graph Maintenance & Freshness
- **Automatic Graph Updates**: Whenever adding source files or changing module interfaces, run `graphify update .` (or `python -m graphify update .`) to update knowledge graphs.
