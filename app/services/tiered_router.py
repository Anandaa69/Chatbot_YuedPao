"""
4-Tier Hierarchical Router Service Engine for YuedPao Chatbot
Dispatches user inquiries based on Intent Classification output to appropriate Services and Views.
"""

import sqlite3
import os
import re
import random
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
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

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

    def route_query(self, raw_query: str, user_id: str = "default_user", session_history: Optional[List[str]] = None, override_offset: Optional[int] = None) -> Dict[str, Any]:
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
        has_more = False
        next_offset_val = 5

        if intent == "greeting":
            greetings = [
                "สวัสดีครับ! 👋 ยินดีต้อนรับสู่ YuedPao Chatbot",
                "หวัดดีครับ! 😊 ยินดีให้บริการที่ YuedPao",
                "สวัสดีครับ! 🙌 ยินดีต้อนรับสู่ร้าน YuedPao",
            ]
            reply_text = (
                f"{random.choice(greetings)}\n\n"
                "🛍️ ฉันช่วยคุณได้เรื่องอะไรบ้าง:\n"
                "1️⃣ ค้นหาสินค้า – พิมพ์ว่า 'เสื้อยืดผู้หญิงสีดำ ไม่เกิน 300'\n"
                "2️⃣ แนะนำไซส์ – บอกส่วนสูง/น้ำหนัก/รอบอก เช่น 'สูง 165 หนัก 55'\n"
                "3️⃣ เปรียบเทียบผ้า – พิมพ์ว่า 'ผ้า Ultrasoft ต่างกับ Tailor Cool ยังไง'\n"
                "4️⃣ คูปองส่วนลด – พิมพ์ว่า 'มีโค้ดส่วนลดไหม'\n"
                "5️⃣ โปรโมชัน – พิมพ์ว่า 'ดีลวันนี้มีอะไรบ้าง'\n\n"
                "💬 ลองพิมพ์มาได้เลยครับ!"
            )

        elif intent == "product_search":
            search_res = self.product_service.search_products(raw_query, top_k=5, offset=0, return_dict=True, corrected_query=corrected_query)
            products = search_res["products"]
            fallback_msg = search_res.get("fallback_message")
            has_more = search_res.get("has_more", False) and 5 < 20
            next_offset_val = 5
            
            # Store search context in user session
            self.user_sessions[user_id] = {
                "last_query": raw_query,
                "offset": 0
            }

            if products:
                if fallback_msg:
                    reply_text = fallback_msg
                else:
                    reply_text = f"พบสินค้าแบรนด์ยืดเปล่า {search_res.get('total_count', len(products))} รายการที่ตรงกับความต้องการของคุณ (อันดับ 1–{len(products)}) ครับ:"
                flex_payload = build_product_flex_carousel(products)
            else:
                unsupported_keywords = ["รองเท้า", "นาฬิกา", "น้ำหอม", "แว่นตา", "เข็มขัด", "แหวน", "สร้อย", "ลิป", "กระเป๋าตังค์", "สเก็ตบอร์ด", "หูฟัง", "ตู้เย็น", "แก้วน้ำ", "หมอน", "เคสโทรศัพท์", "โน๊ตบุ๊ค"]
                q_low = raw_query.lower()
                found_unsupported = [kw for kw in unsupported_keywords if kw in q_low]
                if not found_unsupported and re.search(r'(?<!สี)ครีม', q_low):
                    found_unsupported = ["ครีม"]
                if found_unsupported:
                    item_name = found_unsupported[0]
                    reply_text = f"ขออภัยด้วยนะครับ สินค้าประเภท '{item_name}' ปัจจุบันแบรนด์ YuedPao ยังไม่มีจำหน่ายครับ 😅 สามารถลองดูสินค้าประเภท เสื้อยืด เสื้อโปโล กางเกง หมวก หรือกระเป๋าสะพาย ของยืดเปล่าแทนได้เลยนะครับ 🛍️"
                else:
                    reply_text = "ขออภัยครับ สินค้ากลุ่มนี้ในระบบ YuedPao ยังไม่มีจำหน่ายครับ 😅 ลองค้นหาด้วยประเภทสินค้า เช่น เสื้อยืด โปโล กางเกง หมวก หรือกระเป๋า ดูแทนได้เลยนะครับ 🛍️"

        elif intent == "see_more_products":
            user_sess = self.user_sessions.get(user_id, {})
            last_query = user_sess.get("last_query")
            
            if not last_query:
                products = self.product_service.get_fair_top5_recommendations(session_history=session_history)
                reply_text = "สุ่มแนะนำสินค้าฮิต ยืดเปล่า ประจำสัปดาห์ครับ:"
                flex_payload = build_product_flex_carousel(products)
                has_more = False
            else:
                current_offset = override_offset if override_offset is not None else user_sess.get("offset", 0)
                next_offset_target = current_offset + 5
                
                if next_offset_target >= 20:
                    reply_text = "แสดงสินค้าตรงตามเงื่อนไขครบ 20 รายการแล้วครับ สามารถลองปรับงบประมาณหรือค้นหาด้วยสีอื่นเพิ่มเติมได้เลยครับ"
                    products = []
                    flex_payload = None
                    has_more = False
                else:
                    search_res = self.product_service.search_products(last_query, top_k=5, offset=next_offset_target, return_dict=True, corrected_query=corrected_query)
                    products = search_res["products"]
                    has_more = search_res.get("has_more", False) and (next_offset_target + 5 < 20)
                    next_offset_val = next_offset_target + 5
                    
                    if products:
                        user_sess["offset"] = next_offset_target
                        reply_text = f"แสดงผลการค้นหาเพิ่มเติมของ '{last_query}' (อันดับที่ {next_offset_target+1}–{next_offset_target+len(products)}) ครับ:"
                        flex_payload = build_product_flex_carousel(products)
                    else:
                        reply_text = f"แสดงสินค้าตรงตามเงื่อนไขของ '{last_query}' ครบทั้งหมดเรียบร้อยแล้วครับ"
                        has_more = False

        elif intent == "coupon_ticket":
            coupons = self.promotion_service.get_all_coupons() or self.get_coupons_from_db()
            if coupons:
                reply_text = "รวมคูปองส่วนลดและโค้ดส่วนลดพิเศษล่าสุดจาก YuedPao สามารถกดปุ่มคัดลอกโค้ดไปใช้ได้เลยครับ:"
                flex_payload = build_coupon_flex_carousel(coupons)
            else:
                reply_text = "ขณะนี้ยังไม่มีคูปองส่วนลดเพิ่มเติม ลองติดตามกิจกรรมใหม่ๆ บนหน้าเว็บ YuedPao ได้เลยครับ"

        elif intent == "promotion_deal" or intent == "promotion_discount":
            q_lower = raw_query.lower()
            corr_lower = corrected_query.lower()
            
            # Direct Rule-Based Query Routing
            if any(k in q_lower or k in corr_lower for k in ["ประจำวัน", "วันนี้", "แฟลชเซล", "flash sale"]):
                promos = self.promotion_service.get_daily_deals(limit=10)
                deal_title_str = "รวมสินค้าแฟลชเซลประจำวัน"
            elif any(k in q_lower or k in corr_lower for k in ["ประจำเดือน", "เดือนนี้"]):
                promos = self.promotion_service.get_monthly_deals(limit=10)
                deal_title_str = "รวมดีลพิเศษประจำเดือนนี้"
            else:
                # Combined active deals
                promos = self.promotion_service.get_daily_deals(limit=5) + self.promotion_service.get_monthly_deals(limit=5)
                deal_title_str = "รวมโปรโมชันและดีลพิเศษล่าสุด"

            if promos:
                for p in promos:
                    if "deal_price" in p and "price" not in p:
                        p["price"] = p["deal_price"]
                reply_text = f"{deal_title_str} ({len(promos)} รายการ) จาก YuedPao ครับ:"
                flex_payload = build_product_flex_carousel(promos)
            else:
                reply_text = "ขณะนี้ยังไม่มีโปรโมชันส่วนลดเพิ่มเติม ลองติดตามกิจกรรมใหม่ๆ บนหน้าเว็บ YuedPao ได้เลยครับ"

        elif intent == "random_recommendation":
            products = self.product_service.get_fair_top5_recommendations(session_history=session_history)
            reply_text = "สุ่มแนะนำเสื้อยืด 5 หมวดฮิต ยืดเปล่า สไตล์เด่นประจำสัปดาห์ครับ:"
            flex_payload = build_product_flex_carousel(products)

        elif intent == "fabric_comparison":
            reply_text = "สรุปข้อมูลนวัตกรรมเนื้อผ้า ยืดเปล่า ทั้ง 4 แบบสำหรับการใช้งานครับ:"
            flex_payload = build_fabric_comparison_flex()

        elif intent == "size_recommendation":
            reply_text = "ตารางไซส์มาตรฐานยืดเปล่า และคำแนะนำการเลือกขนาดเสื้อครับ:"
            flex_payload = build_size_recommendation_flex()

        elif intent == "search_help":
            reply_text = (
                "💡 วิธีค้นหาสินค้า YuedPao (พิมพ์ตามสไตล์คุณได้เลยครับ):\n\n"
                "1️⃣ ชนิดสินค้า & ทรง: \"เสื้อยืดคอกลม\", \"โปโล\", \"Oversize\", \"กางเกงยีนส์\", \"กระเป๋า\"\n"
                "2️⃣ งบ & ราคา: \"ไม่เกิน 300\", \"ราคามากกว่า 500\", \"งบ 500\"\n"
                "3️⃣ เพศ & ช่วงวัย: \"เสื้อผู้หญิง\", \"เสื้อผู้ชาย\", \"เสื้อเด็กชาย\"\n"
                "4️⃣ สี & สไตล์: \"สีชาไทย\", \"สีแดง\", \"เสื้อใส่วิ่ง\", \"ผ้านุ่มไม่ต้องรีด\"\n"
                "5️⃣ ตัวฮิต & แนะนำ: \"ขอสินค้าขายดี\", \"สุ่มแนะนำ\"\n\n"
                "ลองพิมพ์ประโยคค้นหาเข้ามาได้เลยครับ! 🛍️"
            )

        else: # Default fallback
            products = self.product_service.get_fair_top5_recommendations(session_history=session_history)
            reply_text = "ยินดีต้อนรับสู่ YuedPao Chatbot! สามารถเลือกเมนูด้านล่างหรือสอบถามสินค้าได้เลยครับ:"
            flex_payload = build_product_flex_carousel(products)

        # 3. Build Quick Reply options with pagination support
        quick_replies = build_quick_reply_items(intent, has_more=has_more, next_offset=next_offset_val)

        # Collect display items for debug log
        rendered_items = []
        if intent == "coupon_ticket" and 'coupons' in locals() and coupons:
            rendered_items = [f"Code: {c.get('coupon_code', 'N/A')} | Title: {c.get('discount_title', 'N/A')}" for c in coupons]
        elif intent in ["promotion_deal", "promotion_discount"] and 'promos' in locals() and promos:
            rendered_items = [f"Product: {p.get('name', 'N/A')} | Price: ฿{p.get('price', 0)} | Deal: {p.get('deal_title', 'N/A')}" for p in promos]
        elif 'products' in locals() and products:
            rendered_items = [f"Product: {p.get('name', 'N/A')} | Cat: {p.get('category', 'N/A')} | Gender: {p.get('gender', 'unisex')} | Price: ฿{p.get('price', 0)}" for p in products]

        card_count = len(flex_payload.get("contents", [])) if flex_payload and isinstance(flex_payload, dict) and "contents" in flex_payload else 0
        print(f"🚀 [Tiered Router] User: '{user_id}' | Intent: '{intent}' ({tier_used}) ──► Flex Cards: {card_count} | HasMore: {has_more} | QuickReplies: {len(quick_replies.get('items', [])) if quick_replies else 0}")
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
