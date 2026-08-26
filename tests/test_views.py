"""
Tests for Views (LINE Flex Message Carousel JSON & Quick Replies)
"""
from app.views.flex_carousel import build_product_flex_carousel, build_coupon_flex_carousel
from app.views.flex_fabric import build_fabric_comparison_flex, build_size_recommendation_flex
from app.views.quick_replies import build_quick_reply_items


def test_build_product_flex_carousel():
    products = [
        {
            "name": "Classic Cotton Oversize",
            "category": "Oversize",
            "price": 290,
            "colors": ["Cream", "Black"],
            "image_url": "https://example.com/img.jpg"
        }
    ]
    flex = build_product_flex_carousel(products)
    assert flex["type"] == "carousel"
    assert len(flex["contents"]) == 1
    assert flex["contents"][0]["hero"]["aspectRatio"] == "1:1"
    assert flex["contents"][0]["body"]["contents"][1]["maxLines"] == 2


def test_build_coupon_flex_carousel():
    coupons = [
        {
            "coupon_code": "NEWMEMBER5",
            "discount_title": "ส่วนลด 5%",
            "min_spend": 200,
            "valid_duration": "31 ธ.ค. 2033",
            "detailed_condition": "เมื่อซื้อครบ 200 บาทขึ้นไป"
        }
    ]
    flex = build_coupon_flex_carousel(coupons)
    assert flex["type"] == "carousel"
    assert len(flex["contents"]) == 1
    # Check clipboard copy action button
    footer_button = flex["contents"][0]["footer"]["contents"][0]
    assert footer_button["action"]["type"] == "clipboard"
    assert footer_button["action"]["clipboardText"] == "NEWMEMBER5"


def test_build_fabric_comparison_flex():
    flex = build_fabric_comparison_flex()
    assert flex["type"] == "bubble"
    assert "คู่มือเปรียบเทียบเนื้อผ้า YuedPao" in flex["body"]["contents"][0]["text"]


def test_build_size_recommendation_flex():
    flex = build_size_recommendation_flex()
    assert flex["type"] == "bubble"
    assert "ตารางไซส์มาตรฐาน YuedPao" in flex["body"]["contents"][0]["text"]


def test_build_quick_reply_items():
    qr = build_quick_reply_items("product_search")
    assert "items" in qr
    assert len(qr["items"]) == 4
