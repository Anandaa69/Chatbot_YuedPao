# 🧪 Testing & Automated Verification Rules - Chatbot Yuedpao

## 1. Verification Before Task Completion
- **Never Declare Success Without Running Tests**: After adding or updating code, run `pytest` (or `poetry run pytest`) to ensure all unit and integration test suites pass with 100% success rate.

## 2. Test Coverage & Verification Scenarios
- **Tiered Router Tests (`tests/test_router.py`)**: Verify that Tier 0 exact matches (< 5ms), Tier 1 spelling correction (10-30ms), Tier 2 WangchanBERTa intent matching (30-80ms), and Tier 3 LLM/Human fallback execute as expected.
- **NLP & Candidate Generation Tests (`tests/test_nlp.py`)**: Verify Edit Distance <= 2, Weighted keyboard distance (เกษมณี/ปัตตะโชติ), Thai Soundex, and BERT context ranking for Yuedpao domain terms (e.g. Non-iron, Ultrasoft, Tailor Cool, MotionSkin).
- **Scraper Robustness Tests (`tests/test_scraper.py`)**: Verify HTML parsing resilience, rate limiting, error handling, missing attribute fallbacks, and DB sync.
- **Top 5 Randomization & UX Tests (`tests/test_carousel.py`)**: Verify fair sampling algorithm (`random.sample`), session cache deduplication (preventing back-to-back identical recommendations), and valid LINE Flex Message JSON output (`aspectRatio`, `maxLines`).
