"""
Tests for Next-Gen Typo Resilience & Two-Pass Hybrid Retrieval System
Validates Keyboard-aware Edit Distance, Thai Soundex Phonetic matching, and Two-Pass Search Relaxation.
"""

import pytest
from app.services.intent_service import IntentService
from app.services.product_service import ProductService
from app.services.tiered_router import TieredRouter


@pytest.fixture(scope="module")
def intent_service():
    return IntentService()


@pytest.fixture(scope="module")
def product_service():
    return ProductService.get_instance()


@pytest.fixture(scope="module")
def tiered_router():
    return TieredRouter()


def test_thai_soundex_matching(intent_service):
    """Test Thai soundex matching on common brand phonetic misspellings."""
    assert intent_service._soundex_match("ยึดเป่า") == "ยืดเปล่า"
    assert intent_service._soundex_match("เสือยืบ") == "เสื้อยืด"


def test_spell_correction_phonetic_and_keyboard(intent_service):
    """Test full spell correction on severe typos."""
    corrected, _ = intent_service.correct_spelling("เสือยืบ สีดัม")
    assert "เสื้อยืด" in corrected or "ดำ" in corrected

    corrected_brand, _ = intent_service.correct_spelling("ยึดเป่า ผ้านุ่ม")
    assert "ยืด" in corrected_brand and "เปล่า" in corrected_brand

    corrected_polo, _ = intent_service.correct_spelling("โปลง คอปก")
    assert "โปโล" in corrected_polo


def test_intent_prediction_on_typos(intent_service):
    """Test that IntentService accurately classifies queries even with severe typos."""
    res1 = intent_service.predict_intent("เสือยืบ สีดำ ไม่เกิน 300")
    assert res1["intent"] == "product_search"

    res2 = intent_service.predict_intent("เสื้อเด ผ้านุ่ม")
    assert res2["intent"] == "product_search"

    res3 = intent_service.predict_intent("อันต้าซอบ ต่างกับ ทเลอคูล ยังไง")
    assert res3["intent"] == "fabric_comparison"

    res4 = intent_service.predict_intent("หวัดดีจ้าาา")
    assert res4["intent"] == "greeting"


def test_two_pass_product_search_fallback(product_service):
    """Test that Two-Pass Search succeeds on typos that yield 0 results in Pass 1."""
    raw_typo = "เสือยืบสีดัม"
    corrected = "เสื้อยืด สีดำ"
    res = product_service.search_products(
        raw_query=raw_typo,
        top_k=5,
        offset=0,
        return_dict=True,
        corrected_query=corrected
    )
    assert len(res["products"]) > 0
    assert "fallback_message" in res
    assert "เสื้อยืด สีดำ" in res["fallback_message"] or "เสือยืบสีดัม" in res["fallback_message"]


def test_tiered_router_typo_end_to_end(tiered_router):
    """Test end-to-end user query routing with severe typos."""
    res = tiered_router.route_query("เสือยืบ สีดำ ไม่เกิน 400", user_id="test_typo_user")
    assert res["intent"] == "product_search"
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0
