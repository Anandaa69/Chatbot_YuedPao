# 🧠 Obsidian Vault & Knowledge Base Rules - Chatbot Yuedpao

## 1. Context & Business Logic Reading
- **Mandatory Inspection**: Before implementing features, writing NLP handlers, building scrapers, or modifying LINE Flex messages, consult `yuedpao_brain/wiki/index.md` and relevant vault pages (`project-overview.md`, `architecture-tiered-router.md`, `nlp-spelling-correction.md`, `product-catalog-scraping.md`, `carousel-randomization.md`, `rubric-evaluation-checkpoints.md`, `database-schema.md`).
- **Separation of Concerns**:
  - **Obsidian Vault (`yuedpao_brain/`)**: Product requirements, Tiered Router Architecture, Hybrid NLP (Edit Distance + BERT), Scraping specs, Domain Vocabulary, Rubric checkmarks, `.obsidian` configurations, and Session logs.
  - **Graphify (`graphify-out/`)**: Code execution flow, call graphs, module dependencies (`scraper/`, `nlp/`, `line_bot/`, `database/`).

## 2. Smart Logging Strategy (Selective Persistence)

> [!TIP]
> Log meaningful milestones, architectural decisions, and benchmark results to `yuedpao_brain/`. Avoid logging trivial CLI checks or micro-edits to prevent vault noise.

### 📌 WHEN TO LOG (ต้องบันทึก):
1. **Feature Completion / Major Milestones**: After completing a module (e.g. `TieredRouter`, `YuedpaoScraper`, `FlexBuilder`), update or create the relevant note in `yuedpao_brain/wiki/`.
2. **Architectural Decisions (ADR)**: Document design choices, tradeoffs, and structural changes.
3. **Test Results & Performance Benchmarks**: Log latency measurements, accuracy metrics, and key test pass rates.
4. **Critical Bug Fixes**: Document root causes and fixes for non-trivial bugs.
5. **Session Log Summary**: At the end of a significant session, append a log entry to `yuedpao_brain/wiki/log.md` under `## 📅 [YYYY-MM-DD] - Session X: <Title>`.

### 🚫 WHEN NOT TO LOG (ไม่ต้องบันทึก):
- Trivial CLI inspections (e.g. `list_dir`, `view_file` calls).
- Minor syntax typo fixes or whitespace cleanup.
- Intermediate/scratch work.

## 3. Obsidian Vault Standards
- **Wikilinks**: Use `[[Wikilinks]]` for internal note connections (e.g., `[[architecture-tiered-router]]`).
- **Frontmatter**: Include standard YAML metadata (`title`, `date`, `tags`, `sources`).
- **Callouts**: Use GitHub/Obsidian callout syntax (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!TIP]`, `> [!WARNING]`).
