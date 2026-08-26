"""
User Session & Carousel History Model for YuedPao Chatbot
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class UserSession:
    user_id: str
    shown_product_ids: List[int] = field(default_factory=list)
    last_intent: str = ""

    def add_shown_product(self, product_id: int):
        """Keep last 10 shown product IDs to prevent repetitive recommendations."""
        if product_id not in self.shown_product_ids:
            self.shown_product_ids.append(product_id)
        if len(self.shown_product_ids) > 10:
            self.shown_product_ids.pop(0)
