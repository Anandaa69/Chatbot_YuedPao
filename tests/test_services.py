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


def test_product_service_is_available_filtering():
    from app.services.product_service import ProductService
    ps = ProductService.get_instance()
    assert len(ps.products) > 0
    for prod in ps.products:
        assert prod.get("is_available", 1) == 1


def test_product_service_style_vibe_matching():
    from app.services.product_service import ProductService
    ps = ProductService.get_instance()

    # 1. Test 'น่ารัก' query returns female/crop/babytee items
    res_cute = ps.search_products("ขอดูเสื้อน่ารักๆ หน่อย", top_k=5)
    assert len(res_cute) > 0
    for item in res_cute:
        assert item.get("gender") in ["female", "unisex"]

    # 2. Test 'เท่ๆ' query returns oversize/street items
    res_cool = ps.search_products("ขอเสื้อยืดเท่ๆ สตรีทๆ", top_k=5)
    assert len(res_cool) > 0

    # 3. Test 'เรียบหรู' query returns polo/shirt items
    res_chic = ps.search_products("ขอเสื้อยืดเรียบหรูดูดีใส่ทำงาน", top_k=5)
    assert len(res_chic) > 0


