# 🧠🕸️ Obsidian Vault & Graphify Architecture Rules - Chatbot Yuedpao

## 1. Dual Knowledge & Code Navigation Workflow
Before writing code or refactoring modules, agents must consult two primary knowledge layers:
- **Obsidian Vault (`yuedpao_brain/`)**: Stores domain business rules, 4-Tier Router specs, hybrid NLP pipeline, web scraping specs, rubric score criteria, and development session logs. Start at `yuedpao_brain/wiki/index.md`.
- **Graphify Code Graph (`graphify-out/` or module dependency graph)**: Stores execution call-graphs, module relationships, and service dispatches (`intent_service`, `product_service`, `tiered_router`, `webhook_controller`, `scraper_service`).

## 2. Separation of Concerns
| System | Directory | Primary Purpose | Key Components |
|---|---|---|---|
| **Obsidian Vault** | `yuedpao_brain/` | Domain requirements & architectural decisions | `wiki/index.md`, `wiki/architecture-tiered-router.md`, `wiki/nlp-spelling-correction.md`, `wiki/log.md` |
| **Graphify Graph** | `graphify-out/` | Code structure & module dependency graph | Core nodes: `TieredRouter`, `IntentService`, `ProductService`, `YuedpaoScraper`, `LineFlexBuilder` |

## 3. Obsidian Knowledge Vault Standards
- **Wikilinks**: Use `[[Wikilink]]` format for internal connections (e.g. `[[architecture-tiered-router]]`).
- **Frontmatter**: Include standard YAML metadata (`title`, `date`, `tags`, `sources`).
- **Callouts**: Use GFM/Obsidian callouts (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!TIP]`, `> [!WARNING]`).
- **Selective Logging**: Document milestones, ADRs, test benchmarks, and critical bug fixes in `yuedpao_brain/wiki/log.md`. Avoid trivial micro-edits.

## 4. Graphify Freshness & Enforcement
- When adding new modules, routes, or service dependencies, maintain/update knowledge graph declarations.
- Verify module call-graphs before modifying function signatures or cross-service communications.
