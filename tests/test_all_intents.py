"""
Comprehensive Automated Test Suite for all YuedPao Chatbot Intents
Tests TieredRouter, IntentService, ProductService, PromotionService, and LINE Flex Views.
"""

import re
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


def test_intent_product_search_red_color_female(router):
    res = router.route_query("ขอดูเสื้อผู้หญิงน่ารักๆ ราคาต่ำกว่า 300 สีแดง")
    assert res["intent"] == "product_search"
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0
    # Verify top card is female cute item and has Red/maroon/rosewood in body/title
    first_card_text = str(res["flex_payload"]["contents"][0]).lower()
    assert any(term in first_card_text for term in ["red", "แดง", "maroon", "rosewood", "rose", "ชาไทย"])


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


def test_intent_see_more_products_pagination(router):
    # Step 1: Initial Product Search for user_test_1
    res1 = router.route_query("อยากได้เสื้อยืดสีดำ", user_id="user_test_1")
    assert res1["intent"] == "product_search"
    assert res1["flex_payload"] is not None
    assert len(res1["flex_payload"]["contents"]) == 5
    # Verify Quick Reply has see_more pill
    qr_labels = [item["action"]["label"] for item in res1["quick_replies"]["items"]]
    assert any("ดูเพิ่มเติม" in label for label in qr_labels)

def test_intent_kids_boy_tshirt_filtering(router):
    res = router.route_query("ขอดูเสื้อเด็กชาย ราคาต่ำกว่า 300")
    assert res["intent"] == "product_search"
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0
    # Ensure NO boxers (UNWEAR) appear in top 5 for kids shirt query
    for card in res["flex_payload"]["contents"]:
        body_text = str(card.get("body", {}))
        assert "Unwear" not in body_text and "Briefs" not in body_text


def test_intent_min_price_boundary_filtering(router):
    res = router.route_query("สินค้าที่ราคามากกว่า 500 ที่ขายดีสุด")
    assert res["intent"] == "product_search"
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0
    # Ensure ALL returned items are >= 500
    for card in res["flex_payload"]["contents"]:
        body_text = str(card.get("body", {}))
        # Extract price number from flex card body text
        match = re.search(r'(\d+(?:\.\d+)?)\s*บาท', body_text)
        if match:
            price_val = float(match.group(1))
            assert price_val >= 500


def test_intent_running_shirt_filtering(router):
    res = router.route_query("อยากได้เสื้อใส่วิ่ง")
    assert res["intent"] == "product_search"
    assert res["flex_payload"] is not None
    assert len(res["flex_payload"]["contents"]) > 0
    # Ensure NO running caps or running shorts appear when searching for running SHIRTS
    for card in res["flex_payload"]["contents"]:
        body_text = str(card.get("body", {})).lower()
        assert "หมวก" not in body_text and " cap" not in body_text and "กางเกง" not in body_text and "short" not in body_text


def test_intent_search_help(router):
    res = router.route_query("วิธีการค้นหา")
    assert res["intent"] == "search_help"
    assert "วิธีค้นหาสินค้า YuedPao" in res["reply_text"]
    assert "1️⃣ ชนิดสินค้า & ทรง" in res["reply_text"]
