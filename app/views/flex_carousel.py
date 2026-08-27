"""
Flex Message Carousel Builder for YuedPao Chatbot
Generates LINE Flex Message Carousel cards for Top 5 Products and Coupon Tickets.
"""
from typing import List, Dict, Any


def build_product_flex_carousel(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build LINE Flex Message Carousel JSON for Top 5 Product recommendations.
    Enforces LINE UI Standards: aspectRatio 1:1, maxLines 2.
    """
    bubbles = []
    
    for item in products[:5]:
        name = item.get("name", "เสื้อยืด YuedPao")
        category = item.get("category", "General")
        price = item.get("price", 0)
        original_price = item.get("original_price")
        colors = item.get("colors", [])
        image_url = item.get("image_url") or "https://mp-static.yuedpao.com/images/logo.png"
        if image_url.endswith(".svg") or "free-delivery" in image_url:
            image_url = "https://mp-static.yuedpao.com/images/logo.png"
        product_url = item.get("product_url") or "https://yuedpao.com"
        color_str = ", ".join(colors[:3]) if isinstance(colors, list) else str(colors)
        
        try:
            val = float(str(price).replace("..", "."))
            if val.is_integer():
                price_text = f"{int(val):,} บาท"
            else:
                price_text = f"{round(val, 1):,} บาท"
        except Exception:
            price_text = "สอบถามราคา"
        
        contents = [
            # Category Badge
            {
                "type": "text",
                "text": f"{category.upper()}",
                "weight": "bold",
                "color": "#e63946",
                "size": "xs"
            },
            # Product Name
            {
                "type": "text",
                "text": name,
                "weight": "bold",
                "size": "md",
                "margin": "xs",
                "maxLines": 2,
                "wrap": True
            },
            # Color Information
            {
                "type": "text",
                "text": f"สี: {color_str}" if color_str else "หลากหลายสี",
                "size": "xs",
                "color": "#666666",
                "margin": "xs"
            },
            # Price Section
            {
                "type": "box",
                "layout": "baseline",
                "margin": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": price_text,
                        "weight": "bold",
                        "size": "lg",
                        "color": "#1d3557",
                        "flex": 0
                    }
                ]
            }
        ]
        
        # Optional Original Price strike-through
        if original_price and original_price > price:
            contents[-1]["contents"].append({
                "type": "text",
                "text": f"{original_price:,}฿",
                "size": "xs",
                "color": "#999999",
                "decoration": "line-through",
                "margin": "sm",
                "flex": 0
            })

        bubble = {
            "type": "bubble",
            "size": "micro",
            "hero": {
                "type": "image",
                "url": image_url,
                "size": "full",
                "aspectRatio": "1:1",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "12px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูรายละเอียด",
                            "uri": product_url
                        },
                        "style": "primary",
                        "color": "#e63946",
                        "height": "sm"
                    }
                ],
                "paddingAll": "8px"
            }
        }
        bubbles.append(bubble)
        
    # Append 6th 'Show More' Bubble Card if total items exceed 5
    if len(products) > 5:
        remaining_count = len(products) - 5
        more_bubble = {
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ดูเพิ่มเติม",
                        "weight": "bold",
                        "size": "md",
                        "color": "#e63946",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": f"ยังมีดีลน่าสนใจอีก {remaining_count} รายการ",
                        "size": "xs",
                        "color": "#666666",
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    }
                ],
                "paddingAll": "16px",
                "justifyContent": "center"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูทั้งหมดบนเว็บ",
                            "uri": "https://www.yuedpao.com"
                        },
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "paddingAll": "8px"
            }
        }
        bubbles.append(more_bubble)

    return {
        "type": "carousel",
        "contents": bubbles
    }


def build_coupon_flex_carousel(coupons: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build LINE Flex Message Carousel JSON for Coupon Tickets.
    Includes 'คัดลอกโค้ด' (Clipboard Action button).
    """
    bubbles = []
    
    for item in coupons[:5]:
        code = item.get("coupon_code", "YUEDPAO")
        title = item.get("discount_title", "ส่วนลดพิเศษ YuedPao")
        min_spend = item.get("min_spend", 0)
        duration = item.get("valid_duration", "ระยะเวลาตามเงื่อนไข")
        condition = item.get("detailed_condition", "เงื่อนไขเป็นไปตามที่บริษัทกำหนด")
        
        min_spend_str = f"เมื่อซื้อครบ {min_spend:,} บาท" if min_spend > 0 else "ไม่มีขั้นต่ำ"
        
        bubble = {
            "type": "bubble",
            "size": "micro",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "คูปองส่วนลดพิเศษ",
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xs"
                    },
                    {
                        "type": "text",
                        "text": code,
                        "weight": "bold",
                        "color": "#ffffff",
                        "size": "xl",
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#e63946",
                "paddingAll": "12px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "sm",
                        "maxLines": 2,
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": f"{min_spend_str}",
                        "size": "xs",
                        "color": "#457b9d",
                        "margin": "xs"
                    },
                    {
                        "type": "text",
                        "text": f"{duration}",
                        "size": "xs",
                        "color": "#666666",
                        "margin": "xs",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": f"{condition}",
                        "size": "xs",
                        "color": "#999999",
                        "margin": "xs",
                        "maxLines": 2,
                        "wrap": True
                    }
                ],
                "paddingAll": "10px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "clipboard",
                            "label": "คัดลอกโค้ด",
                            "clipboardText": code
                        },
                        "style": "secondary",
                        "height": "sm"
                    }
                ],
                "paddingAll": "8px"
            }
        }
        bubbles.append(bubble)
        
    return {
        "type": "carousel",
        "contents": bubbles
    }
