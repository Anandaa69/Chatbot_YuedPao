"""
Tests for Data Models & DB Schemas
"""
from app.models.product import Product, Coupon
from app.models.session import UserSession


def test_product_model():
    p = Product(
        product_id=1,
        name="Classic Cotton Oversize",
        category="Oversize",
        fabric="Classic Cotton",
        style="Oversize",
        price=290,
        colors=["Cream", "Black"]
    )
    assert p.product_id == 1
    assert p.price == 290
    assert "Cream" in p.colors


def test_coupon_model():
    c = Coupon(
        coupon_code="NEWMEMBER5",
        discount_title="ส่วนลด 5%",
        min_spend=200
    )
    assert c.coupon_code == "NEWMEMBER5"
    assert c.min_spend == 200


def test_user_session_model():
    session = UserSession(user_id="user_123")
    for i in range(15):
        session.add_shown_product(i)
    assert len(session.shown_product_ids) == 10
    assert 0 not in session.shown_product_ids
    assert 14 in session.shown_product_ids
