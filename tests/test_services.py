"""
Tests for Services (TieredRouter, IntentService, ProductService, PromotionService)
"""
from app.services.tiered_router import TieredRouter


def test_tiered_router_product_search():
    router = TieredRouter()
    res = router.route_query("อยากได้เสื้อยืดสีครีมผ้านุ่มๆ ไม่เกิน 400")
    assert res["intent"] == "product_search"
    assert "reply_text" in res
    assert res["flex_payload"] is not None
    assert "quick_replies" in res


def test_tiered_router_coupon_ticket():
    router = TieredRouter()
    res = router.route_query("มีคูปองส่วนลดอะไรบ้าง")
    assert res["intent"] == "coupon_ticket"
    assert "reply_text" in res
    assert res["flex_payload"] is not None


def test_tiered_router_promotion_deal():
    router = TieredRouter()
    res = router.route_query("แฟลชเซลประจำวันมีตัวไหนลดบ้าง")
    assert res["intent"] == "promotion_deal"
    assert "reply_text" in res
    assert res["flex_payload"] is not None


def test_tiered_router_random_recommendation():
    router = TieredRouter()
    res = router.route_query("สุ่มแนะนำสินค้า")
    assert "reply_text" in res
    assert res["flex_payload"] is not None


def test_tiered_router_fabric_comparison():
    router = TieredRouter()
    res = router.route_query("ผ้า ultrasoft กับ tailor cool ต่างกันยังไง")
    assert res["intent"] == "fabric_comparison"
    assert "reply_text" in res
    assert res["flex_payload"] is not None


def test_tiered_router_size_recommendation():
    router = TieredRouter()
    res = router.route_query("สูง 175 หนัก 70 ใส่ไซส์อะไรดี")
    assert res["intent"] == "size_recommendation"
    assert "reply_text" in res
    assert res["flex_payload"] is not None
