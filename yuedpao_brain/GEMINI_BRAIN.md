# 🧠 Yuedpao Brain - LLM Knowledge Base Schema (GEMINI_BRAIN.md)

This document defines the structure, conventions, and workflows for **yuedpao_brain** — the dedicated Obsidian Knowledge Vault for **Chatbot Yuedpao**. It serves as the master schema for LLM agents and developers.

---

## 🏗️ Vault Architecture

- **`yuedpao_brain/.obsidian/`**: Obsidian Vault configuration (Graph View, core plugins, Wikilink settings).
- **`yuedpao_brain/sources/`**: Raw immutable source specifications and PDF transcripts.
  - `sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md`
- **`yuedpao_brain/wiki/`**: LLM-curated project notes, specifications, models, schemas, and rubrics.
  - `wiki/index.md`: Central catalog and navigation index.
  - `wiki/log.md`: Chronological activity log.
  - `wiki/project-overview.md`: Project summary & Yuedpao brand specs.
  - `wiki/architecture-tiered-router.md`: 4-Tier Router System.
  - `wiki/nlp-spelling-correction.md`: Hybrid Edit Distance + Thai BERT pipeline.
  - `wiki/core-features-rich-menu.md`: Rich Menu 6-grid & 6 Core Features.
  - `wiki/product-catalog-scraping.md`: Web scraping pipeline & domain dictionary.
  - `wiki/carousel-randomization.md`: Top 5 Fair Randomization & LINE Flex Message UX.
  - `wiki/rubric-evaluation-checkpoints.md`: Project rubric score (100%) & key test checkpoints.
  - `wiki/database-schema.md`: SQLite / Supabase data schemas.

---

## 🔄 Operating Workflows

### 1. Ingest & Sync
1. Store raw input files under `sources/`.
2. Extract concepts, architectures, and rules into notes under `wiki/`.
3. Link notes using Obsidian `[[Wikilinks]]` and list them in `wiki/index.md`.
4. Log activity in `wiki/log.md`.

### 2. Query & Knowledge Retrieval
1. Search `wiki/index.md` and consult relevant wiki pages.
2. Adhere strictly to established rules (sub-second router budgets, Edit Distance $\le 2$, Flex Message JSON standards).

---

## 📝 Obsidian Vault Standards

- **Wikilinks**: Use `[[Page Title]]` for notes in the vault.
- **Properties (YAML Frontmatter)**: Include `title`, `date`, `tags`, `sources`.
- **Callouts**: Use Obsidian callouts (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!TIP]`, `> [!WARNING]`).
