"""
4-Tier Hierarchical Router Service Engine for YuedPao Chatbot
Dispatches user inquiries based on Intent Classification output to appropriate Services and Views.
"""

import sqlite3
import os
from typing import Dict, Any, List, Optional
from app.services.intent_service import IntentService
from app.services.product_service import ProductService
from app.services.promotion_service import PromotionService
from app.views.flex_carousel import build_product_flex_carousel, build_coupon_flex_carousel
from app.views.flex_fabric import build_fabric_comparison_flex, build_size_recommendation_flex
from app.views.quick_replies import build_quick_reply_items


class TieredRouter:
    def __init__(self, data_dir: Optional[str] = None):
        self.intent_service = IntentService(data_dir=data_dir)
        self.product_service = ProductService.get_instance()
        self.promotion_service = PromotionService.get_instance()

    def get_coupons_from_db(self) -> List[Dict[str, Any]]:
        """Fetch active coupons from SQLite 'coupons' table."""
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "yuedpao_chatbot.db")
        if not os.path.exists(db_path):
            return []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT coupon_code, discount_title, min_spend, valid_duration, detailed_condition FROM coupons LIMIT 5")
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"⚠️ Error querying coupons table: {e}")
            return []

    def route_query(self, raw_query: str) -> Dict[str, Any]:
        """
        Route user inquiry to appropriate service and build response payload.
        """
        # 1. Predict Intent via 4-Tier Intent Classifier
        predict_res = self.intent_service.predict_intent(raw_query)
        intent = predict_res["intent"]
        tier_used = predict_res["tier_used"]
        corrected_query = predict_res.get("corrected_query", raw_query)

        reply_text = ""
        flex_payload = None
        
        # 2. Dispatch based on Intent
        if intent == "product_search":
            products = self.product_service.search_products(raw_query, top_k=5)
            if products:
                reply_text = f"✨ พบสินค้าเสื้อยืดแบรนด์ยืดเปล่า {len(products)} รายการที่ตรงกับความต้องการของคุณครับ:"
                flex_payload = build_product_flex_carousel(products)
            else:
                reply_text = "ขออภัยครับ ไม่พบสินค้าตรงกับเงื่อนไข ลองปรับงบประมาณหรือค้นหาด้วยสีอื่นดูนะครับ"
                
        elif intent == "coupon_ticket":
            coupons = self.promotion_service.get_all_coupons() or self.get_coupons_from_db()
            if coupons:
                reply_text = "🏷️ รวมคูปองส่วนลดและโค้ดส่วนลดพิเศษล่าสุดจาก YuedPao สามารถกดปุ่มคัดลอกโค้ดไปใช้ได้เลยครับ:"
                flex_payload = build_coupon_flex_carousel(coupons)
            else:
                reply_text = "ขณะนี้ยังไม่มีคูปองส่วนลดเพิ่มเติม ลองติดตามกิจกรรมใหม่ๆ บนหน้าเว็บ YuedPao ได้เลยครับ"

        elif intent == "promotion_deal" or intent == "promotion_discount":
            q_lower = raw_query.lower()
            corr_lower = corrected_query.lower()
            
            # Direct Rule-Based Query Routing
            if any(k in q_lower or k in corr_lower for k in ["ประจำวัน", "วันนี้", "แฟลชเซล", "flash sale"]):
                promos = self.promotion_service.get_daily_deals(limit=10)
                deal_title_str = "⚡ รวมสินค้าแฟลชเซลประจำวัน"
            elif any(k in q_lower or k in corr_lower for k in ["ประจำเดือน", "เดือนนี้"]):
                promos = self.promotion_service.get_monthly_deals(limit=10)
                deal_title_str = "📅 รวมดีลพิเศษประจำเดือนนี้"
            else:
                # Combined active deals
                promos = self.promotion_service.get_daily_deals(limit=5) + self.promotion_service.get_monthly_deals(limit=5)
                deal_title_str = "🏷️ รวมโปรโมชันและดีลพิเศษล่าสุด"

            if promos:
                for p in promos:
                    if "deal_price" in p and "price" not in p:
                        p["price"] = p["deal_price"]
                reply_text = f"{deal_title_str} ({len(promos)} รายการ) จาก YuedPao ครับ:"
                flex_payload = build_product_flex_carousel(promos)
            else:
                reply_text = "ขณะนี้ยังไม่มีโปรโมชันส่วนลดเพิ่มเติม ลองติดตามกิจกรรมใหม่ๆ บนหน้าเว็บ YuedPao ได้เลยครับ"

        elif intent == "random_recommendation":
            products = self.product_service.get_fair_top5_recommendations()
            reply_text = "🎲 สุ่มแนะนำเสื้อยืด 5 หมวดฮิต ยืดเปล่า สไตล์เด่นประจำสัปดาห์ครับ:"
            flex_payload = build_product_flex_carousel(products)

        elif intent == "fabric_comparison":
            reply_text = "👕 สรุปข้อมูลนวัตกรรมเนื้อผ้า ยืดเปล่า ทั้ง 4 แบบสำหรับการใช้งานครับ:"
            flex_payload = build_fabric_comparison_flex()

        elif intent == "size_recommendation":
            reply_text = "📏 ตารางไซส์มาตรฐานยืดเปล่า และคำแนะนำการเลือกขนาดเสื้อครับ:"
            flex_payload = build_size_recommendation_flex()

        else: # Default fallback
            products = self.product_service.get_fair_top5_recommendations()
            reply_text = "ยินดีต้อนรับสู่ YuedPao Chatbot! สามารถเลือกเมนูด้านล่างหรือสอบถามสินค้าได้เลยครับ:"
            flex_payload = build_product_flex_carousel(products)

        # 3. Build Quick Reply options
        quick_replies = build_quick_reply_items(intent)

        # Collect display items for debug log
        rendered_items = []
        if intent == "coupon_ticket" and 'coupons' in locals() and coupons:
            rendered_items = [f"Code: {c.get('coupon_code', 'N/A')} | Title: {c.get('discount_title', 'N/A')}" for c in coupons]
        elif intent in ["promotion_deal", "promotion_discount"] and 'promos' in locals() and promos:
            rendered_items = [f"Product: {p.get('name', 'N/A')} | Price: ฿{p.get('price', 0)} | Deal: {p.get('deal_title', 'N/A')}" for p in promos]
        elif 'products' in locals() and products:
            rendered_items = [f"Product: {p.get('name', 'N/A')} | Price: ฿{p.get('price', 0)}" for p in products]

        card_count = len(flex_payload.get("contents", [])) if flex_payload and isinstance(flex_payload, dict) and "contents" in flex_payload else 0
        print(f"🚀 [Tiered Router] Intent: '{intent}' ({tier_used}) ──► Flex Cards: {card_count} | QuickReplies: {len(quick_replies.get('items', [])) if quick_replies else 0}")
        if rendered_items:
            print("   📦 [Items Rendered to User]:")
            for idx, item_str in enumerate(rendered_items[:6], 1):
                print(f"      {idx}. {item_str}")

        return {
            "intent": intent,
            "tier_used": tier_used,
            "corrected_query": corrected_query,
            "reply_text": reply_text,
            "flex_payload": flex_payload,
            "quick_replies": quick_replies
        }
