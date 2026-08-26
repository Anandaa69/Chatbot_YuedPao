"""
Product, Variant, and Coupon Data Models for YuedPao Chatbot
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Product:
    product_id: int
    name: str
    category: str
    fabric: str
    style: str
    price: int
    description: str = ""
    image_url: str = ""
    colors: List[str] = field(default_factory=list)


@dataclass
class Coupon:
    coupon_code: str
    discount_title: str
    min_spend: int = 0
    valid_duration: str = ""
    detailed_condition: str = ""
