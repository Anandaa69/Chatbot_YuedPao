"""
Rich Menu Configuration & Postback Action Mappings for YuedPao Chatbot
Defines Rich Menu Grid actions mapped to Chatbot Intents.
"""
from typing import Dict, Any

RICH_MENU_ACTIONS = {
    "action_search": "ค้นหาเสื้อยืด",
    "action_promotion": "มีโปรโมชันคูปองอะไรบ้าง",
    "action_random": "สุ่มแนะนำสินค้า",
    "action_fabric": "เปรียบเทียบคุณสมบัติผ้า",
    "action_size": "ขอตารางไซส์หน่อย",
    "action_contact": "ติดต่อแอดมิน"
}


def get_rich_menu_postback_query(postback_data: str) -> str:
    """Map Rich Menu postback data string to inquiry text for TieredRouter."""
    return RICH_MENU_ACTIONS.get(postback_data, postback_data)
