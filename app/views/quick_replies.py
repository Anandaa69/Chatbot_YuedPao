"""
LINE Quick Reply Pills Generator for YuedPao Chatbot
Generates interactive Quick Reply buttons for user navigation.
"""
from typing import Dict, Any, List


def build_quick_reply_items(intent: str = "", has_more: bool = False, next_offset: int = 5) -> Dict[str, Any]:
    """
    Build LINE Quick Reply JSON payload with context-aware buttons.
    """
    items = []
    if has_more:
        items.append({
            "type": "action",
            "action": {
                "type": "message",
                "label": f"⏩ ดูเพิ่มเติม ({next_offset+1}-{next_offset+5})",
                "text": "ขอดูเพิ่มเติมหน่อย"
            }
        })

    items.extend([
        {
            "type": "action",
            "action": {
                "type": "message",
                "label": "สุ่มแนะนำสินค้า",
                "text": "สุ่มแนะนำสินค้า"
            }
        },
        {
            "type": "action",
            "action": {
                "type": "message",
                "label": "ดูคูปองส่วนลด",
                "text": "มีโปรโมชันคูปองอะไรบ้าง"
            }
        },
        {
            "type": "action",
            "action": {
                "type": "message",
                "label": "เปรียบเทียบผ้า",
                "text": "เปรียบเทียบคุณสมบัติผ้า"
            }
        },
        {
            "type": "action",
            "action": {
                "type": "message",
                "label": "ดูตารางไซส์",
                "text": "ขอตารางไซส์หน่อย"
            }
        }
    ])

    # Re-order based on current intent if needed
    if intent in ("coupon_ticket", "promotion_deal", "promotion_discount"):
        # Put random product recommendation upfront
        if not has_more:
            items[0], items[1] = items[1], items[0]
    elif intent == "fabric_comparison":
        if not has_more:
            items[0], items[2] = items[2], items[0]

    # Limit LINE quick reply items to 13
    items = items[:5]

    return {
        "items": items
    }
