"""
Comprehensive Automated Test Suite for all YuedPao Chatbot Intents
Tests TieredRouter, IntentService, ProductService, PromotionService, and LINE Flex Views.
"""

import pytest
from app.services.tiered_router import TieredRouter


@pytest.fixture(scope="module")
def router():
    return TieredRouter()


def test_intent_product_search_model_color_price(router):
    res = router.route_query("อยากได้เสื้อยืด Oversize สีครีม ผ้านุ่มๆ ไม่เกิน 400 บาท")
    assert res["intent"] == "product_search"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert res["flex_payload"]["type"] == "carousel"
    assert len(res["flex_payload"]["contents"]) > 0


def test_intent_product_search_best_seller_popularity(router):
    res = router.route_query("ขอดูตัวขายดีที่สุดในร้านหน่อย")
    assert res["intent"] == "product_search"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert res["flex_payload"]["type"] == "carousel"
    assert len(res["flex_payload"]["contents"]) > 0


def test_intent_product_search_female_style_vibe(router):
    res = router.route_query("ขอดูเสื้อผู้หญิงน่ารักๆ สดใสๆ หน่อย")
    assert res["intent"] == "product_search"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0


def test_intent_product_search_jeans(router):
    res = router.route_query("มีกางเกงยีนส์ยืดขายไหม")
    assert res["intent"] == "product_search"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0


def test_intent_product_search_bag(router):
    res = router.route_query("อยากเห็นกระเป๋าสะพายข้าง Yuedpao")
    assert res["intent"] == "product_search"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0


def test_intent_coupon_ticket(router):
    res = router.route_query("ขอโค้ดส่วนลดกับคูปองล่าสุดหน่อย")
    assert res["intent"] == "coupon_ticket"
    assert "reply_text" in res and "คูปอง" in res["reply_text"]
    assert res["flex_payload"] is not None
    assert res["flex_payload"]["type"] == "carousel"
    # Verify clipboard action in coupon flex cards
    first_card = res["flex_payload"]["contents"][0]
    button_actions = [
        btn.get("action", {}).get("type")
        for btn in first_card.get("footer", {}).get("contents", [])
    ]
    assert "clipboard" in button_actions or any("clipboard" in str(b) for b in button_actions)


def test_intent_promotion_deal_daily(router):
    res = router.route_query("มีสินค้าโปรโมชันแฟลชเซลประจำวันไหม")
    assert res["intent"] in ["promotion_deal", "promotion_discount"]
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0


def test_intent_promotion_deal_monthly(router):
    res = router.route_query("ขอดูดีลโปรโมชั่นประจำเดือนนี้")
    assert res["intent"] in ["promotion_deal", "promotion_discount"]
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0


def test_intent_random_recommendation(router):
    res = router.route_query("ลองสุ่มแนะนำเสื้อให้หน่อย ไม่รู้จะเลือกอะไรดี")
    assert res["intent"] == "random_recommendation"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) == 5


def test_intent_fabric_comparison(router):
    res = router.route_query("ผ้า ultrasoft กับ tailor cool ต่างกันยังไงและซักแล้วยับไหม")
    assert res["intent"] == "fabric_comparison"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert res["flex_payload"]["type"] == "bubble"


def test_intent_size_recommendation(router):
    res = router.route_query("สูง 175 หนัก 70 ใส่เสื้อยืดไซส์อะไรดี")
    assert res["intent"] == "size_recommendation"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert res["flex_payload"]["type"] == "bubble"


def test_intent_typo_resilience_polo(router):
    res = router.route_query("เสิ้อยืดโปโลสีดำใส่ทำงานมีมั้ย")
    assert res["intent"] == "product_search"
    assert "reply_text" in res and res["reply_text"]
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0
