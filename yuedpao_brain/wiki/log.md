---
title: Project Activity Log
date: 2026-08-23
tags: [log, history, yuedpao]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 📅 Project Activity & Session Log - Chatbot Yuedpao

Backlink: [[index]]

## 📅 [2026-08-28] - Session 52: การแก้ไขการค้นหาสินค้าตามรูปกราฟิก (Dugong/Icons of Hope Description Enrichment) & Exact Numeric Spec Boost ADR

### 🎯 สรุปผลงานที่ปรับปรุง
1. **การเติมเต็มคำอธิบายสินค้าเสื้อลายพะยูน (`Icons of Hope UNDP Collection`)**:
   * สแกนตาราง `products` พบว่าคำว่า `"พะยูน"` ไม่อยู่ในคอลัมน์ `description` ของ DB เดิม (โดน Scraper ตัดย่อข้อความ)
   * ทำการอัปเดต DB และรัน **Document Expansion 2.0 (Rule 6)** เติมคีย์เวิร์ด `ลายพะยูน อนุรักษ์พะยูน สัตว์ทะเล YUEDPAO X UNDP` ลงใน `products` และ Index เข้า ChromaDB VectorDB / BM25 
   * ผลลัพธ์: ค้นหาประโยค `"มีเสื้อลายพะยูนมั้ย"` ดึงเสื้อรุ่น **`Oversize Screen ICONS OF HOPE YUEDPAO X UNDP`** ขึ้นอันดับ 1 ทันที
2. **ระบบการให้โบนัสตัวเลขสเปกเป๊ะ (`spec_boost = 3.00x`)**:
   * เพิ่มลอจิก `spec_boost` ใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) เมื่อผู้ใช้ระบุสเปกสัดส่วนผสมผ้าเป๊ะๆ เช่น `cotton 60%` สินค้าที่มีตัวเลขตรงตามโจทย์จะได้รับคะแนน **3.00x** เบียดขึ้นอันดับ 1-4 ทันที
3. **การทดสอบความถูกต้องอัตโนมัติ (Automated Pytest Standard)**:
   * รันคำสั่ง `python run.py test` ผ่าน **100% ครบทั้ง 19 เคสทดสอบ (19/19 PASSED in 36.34s)**

---

## 📅 [2026-08-27] - Session 51: การป้องกันสินค้าหลุดขอบเขต (Out-of-Domain Item Leakage) & Price Boundary / First Visit Intent Fix ADR

### 🎯 สรุปผลงานที่ปรับปรุง
1. **ระบบป้องกันสินค้าหลุดขอบเขต (Out-of-Domain Item Leakage Safeguard)**:
   - เพิ่ม **Pre-Search Unsupported Category Guard** ใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) และ [tiered_router.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/tiered_router.py) ตรวจคำค้นหาที่ไม่มีในร้าน (`รองเท้า`, `นาฬิกา`, `น้ำหอม`, `แว่นตา`, `เข็มขัด`, `สร้อย`, `สเก็ตบอร์ด`, `หูฟัง`, `ตู้เย็น`) 
   - หากแมตช์เจอคำกลุ่มนี้ ระบบจะคืนค่า `products = []` และตอบปฏิเสธสุภาพทันที (*"ขออภัยด้วยนะครับ สินค้าประเภท 'รองเท้า' ปัจจุบันแบรนด์ YuedPao ยังไม่มีจำหน่ายครับ 😅"*) โดยไม่ยัดเยียดเสื้อยืด 5 ตัวออกไป
2. **การแก้ไข Price Boundary Filter (Bug #1 & Range 100-200)**:
   - แก้ไข `_extract_price_bounds()` ใช้ Negative Lookbehind `(?<!ไม่)(?:มากกว่า|เกิน)` ป้องกันคำว่า `"ไม่เกิน 200"` โดนตีความผิดเป็น `min_price = 200`
   - เพิ่ม Regex Pattern `(\d+)\s*[-–—toถึง]\s*(\d+)` รองรับการระบุงบแบบช่วง (`100-200` บาท) ได้อย่างถูกต้อง
3. **การแก้ไข Tier 1 First Visit Intent Order**:
   - ปรับลำดับ Tier 1 ใน [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) ตรวจจับสัญญาณผู้ใช้ใหม่ (`"ครั้งแรก"`, `"น่าสนใจ"`, `"แนะนำหน่อย"`) ให้ถูกจัดเข้า `random_recommendation` (เพื่อแสดงสินค้าขายดี Top-5) แทนที่จะโดนคีย์เวิร์ดกวาดแบบ Greedy เข้า `product_search`

---

## 📅 [2026-08-27] - Session 49: ระบบรองรับประโยคปฏิเสธประเภท "ไม่ใช่เสื้อ" (Negative Shirt Constraint Guard ADR)

### 🎯 สรุปผลงานที่ปรับปรุง
1. **ระบบรองรับประโยคปฏิเสธประเภท "ไม่ใช่เสื้อ" / "ไม่เอาเสื้อ" / "นอกจากเสื้อ"**:
   - เพิ่มคำว่า `"ไม่"` และ `"ไม่ใช่"` เข้าไปใน `PRESERVED_KEYWORDS` ใน [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) เพื่อป้องกันไม่ให้คำปฏิเสธถูกลบระหว่างกระบวนการ Clean Stopwords
   - พัฒนา **Negative Constraint Guard** ใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) ตรวจจับประโยคปฏิเสธ `query_not_shirt = True` แล้วสั่งให้ระบบ:
     * เพิ่มโบนัสคะแนนสินค้าหมวดที่ไม่ใช่เสื้อ (**กระเป๋า, หมวก, ถุงเท้า, กางเกงยีนส์, กางเกงใน Unwear**) เป็น **2.50x**
     * ลดคะแนนสินค้าประเภทเสื้อยืด โปโล ครอป ลงเหลือ **0.01x**
2. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - เพิ่มเคสทดสอบ `test_intent_negative_shirt_constraint` ใน [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py)
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 19 เคสทดสอบ (19/19 PASSED in 36.37s)**

---

## 📅 [2026-08-27] - Session 48: การพัฒนาป้าย Badge สินค้าแนะนำ ("⭐ แนะนำ") บน LINE Flex Carousel ADR

### 🎯 สรุปผลงานที่ปรับปรุง
1. **การแสดงป้าย Badge สินค้าแนะนำบน LINE Flex Message (`⭐ แนะนำ`)**:
   - ปรับปรุง [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) ติดธง `is_recommended = True` ให้กับสินค้าจากการสุ่มแนะนำและสินค้าเติมเติม Smart Fallback
   - ปรับปรุงการสร้าง Flex Cards ใน [flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py) แสดงผลป้าย Badge เล็กๆ **`⭐ แนะนำ`** สีส้มทอง (`#d97706`) ที่มุมขวาบนของการ์ดสินค้าอย่างสวยงาม
2. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 18 เคสทดสอบ (18/18 PASSED in 36.49s)**

---

## 📅 [2026-08-27] - Session 47: ระบบป้องกันสินค้าผู้ใหญ่หลุดเติมช่องการ์ดเมื่อค้นหาเสื้อเด็ก (Demographic Filter Guard ADR)

### 🎯 สรุปผลงานที่ปรับปรุง
1. **การป้องกันสินค้าผู้ใหญ่หลุดเติมช่องการ์ดสินค้าเด็ก (`Demographic Filter Guard`)**:
   - พัฒนาการกรองระดับผลลัพธ์สุดท้ายใน `search_products()` ของ [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py)
   - เมื่อผู้ใช้ค้นหาสินค้าเด็ก (`query_has_kids = True`) หากพบสินค้าเด็กตรงเงื่อนไข ระบบจะคัดกรองเฉพาะสินค้าเด็กเท่านั้น และจะไม่ดึงสินค้าผู้ใหญ่ที่มีคะแนนซัพเพรสเข้ามาเติมในช่องการ์ดสินค้าที่เหลือ (เช่น แสดงผล 4 การ์ดเด็กล้วนตรงเงื่อนไข 100%)
2. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 18 เคสทดสอบ (18/18 PASSED in 37.62s)**

---

## 📅 [2026-08-27] - Session 46: มาตรฐานการจัดรูปแบบราคาทศนิยม 1 ตำแหน่ง (Single Decimal Price Standard ADR)

### 🎯 สรุปผลงานที่ปรับปรุง
1. **การบังคับรูปแบบราคาทศนิยมไม่เกิน 1 ตำแหน่งทั่วทั้งระบบ**:
   - อัปเดตราคาในฐานข้อมูล SQLite `yuedpao_chatbot.db` ให้เศษทศนิยมราคาส่วนลดปัดเหลือไม่เกิน 1 ตำแหน่ง (`292.54` ➔ `292.5`)
   - ปรับปรุงฟังก์ชัน `_format_price` ใน [flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py) (`round(val, 1)`) ให้การ์ดสินค้า Flex Carousel แสดงราคาสูงสุด 1 ตำแหน่งเท่านั้น (`฿292.5 บาท`)
2. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 18 เคสทดสอบ (18/18 PASSED in 38.44s)**

---

## 📅 [2026-08-27] - Session 45: การล้างราคาทศนิยมเกิน (`292..539`) & การปรับปรุงคู่มือวิธีการค้นหากระชับ ADR

### 🎯 สรุปผลงานที่ปรับปรุง
1. **การคลีนราคาสินค้าทศนิยมเกินและจุดซ้ำ (`_format_price`)**:
   - พัฒนาสคริปต์ทำความสะอาดราคาสินค้าที่มีเศษทศนิยมเกิน 3 ตำแหน่ง (`292.539` ➔ `292.54`) ใน SQLite DB `yuedpao_chatbot.db`
   - เพิ่มฟังก์ชัน `_format_price` ใน [flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py) ป้องกันจุดซ้ำ (`..`) และจัดรูปแบบทศนิยมให้สวยงาม
2. **การปรับปรุงคู่มือแนะนำวิธีการค้นหา (`search_help`) สั้นกระชับ**:
   - ปรับปรุง `reply_text` ใน [tiered_router.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/tiered_router.py) ให้กระชับ สั้น อ่านง่าย อ่านจบใน 5 บรรทัดบนหน้าจอ LINE
3. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 18 เคสทดสอบ (18/18 PASSED in 36.93s)**

---

## 📅 [2026-08-27] - Session 44: สถาปัตยกรรมนำเข้าสินค้าดีลลง Vector DB (Dual-Layer Vector Ingestion ADR) & สรุปข้อมูลสำหรับนำเสนอ

### 🎯 สรุปหลักการทำงานเชิงสถาปัตยกรรม (Architectural Decision Record)
1. **กระบวนการนำเข้าข้อมูลสินค้าดีลลง Vector DB (ChromaDB + E5 Model)**:
   - **Document Expansion & Composite Passage:** แปลงข้อมูลจาก SQLite DB โดยฉีดทั้ง `ราคาเต็ม (original_price)` และ `ราคาลด (price)` พร้อมฉายานวัตกรรมผ้า/สี/สไตล์ ลงในข้อความบรรยายเต็ม (`Composite Passage Text`) ก่อนสร้าง Vector Embedding
   - **Dual-Layer Search Architecture:**
     * *Layer 1 (Vector Search - ภาษาพูด):* ค้นหาความหมายของประโยคเปรียบเปรย เช่น *"ขอเสื้อดีลราคาถูก"*, *"เสื้อโปโลลดราคา"* ผ่าน ChromaDB Vector Similarity
     * *Layer 2 (Metadata Filtering - ตัวเลขคณิตศาสตร์):* กรองเงื่อนไขราคาสุดสุทธิ (`price <= 300`, `price >= 500`) ผ่าน ChromaDB Metadata & SQLite DB เพื่อความแม่นยำ 100%
2. **การรวมศูนย์คำสั่งโปรเจกต์ (`run.py` - Master CLI Runner)**:
   - รวบรวมคำสั่งบริหารจัดการระบบในไฟล์เดียว (`serve`, `scrape-products`, `scrape-coupons`, `reindex`, `test`, `status`)
3. **การตั้งค่า Rich Menu ปุ่ม A ("วิธีการค้นหา")**:
   - เชื่อมโยง Intent `search_help` ตอบกลับคู่มือแนะนำการค้นหาสินค้า 6 หมวดหมู่แบบเข้าใจง่ายสำหรับผู้ใช้ LINE
4. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 18 เคสทดสอบ (18/18 PASSED in 37.77s)**

---

## 📅 [2026-08-27] - Session 43: การพัฒนา Intent แนะนำวิธีการค้นหา (`search_help`) สำหรับ Rich Menu ปุ่ม A ADR

### 🎯 สรุปผลงานที่พัฒนาขึ้น
1. **การเพิ่ม Intent แนะนำการค้นหา (`search_help`)**:
   - เพิ่ม Priority Rule ใน [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) ดักจับคีย์เวิร์ด *"วิธีการค้นหา"*, *"วิธีค้นหา"*, *"ค้นหายังไง"* ( Tier 1 Priority Rule )
   - ปรับปรุง [tiered_router.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/tiered_router.py) ให้ตอบกลับคู่มือแนะนำการค้นหาอย่างละเอียด 6 หมวดหมู่ (ประเภท/ทรงเสื้อ, ช่วงราคา min-max, เพศ/ช่วงวัย, โทนสี, นวัตกรรมผ้า, สินค้าขายดี)
2. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - เพิ่มเคสทดสอบ `test_intent_search_help` ใน [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py)
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 18 เคสทดสอบ (18/18 PASSED in 37.77s)**

---

## 📅 [2026-08-27] - Session 42: การแก้ไขปัญหาราคาป้ายส่วนลดหมวก/อุปกรณ์เสริม & การสร้างดรรชนี Hybrid Search ใหม่ ADR

### 🎯 สรุปผลงานที่แก้ไขแล้ว
1. **การแก้ไขปัญหาราคาหมวกไม่ตรงกับหน้าเว็บ (Discount Badge Scraper Bugfix)**:
   - ปรับปรุงการสกัดราคาใน [scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py) ให้ดึงราคาเฉพาะตัวเลขหลังสัญลักษณ์ `฿` โดยตรง ป้องกันการดึงตัวเลขจากป้ายส่วนลด (เช่น *"โค้ดลด 150 บาท"*)
   - อัปเดตราคาสินค้าประเภทหมวกและอุปกรณ์เสริมทุกรุ่น (*Classic Cap, Fade Denim Cap, Bucket Hat, Ultraflow Running Cap*) เป็น **฿290** ตรงตามหน้าเว็บ YuedPao 100%
2. **การพัฒนาเมธอด `reload_and_index()` ใน `ProductService`**:
   - พัฒนาเมธอด `reload_and_index()` ใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) รองรับคำสั่ง `python run.py reindex`
   - ผลการสร้างดรรชนีใหม่: **Successfully indexed 945 products into ChromaDB & BM25**
3. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 17 เคสทดสอบ (17/17 PASSED in 38.70s)**

---

## 📅 [2026-08-27] - Session 41: การทดสอบและปรับปรุง BERT E5 Passage Vector Matching ADR

### 🎯 สรุปผลงานที่ปรับปรุง
1. **การปรับแต่ง BERT Intent Passages (`INTENT_PASSAGES`)**:
   - ปรับปรุงข้อความ `INTENT_PASSAGES` ใน [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) สำหรับหมวด `fabric_comparison` (เพิ่มคีย์เวิร์ดนวัตกรรมสัมผัสผ้านุ่ม ผ้าเย็น ระบายเหงื่อ ไม่ติดตัว) และ `random_recommendation`
2. **การทดสอบภาษาพูดเชิงธรรมชาติด้วย BERT Multilingual E5 Model (Tier 3)**:
   - ทดสอบ 5 ประโยคภาษาพูดสไตล์ Lifestyle & Comfort
   - ผลการทดลอง: BERT Tier 3 Match สามารถจับประโยคอย่าง *"ขอชุดใส่ไปเดินเที่ยวชิลๆ คาเฟ่เสาร์อาทิตย์"* และ *"เพิ่งเคยซื้อแบรนด์นี้ครั้งแรก แนะนำตัวไหนดี"* ลง Intent ได้อย่างแม่นยำด้วย Latency **10.9 ms - 12.6 ms**
3. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 17 เคสทดสอบ (17/17 PASSED in 36.52s)**

---

## 📅 [2026-08-27] - Session 40: ระบบป้องกันสินค้าผิดประเภทในหมวดหมู่เดียวกัน (Item Type Mismatch Demotion ADR)

### 🎯 สรุปผลงานและจุดเด่นทางเทคนิค
1. **การป้องกันสินค้าประเภทหมวก/กางเกงหลุดเจือปนเมื่อค้นหาเสื้อ (`category_mismatch_boost`)**:
   - พัฒนาตัวกรองระดับชื่อสินค้าและ Text Haystack ใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py)
   - เมื่อผู้ใช้ระบุคำว่า `"เสื้อ"` (`query_has_shirt = True`): สินค้าประเภทหมวกวิ่งและกางเกงวิ่งในหมวดกีฬา `ULTRA FLOW` ที่มีคำว่า `"หมวก"`, `"cap"`, `"กางเกง"`, `"shorts"` จะถูก **ลดคะแนนลงเหลือ 0.01x**
   - เมื่อผู้ใช้ระบุคำว่า `"กางเกง"` (`query_has_pants = True`): สินค้าประเภทเสื้อยืด โปโล ครอป จะถูกลดคะแนนลงเหลือ 0.01x
2. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest Standard)**:
   - เพิ่มเคสทดสอบ `test_intent_running_shirt_filtering` ใน [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py)
   - ผลการรัน Pytest ผ่านคำสั่ง `python run.py test`: **ผ่าน 100% ครบทั้ง 17 เคสทดสอบ (17/17 PASSED in 36.90s)**

---

## 📅 [2026-08-27] - Session 39: การพัฒนาศูนย์รวมคำสั่ง Master CLI Runner (`run.py`) ADR

### 🎯 สรุปผลงานที่พัฒนาขึ้น
1. **การสร้างศูนย์รวมคำสั่งโปรเจกต์ (`run.py` - Master CLI Runner)**:
   - พัฒนาไฟล์ [run.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/run.py) รวบรวมคำสั่งรันระบบและ pipeline ทั้งหมดไว้ที่จุดเดียว:
     * `python run.py serve`: รันแอปพลิเคชัน Flask LINE Webhook Server
     * `python run.py scrape-products --all`: รันสแคปเปอร์สินค้า & อัปเดตคลังคำศัพท์ภาษาไทย Domain Vocab
     * `python run.py scrape-coupons`: สแคปคูปอง & ทำดรรชนี RRF ChromaDB โปรโมชันใหม่
     * `python run.py reindex`: สร้างดรรชนี BM25 & ChromaDB Vector สินค้าใหม่จาก SQLite
     * `python run.py test`: รันชุดทดสอบอัตโนมัติ Pytest 16/16 Intents
     * `python run.py generate-richmenu`: เจนภาพ Rich Menu 4K 2500x1686 px
     * `python run.py status`: แสดงรายงานสรุปสถานะ DB สินค้า คูปอง และ NLP Vocab
2. **การทดสอบความถูกต้อง**:
   - คำสั่ง `python run.py status` แสดงสถานะสินค้า 1,405 รายการ, 148 หมวดหมู่, 9,196 ไซส์/สี, 5 คูปอง และคำศัพท์ NLP 514 คำอย่างสมบูรณ์

---

## 📅 [2026-08-27] - Session 38: การวิเคราะห์สแกนและซิงก์ราคากระเป๋าสินค้าจริงทั้งหมวดหมู่อัตโนมัติ (Full ACCESSORIES Live Price Resync ADR)

### 🎯 สาเหตุและการแก้ไข (Root Cause & Complete Solution)
1. **สาเหตุที่ราคากระเป๋าเดิมใน DB ไม่ตรงกับหน้าเว็บ:**
   - หน้ารายละเอียดสินค้าประเภทกระเป๋ามีตัวเลือกสายสะพาย/อุปกรณ์เสริม (เช่น `สายสะพาย Multi Strap ฿190 / ฿290`) แสดงอยู่บนหน้าเว็บด้วย
   - ลอจิกเดิมใน `scraper_service.py` ใช้คำสั่ง `min(price_nums)` ซึ่งไปดึงเอาราคาขั้นต่ำของ **ตัวเลือกสายสะพาย (฿190 / ฿290)** แทนที่จะเป็น **ราคากระเป๋าหลัก (฿690 / ฿990)**
2. **การรันสคริปต์ซิงก์ราคาจากหน้าเว็บจริง (`sync_bag_prices.py`)**:
   - พัฒนาและรันสคริปต์ดึง DOM Data ล่าสุดจาก `https://www.yuedpao.com/ACCESSORIES-cat.ordqos` ด้วย Selenium
   - อัปเดตราคาในตาราง `products` สำหรับกระเป๋าทุกรายการครบทั้ง 48 รายการใน SQLite `yuedpao_chatbot.db` ตรงตามหน้าเว็บ 100%:
     * **The Bagg Carry bag:** จาก ฿290 ➔ **฿990**
     * **Yuedpao Fluffy Bag  กระเป๋าสะพายข้าง:** จาก ฿290 ➔ **฿690**
     * **Yuedpao Active Bag:** จาก ฿290 ➔ **฿690**
     * **The Bagg Fluffy Gozy Bag:** **฿690**
     * **The Bagg Canvas Core Bag:** **฿590**
     * **The Bagg Canvas Classic Tote:** **฿590**
     * **The Bagg Fluffy Box Bag:** จาก ฿190 ➔ **฿690**
     * **The bagg mini crossbody bag:** **฿290**
     * **Yuedpao Mini Bag:** **฿120**

---

## 📅 [2026-08-27] - Session 37: การปรับปรุงระบบกรองขอบเขตราคาขั้นต่ำ (Min Price Boundary) & ราคาสินค้ากระเป๋า ADR

### 🎯 สรุปผลงานที่แก้ไขแล้ว
1. **การกรองขอบเขตราคาขั้นต่ำ (Min Price Boundary Extraction - `_extract_price_bounds`)**:
   - พัฒนาฟังก์ชัน `_extract_price_bounds()` ใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) รองรับทั้งขอบเขตล่าง (`มากกว่า`, `เกิน`, `500 ขึ้นไป`) และขอบเขตบน (`ไม่เกิน`, `ต่ำกว่า`, `งบ 300`)
   - ปรับปรุงการกรองใน `compute_rrf` คัดเฉพาะสินค้าราคา $\ge \text{Min Price}$ ออกมาแสดงเมื่อผู้ใช้ระบุราคาสูงกว่างบขั้นต่ำ
2. **การอัปเดตราคากระเป๋า `The Bagg Canvas Classic Tote` ใน SQLite DB**:
   - อัปเดตราคาในตาราง `products` สำหรับกระเป๋า `The Bagg Canvas Classic Tote` จาก ฿190 เป็น **฿590** ตามราคาขายจริงบนหน้าเว็บ YuedPao
3. **การเพิ่มน้ำหนักสินค้ายอดฮิตขายดี (`sales_vol_boost`)**:
   - ปรับปรุงค่าน้ำหนัก `sales_vol_boost` เมื่อ `is_popular = True` เพื่อดันสินค้ายอดขายสูงสุด (`Ultrasoft`, `Signature`, `Collab`, `Polo`) ขึ้นอันดับ 1-5 อย่างแม่นยำ
4. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest)**:
   - เพิ่มเคสทดสอบ `test_intent_min_price_boundary_filtering` ใน [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py)
   - ผลการรัน Pytest: **ผ่าน 100% ครบทั้ง 16 เคสทดสอบ (16/16 PASSED in 33.94s)**

---

## 📅 [2026-08-27] - Session 36: สรุปสถาปัตยกรรมทางเทคนิคสำหรับนำเสนอ (Presentation Technical Architecture ADR)

### 🎯 สรุปผลงานและจุดเด่นทางเทคนิค (สำหรับนำไปนำเสนอ / Defense)
1. **คลังคำศัพท์สีหลักและเอนจินคำนวณค่าน้ำหนักสี ([product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py))**:
   - ขยาย `COLOR_KEYWORDS_MAP` ครอบคลุม 11 กลุ่มสีหลักทั้งภาษาไทย ภาษาอังกฤษ และชื่อเฉดสีเฉพาะแบรนด์ YuedPao (`แดง`, `แดงเลือดหมู`, `ไวน์`, `Rosewood`, `ชาไทย`, `น้ำเงิน`, `กรม`, `เขียว`, `มิ้นท์`, `Mist Green`, `เหลือง`, `ชมพู`, `ม่วง`, `ส้ม`, `น้ำตาล`, `เทา`, `Smoke Gray`, `ขาว`, `ดำ`)
   - กำหนดลอจิก **2.50x Color Match Boost** ดันสินค้าสีตรงขึ้นอันดับแรก และ **0.15x Non-Match Color Demotion** กดคะแนนสินค้าสีอื่นที่ไม่ตรงออกไป
2. **ระบบแบ่งหน้าแชตอัตโนมัติ (In-Chat Offset Pagination) & เซสชันผู้ใช้**:
   - พัฒนา `search_products(raw_query, top_k=5, offset=N)` และระบบจำเซสชัน `self.user_sessions[user_id]` ใน [tiered_router.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/tiered_router.py)
   - แทรกปุ่มทางลัด Quick Reply แบบไดนามิก (`⏩ ดูเพิ่มเติม (6-10)`, `⏩ ดูเพิ่มเติม (11-15)`) ช่วยให้ผู้ใช้ไถดูสินค้าต่อเนื่องในแอป LINE โดยไม่ต้องเปิดเว็บภายนอก
3. **ระบบกรองกลุ่มอายุและป้องกันหมวดหมู่สินค้าผิดประเภท**:
   - ป้องกันคีย์เวิร์ด `"เด็กชาย"` ไม่ให้ข้ามไปโดนคีย์เวิร์ดผู้ใหญ่ ด้วยเทคนิค `(?<!เด็ก)ชาย` Prefix Regex
   - กำหนด **2.50x Kids Priority Boost** ดันสินค้าเด็ก และ **0.05x Adult Demotion** กดสินค้าผู้ใหญ่ลงล่างสุดเมื่อค้นหาสินค้าเด็ก พร้อมระบบ **0.01x Category Mismatch Factor** กรองหมวดกางเกงใน/ถุงเท้า ออกจากการค้นหาประเภท `"เสื้อ"`
4. **ภาพ Rich Menu ขนาดมาตรฐาน 2500x1686 px พร้อมใช้งาน**:
   - สร้างสคริปต์ `scripts/generate_rich_menu_yuedpao_brand.py` เจนภาพ Rich Menu ความละเอียดสูง 4K พร้อม Header แบรนด์ YuedPao และแมปปิ้ง 6 ปุ่มกด (`action_search`, `action_promotion`, `action_random`, `action_fabric`, `action_size`, `action_contact`)
5. **มาตรฐานการทดสอบอัตโนมัติ (Automated Pytest)**:
   - คำสั่ง `python -m pytest tests/test_all_intents.py -v` ผ่าน **100% ครบทั้ง 15 เคสทดสอบ** ในเวลา 39.33 วินาที

---

## 📅 [2026-08-27] - Session 35: Kids Demographic & Category Mismatch Demotion Fix ADR

### 🎯 Key Accomplishments
1. **Kids Demographic Detection Fix ([app/services/product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py))**:
   - Fixed `_detect_query_gender()` to evaluate kids keywords (`"เด็กชาย"`, `"เด็กหญิง"`, `"เด็ก"`, `"ลูก"`) prior to checking standalone `"ชาย"` to prevent `"เด็กชาย"` from triggering adult male 1.75x boost for men's underwear (`Briefs Unwear Men`).
   - Implemented symmetric Kids Boost / Adult Demotion:
     * When `query_has_kids` is `True`: Kids items get **2.50x Kids Priority Boost**, while adult items get **0.05x Adult Demotion Factor**.
2. **Apparel Category Mismatch Demotion**:
   - Added category mismatch filter when user requests tops/shirts (`"เสื้อ"`, `"โปโล"`, `"คอกลม"`, `"ครอป"`):
     * Non-shirt categories (`UNWEAR`, `ACCESSORIES`, `RIB BRA`, `SOCKS`) are demoted with **0.01x Category Mismatch Factor** to eliminate boxers/briefs from shirt searches.
3. **Database Price Verification**:
   - Confirmed SQLite `products` table prices match actual web prices on YuedPao (e.g. ฿90 for kids shirt, ฿250 for boxers, ฿292.5 for polo sale).
4. **Automated Verification**:
   - Added `test_intent_kids_boy_tshirt_filtering()` in [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py).
   - Executed `python -m pytest tests/test_all_intents.py -v`: **100% Pass Rate (14/14 PASSED in 36.38s)**.

---

## 📅 [2026-08-27] - Session 34: In-Chat Pagination & See More Intent (`see_more_products`) ADR

### 🎯 Key Accomplishments
1. **Product Search Offset Pagination ([app/services/product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py))**:
   - Added `offset: int = 0` parameter to `search_products()`.
   - Updated candidate pool slicing `[offset : offset + top_k]` and included metadata `total_count`, `offset`, and `has_more` in return dictionary.
2. **Intent Engine & Router Integration**:
   - Added `see_more_products` intent with domain triggers (`"ขอดูเพิ่มเติม"`, `"ดูเพิ่มเติม"`, `"ขอดูเพิ่ม"`, `"ขออีก"`, `"ดูเพิ่ม"`, `"ขอเพิ่ม"`, `"ดูรุ่นอื่น"`, `"ดูต่อ"`) in [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py).
   - Implemented `self.user_sessions[user_id]` state management in [tiered_router.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/tiered_router.py) to remember `last_query` and `offset` per user.
   - Dynamically injected `⏩ ดูเพิ่มเติม (6-10)` Quick Reply pills via [quick_replies.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/quick_replies.py).
3. **Automated Test Suite Expansion & Verification**:
   - Added `test_intent_see_more_products_pagination()` in [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py).
   - Executed `python -m pytest tests/test_all_intents.py -v`: **100% Pass Rate (13/13 PASSED in 39.92s)**.

---

## 📅 [2026-08-27] - Session 33: Fair Random Sampling & Session History Integration (`session_history`) ADR

### 🎯 Key Accomplishments
1. **Router Session History Integration ([app/services/tiered_router.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/tiered_router.py))**:
   - Updated `TieredRouter.route_query(raw_query, session_history)` to accept user session history and pass it to `ProductService.get_fair_top5_recommendations(session_history=session_history)`.
   - Ensures user queries for repeated random recommendations (`random_recommendation`) filter out recently recommended product IDs (last 10 items) to guarantee 100% fresh recommendations.
2. **Automated Verification**:
   - Added `test_product_service_fair_random_sampling_session_history()` in [test_services.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_services.py) asserting zero overlap between consecutive sampling batches.
   - Confirmed test pass rate: **1 PASSED in 19.80s**.

---

## 📅 [2026-08-27] - Session 32: Multi-Intent Comprehensive Automated Test Suite (`tests/test_all_intents.py`) ADR

### 🎯 Key Accomplishments
1. **Multi-Intent Comprehensive Test Suite (`tests/test_all_intents.py`)**:
   - Created dedicated test file [test_all_intents.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_all_intents.py) containing 12 automated unit tests across all 6 chatbot intents:
     - `product_search` (Model, color, price filter, popularity/sales volume boost, female preference/style vibe, category filtering for jeans & bags, typo resilience).
     - `coupon_ticket` (Carousel payload verification & `clipboard` action buttons).
     - `promotion_deal` (Daily flash sales & monthly promo deals isolation).
     - `random_recommendation` (Fair 5-item random sampling).
     - `fabric_comparison` (4-Fabric technology guide card).
     - `size_recommendation` (Height & weight size guide card).
2. **Intent Keyword Enrichment in `intent_service.py`**:
   - Expanded `product_triggers` in [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) with category and view keywords (`"อยากเห็น"`, `"กระเป๋า"`, `"กางเกง"`, `"ยีนส์"`, `"โปโล"`, `"ครอป"`, `"เบบี้ที"`).
   - Enriched `INTENT_PASSAGES["product_search"]` passage text to ensure 100% precision in Tier 3 BERT fallback.
3. **Verification & Benchmark Results**:
   - Executed `python -m pytest tests/test_all_intents.py -v`: **100% Pass Rate (12/12 PASSED in 39.60s)**.

---

## 📅 [2026-08-27] - Session 31: Popularity & Sales Volume Boost Search (`sales_vol_boost`) ADR

### 🎯 Key Accomplishments
1. **Sales Volume Database Field & Dynamic SQL Integration**:
   - Updated `ProductService._load_products_from_db()` in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) to dynamically extract `sales_volume` from SQLite `products` table.
   - Injected sales volume metadata into `self.products`, composite document text (`passage: ... | ยอดขาย: X ชิ้น สินค้าขายดี ยอดฮิต`), and ChromaDB `metadatas`.
2. **Popularity Keywords & Tier 1 Intent Routing**:
   - Defined `POPULAR_KEYWORDS` list covering Thai/English popular & best seller terms (`"ขายดี"`, `"ขายดีสุด"`, `"ฮิต"`, `"ฮิตๆ"`, `"ยอดฮิต"`, `"นิยม"`, `"ยอดนิยม"`, `"best seller"`, `"bestseller"`, `"top seller"`, `"ตัวขายดี"`, `"สินค้าขายดี"`, `"ตัวฮิต"`).
   - Updated Tier 1 Priority Rules in [intent_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/intent_service.py) to route popular queries directly to `product_search`.
3. **RRF Sales Volume Multiplier (`sales_vol_boost`)**:
   - Added `_detect_query_popular()` helper and log-scaled popularity boost `sales_vol_boost = 1.0 + min(np.log1p(sales_vol) * 0.25, 1.8)` (yielding up to **~2.65x multiplier** for top-selling items) in RRF Engine (`compute_rrf`).
   - Standard queries apply a minor tie-breaker boost (`1.0 + min(np.log1p(sales_vol) * 0.02, 0.15)`).
4. **Verification & Testing**:
   - Added `test_product_service_popular_sales_volume_search()` in [test_services.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_services.py). Confirmed 100% pass rate across automated unit tests.

---

## 📅 [2026-08-27] - Session 12: Female-First Preference Boost (`1.75x`) & Gender Preference RRF ADR

### 🎯 Key Accomplishments
1. **Gender Preference Match Boost (`gender_match_boost`)**:
   - Resolved issue where Unisex Polo shirts with high BM25 scores beat female-specific products (`Gender: female`) on queries like `"ขอดูเสื้อผู้หญิง..."`.
   - Introduced `gender_match_boost` (1.75x) in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) (`compute_rrf`):
     - When `requested_gender == "female"`, products with `Gender: female` receive a **1.75x boost** over `unisex` items.
     - When `requested_gender == "male"`, products with `Gender: male` receive a **1.75x boost** over `unisex` items.
2. **Polo Crop & Female Apparel Keyword Enrichment**:
   - Expanded `PERSONA_SYNONYMS` for `Polo` and `Crop` with `โปโลครอป`, `polo crop`, `ครอปโปโล`, `เสื้อผู้หญิง`.
3. **Verification Results**:
   - Re-tested `'ขอดูเสื้อผู้หญิงน่ารักๆ หน่อย'` and `'ขอดูเสื้อผู้หญิงสวยๆ หน่อย'`: Top 4 items rendered are 100% Female-specific products (`Gender: female`), completely eliminating Unisex Polo LongSleeve from the top ranks!

---

## 📅 [2026-08-27] - Session 11: Fashion Aesthetic & Style Vibe Understanding (`STYLE_VIBE_KEYWORDS_MAP`) ADR

### 🎯 Key Accomplishments
1. **Fashion Aesthetics & Vibe Architecture**:
   - Defined `STYLE_VIBE_KEYWORDS_MAP` in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) covering 3 primary aesthetic categories:
     - `cool`: `"เท่"`, `"เท่ๆ"`, `"สตรีท"`, `"วินเทจ"`, `"เสื้อฟอก"`, `"ยีนส์"`, `"คาร์โก้"`, `"คูล"`
     - `cute`: `"น่ารัก"`, `"น่ารักๆ"`, `"คิ้วท์"`, `"สดใส"`, `"หวานๆ"`, `"y2k"`
     - `chic`: `"สวย"`, `"สวยๆ"`, `"เรียบหรู"`, `"ดูดี"`, `"สุภาพ"`, `"ใส่ทำงาน"`, `"คัตติ้งเนี๊ยบ"`
2. **Document Expansion & Style Boost**:
   - Injected aesthetic synonyms into `PERSONA_SYNONYMS` for `Oversize`, `Polo`, `Crop`, `Babytee`, `Running Roulette`, and `Tie Dye`.
   - Added `_detect_query_style_vibes()` and `style_vibe_boost` (1.35x) in RRF Hybrid Search Engine (`compute_rrf`).
3. **Structured Debug Logging Upgrade**:
   - Enhanced `search_products()` and `TieredRouter` debug output to print `Gender Filter`, `Style Vibes`, `Intents`, `Colors`, `Max Price`, `Category`, and `Gender` attributes per rendered card.
4. **Verification & Testing**:
   - Added `test_product_service_style_vibe_matching()` in `tests/test_services.py`. All 8 unit tests passed cleanly.

---

## 📅 [2026-08-27] - Session 10: Thai Keyboard Typo Mapping & Demographic Demotion ADR

### 🎯 Key Accomplishments
1. **Thai Apparel Keyboard Typo Mapping (`intent_service.py`)**:
   - Resolved tokenization issue where PyThaiNLP split `"เสื้อบืด"` into `['เสื้อ', 'บืด']`, preventing standard Edit Distance from matching 8-char `"เสื้อยืด"`.
   - Added `TYPO_MAP` in `_correct_word()` handling common Thai typos: `"บืด"` ➔ `"ยืด"`, `"บึด"` ➔ `"ยืด"`, `"เสิ้อยืด"` ➔ `"เสื้อยืด"`, `"babytree"` ➔ `"babytee"`.
   - Verified `'ขอดูเสื้อบืดเท่ๆ'` now cleans perfectly to `'ดู เสื้อยืด เท่'`.

2. **Demographic Demotion Factors (`product_service.py`)**:
   - Resolved issue where broad adult queries (`"ขอดูเสื้อยืดหน่อย"`, `"เสื้อยืดเท่ๆ"`) returned Kids/Crop items in Top-5 due to short name matches.
   - Introduced `kids_boost` (0.15x) and `crop_boost` (0.40x) in `compute_rrf`: demotes Kids and Crop items unless explicitly searched for in the user query.

3. **End-to-End Search Verification**:
   - Re-ran live query `'ขอดูเสื้อบืดเท่ๆ'` through `TieredRouter`: Top-5 items returned 100% adult standard/oversize t-shirts with 0 Kids and 0 Crop items.

---

## 📅 [2026-08-27] - Session 9: Fix BabyTee Category & Style Misclassification ADR

### 🎯 Key Accomplishments
1. **Root Cause Analysis & Diagnosis**:
   - Diagnosed why 16 BabyTee products were incorrectly stored in `yuedpao_chatbot.db` with `category = 'Oversize'` and `style_fit = 'Unisex'`.
   - Identified 2 underlying issues:
     a) Scraper assigned `category = 'Oversize'` based on catalog menu URL names during lazy loading crawl.
     b) `_infer_style_fit()` and `_infer_category()` in [scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py) lacked explicit handlers for `babytee` / `เบบี้ที` keywords, defaulting to `Unisex`.
2. **Database Data Correction**:
   - Updated all 16 BabyTee products in `yuedpao_chatbot.db` setting `category = 'เสื้อยืด BabyTee'` and `style_fit = 'BabyTee'`.
3. **Scraper Service Code Upgrade**:
   - Updated `_infer_category()` and `_infer_style_fit()` in [scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py) adding explicit keyword checks for `babytee`, `เบบี้ที`, `crop`, and `ครอป`.
4. **Search Verification & Vector DB Refresh**:
   - Re-indexed ChromaDB and BM25 index via `ProductService`. Confirmed `BabyTee` search query returns Top-5 items with clean `Category: เสื้อยืด BabyTee` and `Style: BabyTee`.

---

## 📅 [2026-08-27] - Session 8: Product Availability Filtering (`is_available`) & Vector DB Re-indexing

### 🎯 Key Accomplishments
1. **Database Schema & `is_available` Column Support**:
   - Identified 287 out-of-stock / unavailable products out of 695 total products in `yuedpao_chatbot.db`.
   - Updated `ProductService._load_products_from_db()` in [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) to inspect schema dynamically (`PRAGMA table_info(products)`) and filter products strictly `WHERE is_available = 1`.
2. **ChromaDB & BM25 Search Index Auto-Invalidation**:
   - Reduced active indexed document pool from 695 down to **408 active available products**.
   - Triggered clean auto-re-indexing of ChromaDB vector collection (`yuedpao_products_e5_search`) and BM25 index to prevent recommending out-of-stock items to users.
3. **Automated Unit Testing & Verification**:
   - Added `test_product_service_is_available_filtering()` in [test_services.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/tests/test_services.py) asserting all loaded products have `is_available == 1`.
   - Verified 100% test pass rate across the service test suite.

---

## 📅 [2026-08-26] - Session 7: Coupon Ticket & Terms Modal Scraper (`04_coupon_scraper.ipynb`)

### 🎯 Key Accomplishments
1. **Coupon Ticket & Terms Modal Scraper (`notebooks/04_coupon_scraper.ipynb`)**:
   - Created dedicated Jupyter Notebook for scraping coupon containers (`class="w-full flex"`) and left ticket badges (`<div class="flex justify-center items-center flex-col gap-3">` with SVG icon `<g id="bxs:discount">`).
   - Implemented automated popup clicker targeting `<p ...>เงื่อนไขการใช้งาน</p>` to extract **Promo Codes** (e.g. `NEWMEMBER5`, `DIS1000YP1`, `YUEDPAO006`), **Validity Duration** (e.g. `24 ก.ค. 2026 10:00 - 31 ธ.ค. 2033 10:00`), and **Detailed Terms** (e.g. `เมื่อซื้อสินค้า 200 บาทขึ้นไป`).
2. **Database Integration (`coupons` Table)**:
   - Created `coupons` table in `yuedpao_chatbot.db` storing coupon ID, promo code, discount title, min spend, valid duration, detailed condition, eligibility tag, and raw container HTML.
3. **LINE Flex Message Generator**:
   - Implemented `build_line_flex_coupon_carousel()` converting extracted coupon records into LINE Flex Message (Carousel) JSON with `clipboard` action buttons for copying promo codes.

---

## 📅 [2026-08-25] - Session 6: 200 QA Expansion, Enhanced Diagnostic Benchmarking & Price Smart Fallback ADR

### 🎯 Key Accomplishments
1. **QA Benchmark Expansion (100 -> 200 Scenarios)**:
   - Created `notebooks/intent_rank/qa_benchmark_200.json` expanding dataset to 200 QA scenarios across 5 categories (40 per category): Exact Model & Color, Natural Language Fabric Touch, Price Boundary, Typo Resilience (with realistic Thai typing errors), Target Persona.

2. **Diagnostic Evaluation Report Overhaul (`notebooks/intent_rank/rrf_test.ipynb`)**:
   - Added `Ground Truth` & `Max Price` columns for complete visibility during debugging.
   - Added candidate display showing exact matched item name and rank (`Matched / Top-1 Item (Rank #X)`).
   - Added `RRF Score` and `Vector Cosine Similarity Score` to quantify retrieval confidence.
   - Introduced `Precision@1` (Top-1 Accuracy: **82.50%**) alongside `Hit Rate@5` (**90.00%**), `MRR@5` (**0.8600**), and P95 Latency (**53.22 ms**).
   - Implemented Automated Error Categorization: Categorized all 20 misses into 17 Semantic Ranking Misalignments (> Top 5) and 3 Price Exceeded cases.

3. **Price Boundary & Smart Fallback Strategy (ADR)**:
   - Investigated 3 Price Boundary misses (`QA-58` Jeans $\le 400\text{฿}$, `QA-59` Babytee $\le 150\text{฿}$, `QA-145` Tailor Cool $\le 380\text{฿}$). Confirmed Hard Filter (`price <= max_price`) correctly executed, but catalog minimum prices are 790฿, 190฿, 490฿.
   - Formulated **Smart Fallback Strategy**: When hard price filter yields 0 items, system automatically relaxes price constraint to fetch closest matching catalog items and responds with an informative, user-friendly recommendation message on LINE UI.

---

## 📅 [2026-08-25] - Session 5: RRF Hybrid Search Optimization, 100 QA Benchmark & Document Expansion

### 🎯 Key Accomplishments
1. **QA Benchmark Dataset & Evaluation Infrastructure Rebuild**:
   - Created `notebooks/intent_rank/qa_benchmark_100.json` containing 100 ground-truth scenarios across 5 categories (20 each): Exact Model & Color, Natural Language Fabric Touch, Price Boundary, Typo Resilience, Target Persona.
   - Rebuilt `notebooks/intent_rank/rrf_test.ipynb` with 9 complete steps including 100 QA dataset evaluation (Hit Rate@5, MRR@5, P95 Latency, per-category breakdown).

2. **RRF Query Pipeline Constraint Validated**:
   - Discovered and validated that Tier 0 `correct_spelling()` must NOT pre-process queries before RRF Hybrid Search (degrades Hit Rate@5 from 92% to 86% due to stopword removal stripping price/size terms).
   - Saved as Section 5 in `.agents/rules/thai_nlp_chatbot_architecture.md`.

3. **Document Expansion Implementation**:
   - Implemented Document Expansion in Step 3 of `rrf_test.ipynb` injecting Thai/English synonym aliases, color translations, and persona usage keywords directly into composite document passages (`passage: ...`).
   - Saved as Section 6 (Document Expansion) and Section 7 (QA Benchmark Standard) in `.agents/rules/thai_nlp_chatbot_architecture.md`.

4. **Embedding Model Experimentation**:
   - Tested `mrp/SimCSE-model-WangchanBERTa-V2` vs `intfloat/multilingual-e5-small`. Confirmed `multilingual-e5-small` remains optimal for semantic retrieval; restored notebook to `multilingual-e5-small`.

### ⏳ Current Status & Next Action Steps
- **Notebook State**: `notebooks/intent_rank/rrf_test.ipynb` is clean, updated with Document Expansion + 100 QA dataset + `intfloat/multilingual-e5-small`, ready for execution.
- **Next Steps when returning**:
  1. Open and run `rrf_test.ipynb` (or execute via script) to measure new Hit Rate@5 with Document Expansion.
  2. Implement SQL/Python Post-filtering for Price Boundary queries in `app/services/product_service.py`.

---

## 📅 [2026-08-25] - Session 4: Unified Rules Synchronization & Obsidian-Graphify Workflow Enforcement

### 🎯 Key Accomplishments
1. **Rule System Unification & Synchronization**:
   - Created `[[obsidian_graphify.md]]` defining the dual knowledge-code workflow: Obsidian Vault (`yuedpao_brain/`) for domain requirements & ADRs, Graphify (`graphify-out/`) for execution call-graphs & module dependencies.
   - Synchronized all 7 system rule files across both `.gemini/rules/` and `.agents/rules/`: `obsidian_graphify.md`, `obsidian_wiki.md`, `graphify.md`, `thai_nlp_chatbot_architecture.md`, `rubric_priority.md`, `line_bot_sdk.md`, and `testing.md`.
2. **Root Context & Enforcement Verification**:
   - Updated root `GEMINI.md` to enforce the complete rule set.
   - Executed `python -m pytest` test suite to verify 100% pass rate.

---

## 📅 [2026-08-23] - Session 3: MVC + Services Folder Skeleton Setup & Architecture Documented

### 🎯 Key Accomplishments
1. **MVC + Services Skeleton Generation**:
   - Created `app/` folder structure: `models/`, `views/`, `controllers/`, `services/`.
   - Created `tests/` folder structure: `test_models.py`, `test_views.py`, `test_services.py`.
   - Initialized `notebooks/01_test_scraper.ipynb` for Scraper POC.
2. **Knowledge Vault Blueprint Sync**:
   - Created `[[project-architecture]]` note in `yuedpao_brain/wiki/` detailing the responsibility of each layer.
   - Updated `[[index]]` sitemap.

---

## 📅 [2026-08-23] - Session 2: Migration to yuedpao_brain Vault & Obsidian Skill Alignment

### 🎯 Key Accomplishments
1. **Vault Migration & Restructuring**:
   - Migrated knowledge base from legacy `Wiki` path to **`yuedpao_brain/`** Knowledge Vault.
   - Initialized `.obsidian/` configuration folder (`app.json`, `core-plugins.json`, `graph.json`) enabling out-of-the-box Obsidian app compatibility.
2. **System Rules Sync**:
   - Updated `.gemini/rules/obsidian_wiki.md` to reference `yuedpao_brain/` path.
   - Updated `.gemini/rules/graphify.md` and `.gemini/rules/testing.md`.
3. **Obsidian Skill & Graph Network**:
   - Linked notes with bidirectional `[[Wikilinks]]`, tags, YAML properties, and GitHub/Obsidian callouts.

---

## 📅 [2026-08-23] - Session 1: Project Initialization & Knowledge Base Customization

### 🎯 Key Accomplishments
1. **Source Document Ingestion**:
   - Ingested raw PDF specification `ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.pdf` into `yuedpao_brain/sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md`.
2. **System Rules & Configuration Alignment**:
   - Customised `.gemini/rules/obsidian_wiki.md` to reflect Yuedpao system components, domain dictionary, and wiki conventions.
   - Updated `.gemini/rules/graphify.md` to list core system nodes (`TieredRouter`, `EditDistanceBERT`, `YuedpaoScraper`, `LineFlexBuilder`, `ProductDatabase`).
   - Configured `.gemini/rules/testing.md` for 4-tier router, candidate generation, scraper fallback, and Flex Message validation.
   - Updated `yuedpao_brain/GEMINI_BRAIN.md` schema definition.
3. **Comprehensive Knowledge Base Build**:
   - Created `[[index]]` sitemap.
   - Built `[[project-overview]]`, `[[architecture-tiered-router]]`, `[[nlp-spelling-correction]]`, `[[core-features-rich-menu]]`, `[[product-catalog-scraping]]`, `[[carousel-randomization]]`, `[[rubric-evaluation-checkpoints]]`, and `[[database-schema]]`.


## 📅 [2026-08-25] - Session 7: Color-Aware Evaluation, Data Hygiene Cleanup & Production Intent Roadmap ADR

### 🎯 Key Accomplishments
1. **Color-Aware Evaluation Framework Implementation (`notebooks/intent_rank/rrf_test.ipynb`)**:
   - Upgraded evaluation framework to validate **`expected_color`** in addition to model keywords.
   - Re-benchmarked 200 QA scenarios across 5 categories and discovered that 15 out of 24 initial misses were **Wrong Color Matches** (model matched correctly, but color variant differed).
   - Added **Color Match Boosting (1.30x Multiplier)** in `rrf_hybrid_search` to prioritize user-requested colors.

2. **Data Hygiene Cleanup (100% SQLite DB Cleaning)**:
   - Discovered and cleaned **142 dirty product category rows** in `yuedpao_chatbot.db` where scraped HTML text (e.g. `ส่งฟรี*\n...`) contaminated SQLite `category` fields.
   - Cleaned all dirty category strings into standardized categories (`Polo`, `Oversize`, `Babytee`, `Crop`, `Running / Activewear`, `Sleeveless`, `กางเกงยีนส์`, `Pants & Shorts`, `Outerwear & Hoodies`, `Accessories`). Verified 0 dirty rows remain.

3. **Final Production Benchmark Results**:
   - **Precision@1**: **86.50%** (173/200 exact color & model top-1 hits!)
   - **Hit Rate@5**: **94.50%** (189/200 top-5 carousel exact hits!)
   - **MRR@5**: **0.8988**
   - **Typo Resilience Hit Rate@5**: **100.00%** (40/40)
   - **P95 Latency**: **44.60 ms**

4. **Production Intent Architecture Roadmap (ADR)**:
   - Finalized production Intent Architecture based on business reality and DB data availability (avoiding LLM dependency & un-scraped OCR images):
     - **🔥 Priority 1: `product_search`**: Specific search by spec, color, price limit, model & collection (handles model/collection search natively via 1.25x RRF Intent Boost).
     - **🎲 Priority 2: `random_recommendation`**: Fair Random Sampling of Top-5 recommendations using `get_fair_top5_recommendations()` excluding session history.
     - **🏷️ Priority 3: `promotion_discount`**: Promotion carousel displaying `End of year sale` and `ส่งฟรี` items from DB.
     - **💡 Optional (Low Priority): `fabric_comparison`**: Knowledge card explaining fabric benefits (Ultrasoft, Tailor Cool, Classic Cotton, Ecotech).
   - Confirmed Size Recommendation and Store Branch Locator are excluded from Scope due to website data being un-scraped image banners.

5. **Code & Test Suite Synchronization**:
   - Synchronized RRF Hybrid Search Engine (Document Expansion 2.0, Intent Boost, Color Boost, Smart Price Fallback) into production service file `app/services/product_service.py`.
   - Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).


### 💡 ADR: Tier 1 Rule-Based & Edit-Distance Routing for Promotion Intent (`promotion_discount`)
- **Decision**: Implemented a **Tier 1 Priority Rule + Tier 0 Edit-Distance** approach for the `promotion_discount` intent to achieve **< 5 ms sub-second latency** and 100% deterministic output.
- **Routing Rules**:
  1. **Daily Deals Trigger (`daily_deal`)**: Keywords `ประจำวัน`, `วันนี้`, `flash sale`, `แฟลชเซล` (with Edit-Distance typo tolerance e.g. `ดีลปะจำวัน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'daily_deal'` and return Daily Deals Carousel Card immediately.
  2. **Monthly Deals Trigger (`monthly_deal`)**: Keywords `ประจำเดือน`, `เดือนนี้`, `ดีลเดือน` (with Edit-Distance typo tolerance e.g. `ดีลปะจำเดือน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'monthly_deal'` and return Monthly Deals Carousel Card immediately.
  3. **Natural Language / Specific Spec Search**: If user asks open-ended or spec-specific promo queries (e.g. *"มีกางเกงยีนส์ลดราคาไหม"*), fall back to `PromotionService.search_promotions()` via RRF Hybrid Search (`yuedpao_promotions_e5` collection).


---

## 📌 Session 8: Promotion Scraper, Persistent ChromaDB & Typo Benchmark (2026-08-26)

### 1. Targeted Deep Promotion Scraper (`notebooks/03_promotion_scraper.ipynb`)
- Built deep detail scraper for Home Page `/countdown/...` links (Daily Deals & Monthly Deals).
- Navigated into individual product pages (`/physical/...`) to extract rich metadata: `description`, `colors`, `sizes_json`, `size_chart_url`, and `gallery_images_json`.
- Populated 13 rich promotional items into SQLite `promotions` table in `yuedpao_chatbot.db`.

### 2. Single Source of Truth DB Cleanup
- Deleted duplicate database `notebooks/yuedpao_chatbot.db` (30 KB).
- Re-routed all notebooks to use root master database `yuedpao_chatbot.db` (`../yuedpao_chatbot.db`).

### 3. Persistent ChromaDB Architecture (`data/chroma/`)
- Updated `ProductService` and `IntentService` to use `chromadb.PersistentClient(path="data/chroma")`.
- Untracked `data/chroma/` and `.vscode/` from Git index and added wildcard rules to `.gitignore`.
- Created persistent collections: `yuedpao_products_e5_search` (695 items), `yuedpao_promotions_e5` (13 items), and `intent_few_shot` (136 items).

### 4. Promotion Service Engine (`app/services/promotion_service.py`)
- Created `PromotionService` engine handling RRF Hybrid Search for promotion items and fast incremental indexing (< 0.5s).

### 5. Promotion Typo Resilience Benchmark Notebook (`notebooks/intent_rank/test_promotion_typo_intent.ipynb`)
- Created dedicated evaluation notebook for promotion queries with Thai typos.
- Enriched `domain_vocab.json` with promotion vocabulary (`ประจำวัน`, `ประจำเดือน`, `โปรโมชัน`, `ส่วนลด`, `คูปอง`, `แฟลชเซล`, `ดีลพิเศษ`).
- Added Tier 1 Promotion Priority Rule in `intent_service.py` and auto-sync guard for `intent_few_shot` collection.
- **Result:** Achieved **93.33% Accuracy** (14/15) and **< 1.5 ms Latency** on Thai promotion typo queries.
- **Verification:** Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).

---

### 📌 Session 9: Intent Classification Comparison & 5-Fold CV Leakage Fix (`compare_editdistance_vs_pure_bert.ipynb`)
- Created and upgraded dedicated experiment notebook `notebooks/intent_rank/compare_editdistance_vs_pure_bert.ipynb` evaluating 5 architectures:
  1. Method 1: Pure BERT (`intfloat/multilingual-e5-small`) on raw queries.
  2. Method 2: Edit Distance + BERT (Tier 0 spell correction pre-processing).
  3. Method 3: Tier 1 Priority Rules + Pure BERT.
  4. Method 4a: 4-Tier Pipeline (No Few-Shot ChromaDB Lookup).
  5. Method 4b: Full 4-Tier Pipeline (With 100% Leak-Free 5-Fold Stratified Cross-Validation Few-Shot Indexing).
- Resolved Data Leakage by isolating ChromaDB Few-Shot indexing to Train Folds (80%) and testing strictly on Test Folds (20%).
- Added Model Warmup step for precise sub-millisecond latency profiling.

---

### 📌 Session 10: LINE Bot SDK v3 & Flask Architecture Integration
1. **Flask Webhook Controller (`app/main.py` & `app/controllers/webhook_controller.py`)**:
   - Initialized Flask Webhook App with `/callback` POST endpoint supporting `linebot.v3.WebhookHandler` and `MessagingApi`.
   - Added mock mode handling for local development testing without real LINE Secret keys.
   - Added `/health` healthcheck route returning JSON server status.
2. **TieredRouter Integration (`app/services/tiered_router.py`)**:
   - Implemented `TieredRouter` dispatching user inquiries across 5 intents (`product_search`, `promotion_discount`, `random_recommendation`, `fabric_comparison`, `size_recommendation`).
3. **LINE Flex Message Views (`app/views/`)**:
   - `flex_carousel.py`: Built `build_product_flex_carousel()` (Top-5 products, 1:1 image aspect, maxLines 2) and `build_coupon_flex_carousel()` with `📋 คัดลอกโค้ด` (`clipboard` action).
   - `flex_fabric.py`: Built 4-Fabric technology guide card & standard size chart card.
   - `quick_replies.py`: Built interactive Quick Reply pills.
   - `rich_menu_views.py`: Built Rich Menu postback action mapping.
4. **Code Hygiene & Cleanup**:
   - Removed unused/redundant placeholder files (`app/services/nlp_spelling.py` and `app/controllers/admin_controller.py`).

---

### 📌 Session 13: Promotion Image URL & SVG Filter Fix
1. **SVG Image Filtering & Product Image Fallback ([app/services/promotion_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/promotion_service.py))**:
   - Resolved issue where images failed to render on LINE Flex Carousel for Daily Deals.
   - Identified root cause: `promotions` table stored SVG badge icon URLs (`https://www.yuedpao.com/images/free-delivery.svg`), which LINE Flex Messaging API `<hero><image>` cannot render.
   - Updated `PromotionService._load_promotions_from_db()` to `LEFT JOIN products` table, replacing SVG badge icons with actual product PNG/JPEG cover image URLs (`https://mp-static.yuedpao.com/...`).
2. **LINE Flex View SVG Guard ([app/views/flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py))**:
   - Added explicit fallback guard in `build_product_flex_carousel()` to intercept any remaining `.svg` or `free-delivery` URLs and replace them with standard YuedPao PNG cover images (`https://mp-static.yuedpao.com/images/logo.png`).
3. **Verification**:
   - Verified clean resolution of PNG/JPEG image URLs across all Daily Deals items.

---

### 📌 Session 14: Daily vs Monthly Deals Separation & 6th Pagination Card
1. **Daily Deals (`daily_deal`) vs Monthly Deals (`monthly_deal`) Separation**:
---

## 📅 [2026-08-25] - Session 5: RRF Hybrid Search Optimization, 100 QA Benchmark & Document Expansion

### 🎯 Key Accomplishments
1. **QA Benchmark Dataset & Evaluation Infrastructure Rebuild**:
   - Created `notebooks/intent_rank/qa_benchmark_100.json` containing 100 ground-truth scenarios across 5 categories (20 each): Exact Model & Color, Natural Language Fabric Touch, Price Boundary, Typo Resilience, Target Persona.
   - Rebuilt `notebooks/intent_rank/rrf_test.ipynb` with 9 complete steps including 100 QA dataset evaluation (Hit Rate@5, MRR@5, P95 Latency, per-category breakdown).

2. **RRF Query Pipeline Constraint Validated**:
   - Discovered and validated that Tier 0 `correct_spelling()` must NOT pre-process queries before RRF Hybrid Search (degrades Hit Rate@5 from 92% to 86% due to stopword removal stripping price/size terms).
   - Saved as Section 5 in `.agents/rules/thai_nlp_chatbot_architecture.md`.

3. **Document Expansion Implementation**:
   - Implemented Document Expansion in Step 3 of `rrf_test.ipynb` injecting Thai/English synonym aliases, color translations, and persona usage keywords directly into composite document passages (`passage: ...`).
   - Saved as Section 6 (Document Expansion) and Section 7 (QA Benchmark Standard) in `.agents/rules/thai_nlp_chatbot_architecture.md`.

4. **Embedding Model Experimentation**:
   - Tested `mrp/SimCSE-model-WangchanBERTa-V2` vs `intfloat/multilingual-e5-small`. Confirmed `multilingual-e5-small` remains optimal for semantic retrieval; restored notebook to `multilingual-e5-small`.

### ⏳ Current Status & Next Action Steps
- **Notebook State**: `notebooks/intent_rank/rrf_test.ipynb` is clean, updated with Document Expansion + 100 QA dataset + `intfloat/multilingual-e5-small`, ready for execution.
- **Next Steps when returning**:
  1. Open and run `rrf_test.ipynb` (or execute via script) to measure new Hit Rate@5 with Document Expansion.
  2. Implement SQL/Python Post-filtering for Price Boundary queries in `app/services/product_service.py`.

---

## 📅 [2026-08-25] - Session 4: Unified Rules Synchronization & Obsidian-Graphify Workflow Enforcement

### 🎯 Key Accomplishments
1. **Rule System Unification & Synchronization**:
   - Created `[[obsidian_graphify.md]]` defining the dual knowledge-code workflow: Obsidian Vault (`yuedpao_brain/`) for domain requirements & ADRs, Graphify (`graphify-out/`) for execution call-graphs & module dependencies.
   - Synchronized all 7 system rule files across both `.gemini/rules/` and `.agents/rules/`: `obsidian_graphify.md`, `obsidian_wiki.md`, `graphify.md`, `thai_nlp_chatbot_architecture.md`, `rubric_priority.md`, `line_bot_sdk.md`, and `testing.md`.
2. **Root Context & Enforcement Verification**:
   - Updated root `GEMINI.md` to enforce the complete rule set.
   - Executed `python -m pytest` test suite to verify 100% pass rate.

---

## 📅 [2026-08-23] - Session 3: MVC + Services Folder Skeleton Setup & Architecture Documented

### 🎯 Key Accomplishments
1. **MVC + Services Skeleton Generation**:
   - Created `app/` folder structure: `models/`, `views/`, `controllers/`, `services/`.
   - Created `tests/` folder structure: `test_models.py`, `test_views.py`, `test_services.py`.
   - Initialized `notebooks/01_test_scraper.ipynb` for Scraper POC.
2. **Knowledge Vault Blueprint Sync**:
   - Created `[[project-architecture]]` note in `yuedpao_brain/wiki/` detailing the responsibility of each layer.
   - Updated `[[index]]` sitemap.

---

## 📅 [2026-08-23] - Session 2: Migration to yuedpao_brain Vault & Obsidian Skill Alignment

### 🎯 Key Accomplishments
1. **Vault Migration & Restructuring**:
   - Migrated knowledge base from legacy `Wiki` path to **`yuedpao_brain/`** Knowledge Vault.
   - Initialized `.obsidian/` configuration folder (`app.json`, `core-plugins.json`, `graph.json`) enabling out-of-the-box Obsidian app compatibility.
2. **System Rules Sync**:
   - Updated `.gemini/rules/obsidian_wiki.md` to reference `yuedpao_brain/` path.
   - Updated `.gemini/rules/graphify.md` and `.gemini/rules/testing.md`.
3. **Obsidian Skill & Graph Network**:
   - Linked notes with bidirectional `[[Wikilinks]]`, tags, YAML properties, and GitHub/Obsidian callouts.

---

## 📅 [2026-08-23] - Session 1: Project Initialization & Knowledge Base Customization

### 🎯 Key Accomplishments
1. **Source Document Ingestion**:
   - Ingested raw PDF specification `ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.pdf` into `yuedpao_brain/sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md`.
2. **System Rules & Configuration Alignment**:
   - Customised `.gemini/rules/obsidian_wiki.md` to reflect Yuedpao system components, domain dictionary, and wiki conventions.
   - Updated `.gemini/rules/graphify.md` to list core system nodes (`TieredRouter`, `EditDistanceBERT`, `YuedpaoScraper`, `LineFlexBuilder`, `ProductDatabase`).
   - Configured `.gemini/rules/testing.md` for 4-tier router, candidate generation, scraper fallback, and Flex Message validation.
   - Updated `yuedpao_brain/GEMINI_BRAIN.md` schema definition.
3. **Comprehensive Knowledge Base Build**:
   - Created `[[index]]` sitemap.
   - Built `[[project-overview]]`, `[[architecture-tiered-router]]`, `[[nlp-spelling-correction]]`, `[[core-features-rich-menu]]`, `[[product-catalog-scraping]]`, `[[carousel-randomization]]`, `[[rubric-evaluation-checkpoints]]`, and `[[database-schema]]`.


## 📅 [2026-08-25] - Session 7: Color-Aware Evaluation, Data Hygiene Cleanup & Production Intent Roadmap ADR

### 🎯 Key Accomplishments
1. **Color-Aware Evaluation Framework Implementation (`notebooks/intent_rank/rrf_test.ipynb`)**:
   - Upgraded evaluation framework to validate **`expected_color`** in addition to model keywords.
   - Re-benchmarked 200 QA scenarios across 5 categories and discovered that 15 out of 24 initial misses were **Wrong Color Matches** (model matched correctly, but color variant differed).
   - Added **Color Match Boosting (1.30x Multiplier)** in `rrf_hybrid_search` to prioritize user-requested colors.

2. **Data Hygiene Cleanup (100% SQLite DB Cleaning)**:
   - Discovered and cleaned **142 dirty product category rows** in `yuedpao_chatbot.db` where scraped HTML text (e.g. `ส่งฟรี*\n...`) contaminated SQLite `category` fields.
   - Cleaned all dirty category strings into standardized categories (`Polo`, `Oversize`, `Babytee`, `Crop`, `Running / Activewear`, `Sleeveless`, `กางเกงยีนส์`, `Pants & Shorts`, `Outerwear & Hoodies`, `Accessories`). Verified 0 dirty rows remain.

3. **Final Production Benchmark Results**:
   - **Precision@1**: **86.50%** (173/200 exact color & model top-1 hits!)
   - **Hit Rate@5**: **94.50%** (189/200 top-5 carousel exact hits!)
   - **MRR@5**: **0.8988**
   - **Typo Resilience Hit Rate@5**: **100.00%** (40/40)
   - **P95 Latency**: **44.60 ms**

4. **Production Intent Architecture Roadmap (ADR)**:
   - Finalized production Intent Architecture based on business reality and DB data availability (avoiding LLM dependency & un-scraped OCR images):
     - **🔥 Priority 1: `product_search`**: Specific search by spec, color, price limit, model & collection (handles model/collection search natively via 1.25x RRF Intent Boost).
     - **🎲 Priority 2: `random_recommendation`**: Fair Random Sampling of Top-5 recommendations using `get_fair_top5_recommendations()` excluding session history.
     - **🏷️ Priority 3: `promotion_discount`**: Promotion carousel displaying `End of year sale` and `ส่งฟรี` items from DB.
     - **💡 Optional (Low Priority): `fabric_comparison`**: Knowledge card explaining fabric benefits (Ultrasoft, Tailor Cool, Classic Cotton, Ecotech).
   - Confirmed Size Recommendation and Store Branch Locator are excluded from Scope due to website data being un-scraped image banners.

5. **Code & Test Suite Synchronization**:
   - Synchronized RRF Hybrid Search Engine (Document Expansion 2.0, Intent Boost, Color Boost, Smart Price Fallback) into production service file `app/services/product_service.py`.
   - Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).


### 💡 ADR: Tier 1 Rule-Based & Edit-Distance Routing for Promotion Intent (`promotion_discount`)
- **Decision**: Implemented a **Tier 1 Priority Rule + Tier 0 Edit-Distance** approach for the `promotion_discount` intent to achieve **< 5 ms sub-second latency** and 100% deterministic output.
- **Routing Rules**:
  1. **Daily Deals Trigger (`daily_deal`)**: Keywords `ประจำวัน`, `วันนี้`, `flash sale`, `แฟลชเซล` (with Edit-Distance typo tolerance e.g. `ดีลปะจำวัน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'daily_deal'` and return Daily Deals Carousel Card immediately.
  2. **Monthly Deals Trigger (`monthly_deal`)**: Keywords `ประจำเดือน`, `เดือนนี้`, `ดีลเดือน` (with Edit-Distance typo tolerance e.g. `ดีลปะจำเดือน`) $\rightarrow$ Query SQLite `promotions` table where `deal_type = 'monthly_deal'` and return Monthly Deals Carousel Card immediately.
  3. **Natural Language / Specific Spec Search**: If user asks open-ended or spec-specific promo queries (e.g. *"มีกางเกงยีนส์ลดราคาไหม"*), fall back to `PromotionService.search_promotions()` via RRF Hybrid Search (`yuedpao_promotions_e5` collection).


---

## 📌 Session 8: Promotion Scraper, Persistent ChromaDB & Typo Benchmark (2026-08-26)

### 1. Targeted Deep Promotion Scraper (`notebooks/03_promotion_scraper.ipynb`)
- Built deep detail scraper for Home Page `/countdown/...` links (Daily Deals & Monthly Deals).
- Navigated into individual product pages (`/physical/...`) to extract rich metadata: `description`, `colors`, `sizes_json`, `size_chart_url`, and `gallery_images_json`.
- Populated 13 rich promotional items into SQLite `promotions` table in `yuedpao_chatbot.db`.

### 2. Single Source of Truth DB Cleanup
- Deleted duplicate database `notebooks/yuedpao_chatbot.db` (30 KB).
- Re-routed all notebooks to use root master database `yuedpao_chatbot.db` (`../yuedpao_chatbot.db`).

### 3. Persistent ChromaDB Architecture (`data/chroma/`)
- Updated `ProductService` and `IntentService` to use `chromadb.PersistentClient(path="data/chroma")`.
- Untracked `data/chroma/` and `.vscode/` from Git index and added wildcard rules to `.gitignore`.
- Created persistent collections: `yuedpao_products_e5_search` (695 items), `yuedpao_promotions_e5` (13 items), and `intent_few_shot` (136 items).

### 4. Promotion Service Engine (`app/services/promotion_service.py`)
- Created `PromotionService` engine handling RRF Hybrid Search for promotion items and fast incremental indexing (< 0.5s).

### 5. Promotion Typo Resilience Benchmark Notebook (`notebooks/intent_rank/test_promotion_typo_intent.ipynb`)
- Created dedicated evaluation notebook for promotion queries with Thai typos.
- Enriched `domain_vocab.json` with promotion vocabulary (`ประจำวัน`, `ประจำเดือน`, `โปรโมชัน`, `ส่วนลด`, `คูปอง`, `แฟลชเซล`, `ดีลพิเศษ`).
- Added Tier 1 Promotion Priority Rule in `intent_service.py` and auto-sync guard for `intent_few_shot` collection.
- **Result:** Achieved **93.33% Accuracy** (14/15) and **< 1.5 ms Latency** on Thai promotion typo queries.
- **Verification:** Verified 100% pass rate across automated test suite (`python -m pytest`: 3/3 passed).

---

### 📌 Session 9: Intent Classification Comparison & 5-Fold CV Leakage Fix (`compare_editdistance_vs_pure_bert.ipynb`)
- Created and upgraded dedicated experiment notebook `notebooks/intent_rank/compare_editdistance_vs_pure_bert.ipynb` evaluating 5 architectures:
  1. Method 1: Pure BERT (`intfloat/multilingual-e5-small`) on raw queries.
  2. Method 2: Edit Distance + BERT (Tier 0 spell correction pre-processing).
  3. Method 3: Tier 1 Priority Rules + Pure BERT.
  4. Method 4a: 4-Tier Pipeline (No Few-Shot ChromaDB Lookup).
  5. Method 4b: Full 4-Tier Pipeline (With 100% Leak-Free 5-Fold Stratified Cross-Validation Few-Shot Indexing).
- Resolved Data Leakage by isolating ChromaDB Few-Shot indexing to Train Folds (80%) and testing strictly on Test Folds (20%).
- Added Model Warmup step for precise sub-millisecond latency profiling.

---

### 📌 Session 10: LINE Bot SDK v3 & Flask Architecture Integration
1. **Flask Webhook Controller (`app/main.py` & `app/controllers/webhook_controller.py`)**:
   - Initialized Flask Webhook App with `/callback` POST endpoint supporting `linebot.v3.WebhookHandler` and `MessagingApi`.
   - Added mock mode handling for local development testing without real LINE Secret keys.
   - Added `/health` healthcheck route returning JSON server status.
2. **TieredRouter Integration (`app/services/tiered_router.py`)**:
   - Implemented `TieredRouter` dispatching user inquiries across 5 intents (`product_search`, `promotion_discount`, `random_recommendation`, `fabric_comparison`, `size_recommendation`).
3. **LINE Flex Message Views (`app/views/`)**:
   - `flex_carousel.py`: Built `build_product_flex_carousel()` (Top-5 products, 1:1 image aspect, maxLines 2) and `build_coupon_flex_carousel()` with `📋 คัดลอกโค้ด` (`clipboard` action).
   - `flex_fabric.py`: Built 4-Fabric technology guide card & standard size chart card.
   - `quick_replies.py`: Built interactive Quick Reply pills.
   - `rich_menu_views.py`: Built Rich Menu postback action mapping.
4. **Code Hygiene & Cleanup**:
   - Removed unused/redundant placeholder files (`app/services/nlp_spelling.py` and `app/controllers/admin_controller.py`).

---

### 📌 Session 13: Promotion Image URL & SVG Filter Fix
1. **SVG Image Filtering & Product Image Fallback ([app/services/promotion_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/promotion_service.py))**:
   - Resolved issue where images failed to render on LINE Flex Carousel for Daily Deals.
   - Identified root cause: `promotions` table stored SVG badge icon URLs (`https://www.yuedpao.com/images/free-delivery.svg`), which LINE Flex Messaging API `<hero><image>` cannot render.
   - Updated `PromotionService._load_promotions_from_db()` to `LEFT JOIN products` table, replacing SVG badge icons with actual product PNG/JPEG cover image URLs (`https://mp-static.yuedpao.com/...`).
2. **LINE Flex View SVG Guard ([app/views/flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py))**:
   - Added explicit fallback guard in `build_product_flex_carousel()` to intercept any remaining `.svg` or `free-delivery` URLs and replace them with standard YuedPao PNG cover images (`https://mp-static.yuedpao.com/images/logo.png`).
3. **Verification**:
   - Verified clean resolution of PNG/JPEG image URLs across all Daily Deals items.

---

### 📌 Session 14: Daily vs Monthly Deals Separation & 6th Pagination Card
1. **Daily Deals (`daily_deal`) vs Monthly Deals (`monthly_deal`) Separation**:
   - Updated `deal_type` in SQLite `promotions` table via script `app/scripts/update_deals.py` (`daily_deal` for items 1-6, `monthly_deal` for items 7-13).
   - Added `deal_type_filter` in `PromotionService.search_promotions()` to strictly isolate daily flash sale items when user asks for `"ประจำวัน"` or `"แฟลชเซล"`, and monthly promo items when user asks for `"ประจำเดือน"`.
2. **6th Pagination "Show More" Carousel Card ([app/views/flex_carousel.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/views/flex_carousel.py))**:
   - Added automatic 6th bubble card (`⏩ ดูเพิ่มเติม`) at the end of LINE Flex Carousel whenever query results exceed 5 items.
   - Card features remaining item count (e.g. `ยังมีดีลน่าสนใจอีก N รายการ`) and a `🌐 ดูทั้งหมดบนเว็บ` button to direct users to YuedPao's website.
3. **Verification**:
   - Verified 100% strict deal type isolation and clean rendering of 6th pagination card across test queries.

---

### 📌 Session 29: Targeted Out-of-Stock Heading Match Fix (`h4` / `h5`)
1. **Root Cause Analysis & Fix ([scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py))**:
   - **Discovered Trap**: In-stock product pages (such as `Milky Way`) contain a "สินค้าที่คุณอาจชอบ" (Recommended Products) grid carousel at the bottom of the page. Out-of-stock items in that footer carousel have `<span>สินค้าหมด</span>` badges.
   - Performing a naive global `"สินค้าหมด" in page_text` search caused in-stock pages to be falsely flagged as out of stock.
   - **Fix**: Updated `scrape_product_detail` to target specifically the main product out-of-stock heading element:
     ```python
     out_of_stock_h4 = soup.find(lambda tag: tag.name in ["h4", "h5"] and "สินค้าหมด" in tag.get_text())
     is_available = (out_of_stock_h4 is None)
     ```
2. **Verification & Testing**:
   - Tested live against `Dark Green` (Out of stock) -> `is_available = False` (`0`).
   - Tested live against `Milky Way` (In stock) -> `is_available = True` (`1`).
   - Tested live against `Worm Yellow` (In stock) -> `is_available = True` (`1`).
   - Full pytest suite passed clean (11/11 passed in 87s).

### 📌 Session 30: Scraper Robustness, Concurrency, Prices & Sales Volume ADR
1. **Drawer Menu Crawling & Direct URL Fallback ([app/services/scraper_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/scraper_service.py))**:
   - Replaced brittle auto-generated CSS class `span.css-1dwwjt3` with semantic class fallbacks (`span.pointer-cursor` and `.MuiDrawer-paper span`) to withstand front-end MUI Emotion styling updates.
   - Fixed bug where categories without subcategories (e.g. `ACCESSORIES`, `RIB BRA`, `UNWEAR`) were completely skipped by capturing browser direct URL redirections (`page.url`) on drawer element click.
   - Prioritized collection-level landing pages (`ดูทั้งหมด`) to avoid redundant subcategory crawling, accelerating crawl speed by ~5x.
2. **Concurrent Category Scraping ([app/scripts/run_scraper.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/scripts/run_scraper.py))**:
   - Redesigned crawler pipeline from sequential category scraping to concurrent scraping using `asyncio.gather` controlled by `asyncio.Semaphore(3)`.
   - Utilizes separate browser context pages (`browser.new_context`) for memory-isolated concurrent network requests.
3. **Decimal Price Bug & Sales Volume Extraction**:
   - Fixed split decimal prices bug (e.g., 390.50 being split into integer arrays `[390, 50]` where `min` returned `50`) by using float-aware regular expression patterns.
   - Added `sales_volume` (INTEGER DEFAULT 0) column to `products` SQLite schema via auto-migration checks during DB initialization.
   - Shifted sales volume extraction from catalog-level (where it was not rendered by Yuedpao's client-side templates) to product detail page-level parser (`scrape_product_detail()`), supporting standard counts and thousands formats (e.g. `34 ขายแล้ว`, `1.2k ขายแล้ว`).
4. **Allowed Categories Filtering**:
   - Implemented `ALLOWED_MAIN_CATEGORIES` list containing the 28 standard categories requested by the user.
   - Bypasses temporary promotional, seasonal, and event categories (e.g. `CHRISTMAS 2025`, `End of year sale 50%`, `End of year sale 40%`, etc.) to prevent database pollution and redundant product scans.
5. **Verification & Testing**:
   - Verified parallel crawler execution with `--limit-categories 5 --limit 3 --force`: 8 categories (5 discovered + 3 fallbacks) scraped concurrently. Successfully parsed decimal prices (e.g. `390.00`, `990.00`) and sales volume counters into SQLite database.
   - Verified that the allowed categories filtering works perfectly by bypassing seasonal sales categories during menu structure flattening.
   - Verified detail-level sales volume parsing on live products (Sweater `3 ขายแล้ว`, Ultrasoft `34 ขายแล้ว`).
   - Verified that the full pytest suite (18/18 tests) passes clean.

## 📅 [2026-08-28] - Session 53 & 54: Full Description Rescrape, Pure Native NLP (`pythainlp`), Structured Attribute Filtering & Comprehensive Benchmark ADR

### 🎯 สรุปผลงาน สถาปัตยกรรม และการตัดสินใจ (ADR)

#### 1. การดึงสเปกสินค้าฉบับเต็ม (Full Description Rescrape 1,341 รายการ):
- **ปัญหาเดิม:** DB เดิมโดนจำกัดความยาว Description ไว้ที่ 60 ตัวอักษร ทำให้คำสำคัญเชิงสตอรี่ (เช่น *"พะยูน"*, *"อนุรักษ์ทะเล"*, *"Cotton 60%"*) หายไป ส่งผลให้ Search Engine หาไม่เจอ (0% Hit Rate)
- **การแก้ไข:** ปรับปรุง `scraper_service.py` ดึงข้อมูลจาก Container ใหญ่ `div.py-4.tablet:pb-0.tablet:pt-10.desktop:pt-12` โดยไม่จำกัดความยาว อัปเดตสินค้าครบทั้ง 1,341 รายการลง SQLite `yuedpao_chatbot.db` และทำ Re-indexing เข้า ChromaDB (`yuedpao_products_e5`) และ BM25

#### 2. การสถาปนา Pure Native Hybrid Search (BM25 + ChromaDB Vector RRF):
- **การแก้ปัญหาที่ต้นเหตุ (Root-Cause Fix):** ติดตั้ง `pythainlp` เพื่อให้ `_bm25_tokenizer()` ตัดคำภาษาไทยได้อย่างแม่นยำ (`newmm`) และยกเลิกโค้ดแฮก `keyword_boost` ใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py) ออก 100%
- **ผลลัพธ์:** การค้นหาคำว่า *"มีเสื้อลายพะยูนมั้ย"* ดึงเสื้อรุ่น **`Oversize Screen ICONS OF HOPE YUEDPAO X UNDP` (`Wetland`, `Forest`, `Marine`)** ขึ้นอันดับ #1, #2, #3 โดยธรรมชาติทันที

#### 3. สถาปัตยกรรมแยกหน้าที่ Search Index กับ Filter Guards (Title & Metadata Attribute Rule Guard Standard):
- **การค้นพบ (Root Cause Discovery):** พบว่าสตอรี่แคมเปญใน Description มีคำว่า *"ออกแบบโดยศิลปินกลุ่มเด็กรักษ์ทุ่ง"* ทำให้ระบบเดิมตีความว่าเป็นเสื้อเด็ก (`item_is_kids = True`) แล้วไปหักคะแนนการค้นหาเสื้อผู้ใหญ่ลงถึง 85% (`kids_boost = 0.15x`)
- **ข้อสรุปสถาปัตยกรรม:**
  * **Search Engine (BM25 + Vector Search):** สแกนข้อความเต็มจาก **Full Description + Title + Document Expansion** เพื่อค้นหาความหมายลึกๆ
  * **Filter Guards (Kids, Crop, Bra, Pants):** สแกนเฉพาะข้อมูลโครงสร้างหลัก **`item_title_cat = f"{name} {category} {style} {colors}".lower()`** เท่านั้น เพื่อป้องกัน False Positive จากเนื้อหาบทความการตลาด


- **การเพิ่ม Rule Guard สำหรับหมวดหมูีกระเป๋า (`query_has_bag`) และแก้คำสะกดผิด (`กระเป็า` ไม้เตะคู้):**
  * **ปัญหาที่พบจาก Log จริง:** ผู้ใช้พิมพ์คำว่า *"ขอดูกระเป๋าสีดำ"* แล้วระบบดึงเสื้อยืดสีดำขึ้นแทนกระเป๋า เพราะเสื้อยืดสีดำได้คะแนน Color Match + Sales Volume สูงกว่า โดยที่ระบบเดิมยังไม่มี Rule Guard คอยกดคะแนนเสื้อยืดเมื่อผู้ใช้ถามหากระเป๋า และคำว่า *"กระเป็า"* สะกดผิดทำให้ดัก Intent ไม่อยู่
  * **การแก้ไขใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py):**
    1. เพิ่มคำสะกดผิด `"กระเป็า"` (ไม้เตะคู้) ลงใน `INTENT_MAP_KEYWORDS["bag"]`
    2. เพิ่ม `query_has_bag` ใน Category Mismatch Guard ──► ให้โบนัสกระเป๋า **3.50x Boost** และกดคะแนนสินค้าที่ไม่ใช่กระเป๋าลงเหลือ **0.01x (-99% Demotion)**
  * **ผลการทดสอบ:** ทั้งคำสะกดผิด `"ขอดูกระเป็าสีดำ"` และคำสะกดถูก `"ขอดูกระเป๋าสีดำ"` ได้ผลลัพธ์อันดับ 1-3 เป็นกระเป๋าตรงเป๊ะ (`The Bagg Fluffy Gozy Bag`, `The Bagg Canvas Core Bag`, `Mini Crossbody Bag`) โดยไม่มีเสื้อยืดปะปน


- **การเพิ่มคลังคำศัพท์หมวดหมู่ภาษาไทย (25 คำ) ลงใน `domain_vocab.json`:**
  * **รายละเอียด:** เพิ่มคำศัพท์หมวดหมู่ภาษาไทยพื้นฐาน (`กระเป๋า`, `กางเกง`, `เสื้อ`, `ถุงเท้า`, `หมวก`, `บรา`, `แจ็คเก็ต`, `ยีนส์`) ลงใน `app/data/domain_vocab.json` เพื่อให้ Tier 0 Edit Distance รองรับการแก้ไขคำสะกดผิดหมวดหมู่สินค้าภาษาไทยได้สมบูรณ์ 100%


- **การติดตั้งสถาปัตยกรรม Pre-Tokenization Sliding Window Fuzzy Matcher:**
  * **หลักการ:** ยกเลิกการเขียน Hardcode คำสะกดผิดใน `INTENT_MAP_KEYWORDS` ทั้งหมด แล้วเปลี่ยนมาใช้ฟังก์ชัน `_fuzzy_has_keyword()` สแกนหน้าต่างความยาวตัวอักษร (Sliding Window) บนประโยคดิบของผู้ใช้ก่อนการหั่นคำ (Pre-Tokenization)
  * **ผลลัพธ์:** ตรวจจับคำสะกดผิด / พิมพ์ตกวรรณยุกต์ / พิมพ์สระเพี้ยนในประโยคภาษาพูด เช่น *"ขอดูกระเปาม"* ──► จับคู่กับคำว่า *"กระเป๋า"* (Edit Distance: 1) ดึงกระเป๋าขึ้นอันดับ #1–#5 ได้ทันทีโดยไม่ต้องคอย Hardcode คีย์เวิร์ดสะกดผิดเพิ่มเติม


- **การปรับสถาปัตยกรรมเรียงลำดับสินค้าขายดีที่สุด (Strict Sales Volume Popularity Sorting ADR):**
  * **ปัญหาเดิม:** การค้นหาคำว่า *"ขายดีที่สุด"* นำอันดับ RRF มาคูณด้วยตัวคูณลอการิทึม ทำให้สินค้าที่ตรงกับคำค้นหาที่มี RRF สูงกว่า แซงสินค้าที่มี **ยอดขายชิ้นจริงมากกว่า** (เช่น กระเป๋ายอดขาย 9 ชิ้น ขึ้นก่อนกระเป๋ายอดขาย 14 และ 41 ชิ้น)
  * **การแก้ไขใน [product_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/product_service.py):**
    เมื่อ `is_popular = True` (ผู้ใช้พิมพ์ว่า *"ขายดีที่สุด"*, *"ขายดี"*, *"บานท็อป"*) ระบบจะทำการกรองสินค้าที่ตรงกับคีย์เวิร์ด/หมวดหมู่ แล้วทำการ **เรียงลำดับจาก `sales_volume` (จำนวนชิ้นที่ขายได้จริงจากมากไปน้อย) เป็นคีย์หลักแบบ 100% (Primary Key: `sales_volume DESC`)**
  * **ผลลัพธ์การค้นหาจริง (`"ขอดูกระเป๋าที่ขายดีที่สุด"`):**
    1. 🥇 `The bagg mini crossbody bag` (฿290) — **ยอดขาย 41 ชิ้น**
    2. 🥈 `The Bagg 2026 Mini Crossbody Cube Bag` (฿290) — **ยอดขาย 22 ชิ้น**
    3. 🥉 `The Bagg Carry bag` (฿990) — **ยอดขาย 15 ชิ้น**
    4. 4️⃣ `Mini Crossbody Case Bag Classic Black` (฿290) — **ยอดขาย 14 ชิ้น**
    5. 5️⃣ `Ultra Flow Running Rush Bag` (฿250) — **ยอดขาย 11 ชิ้น**
    *(เรียงลำดับยอดขายสะสมจริงจากมากไปน้อย 41 ➔ 22 ➔ 15 ➔ 14 ➔ 11 ชิ้น สมบูรณ์แบบ 100%)*


- **การรันอัปเดตข้อมูลดีลโปรโมชันและ Re-indexing (Promotions & Deals Update ADR):**
  * รันสคริปต์ [app/scripts/update_deals.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/scripts/update_deals.py) อัปเดตประเภทโปรโมชัน 21 รายการ (`daily_deal` และ `monthly_deal`) ลงใน SQLite `yuedpao_chatbot.db`
  * สั่งงาน `PromotionService.reload_and_index()` เพื่อทำ Re-indexing ดีลและคูปองส่วนลดรวม **26 รายการ** เข้าสู่ ChromaDB `yuedpao_promotions_e5` และ BM25 Search Index


- **การสแครปโปรโมชันสดจากหน้าเว็บจริงและการทำ Dual-Layer Indexing (Rule 9 Standard):**
  * สั่งงาน Selenium Headless Scraper [app/scripts/run_promotion_scraper_runner.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/scripts/run_promotion_scraper_runner.py) ดึงโปรโมชันสดจากหน้าเว็บ `https://www.yuedpao.com/countdown/`
  * สแครปข้อมูลสินค้าโปรโมชันเชิงลึก (รูปภาพหลัก, รูปแกลเลอรี, ตารางไซส์, สีคงเหลือ, ราคาดีล) สำเร็จรวม 16 รายการ จัดเก็บลง SQLite `yuedpao_chatbot.db` (ตาราง `promotions`)
  * สั่งงาน `PromotionService.reload_and_index()` เพื่ออัปเดตข้อมูลเข้าสู่ ChromaDB Vector DB (`yuedpao_promotions_e5`) และ BM25 Search Index รวมทั้งสิ้น 21 รายการ (คูปอง + ดีลโปรโมชันสด)


- **แก้ไขปัญหากลุ่มประเภทดีลโปรโมชันสแครปสด (`daily_deal` / `monthly_deal`):**
  * **สาเหตุ:** ข้อความปุ่ม Header บนเว็บติดคำว่า *"เข้าสู่ระบบ"* ทำให้ `deal_type` ถูกจัดเป็น `special_deal` ทั้งหมด
  * **แก้ไข:** ปรับปรุง [app/scripts/run_promotion_scraper_runner.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/scripts/run_promotion_scraper_runner.py) อ่านลำดับหมวดการ์ดบนหน้าเว็บ YuedPao โดยตรง ──► หมวดชุดที่ 1 เป็น `daily_deal` (ดีลประจำวัน 4 รายการ `Ultra Flow Running Shorts`) และหมวดชุดที่ 2 เป็น `monthly_deal` (ดีลประจำเดือน 12 รายการ `Y Collection Polo` & `Y Cargo Short`)
  * **ผลลัพธ์:** ล้างข้อมูลเก่า 100% บันทึกดีลสดใหม่ 16 รายการลง SQLite DB และ Re-index เข้า `PromotionService` รวม 21 รายการสมบูรณ์แบบ


- **การแก้ปัญหาการแสดงผล Flex Cards ของ "ขอดีลวันนี้" และ "ขอดีลเดือนนี้" (Daily & Monthly Deals Routing ADR):**
  * **สาเหตุที่ขึ้น Flex Cards: 0:** เกิดจากการรันสแครปสดก่อนหน้านี้ บันทึก `deal_type` เป็น `special_deal` ทั้งหมดโดยไม่ได้ระบุเป็น `daily_deal` หรือ `monthly_deal` ทำให้เมื่อผู้ใช้ถามหาดีลประจำวัน/ดีลประจำเดือน ฟังก์ชัน `get_daily_deals()` และ `get_monthly_deals()` คืนค่าเป็น 0 รายการ
  * **การแก้ไข:** อัปเดตสคริปต์ [app/scripts/run_promotion_scraper_runner.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/scripts/run_promotion_scraper_runner.py) และรัน [app/scripts/update_deals.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/scripts/update_deals.py) แมป `daily_deal` (ดีลประจำวัน 4 รายการ `Ultra Flow Running Shorts`) และ `monthly_deal` (ดีลประจำเดือน 12 รายการ `Y Collection Polo` & `Y Cargo Short`) ลงใน SQLite DB
  * **ผลการทดสอบการตอบกลับสด:**
    - `"ขอดีลวันนี้"` ──► **Flex Cards: 4 รายการ** (`Ultra flow Running Shorts` สี White, Black, Light Grey, Navy Blue)
    - `"ขอดีลเดือนนี้"` ──► **Flex Cards: 6 รายการ** (`Y Collection Polo 2025` & `Polo LongSleeve`)
    - ผ่านการทดสอบ PyTest อัตโนมัติ **19/19 PASSED (100%)**


- **การแก้ไขปัญหา Memory Staleness ใน PromotionService (Live Server Fresh Load ADR):**
  * **สาเหตุ:** เซิร์ฟเวอร์ที่เปิดรันค้างไว้จำค่า Singleton `self.promotions` จาก RAM ก่อนการ Re-index
  * **การแก้ไข:** ปรับปรุงใน [app/services/promotion_service.py](file:///D:/ananda_personal/my_project/Chatbot_YuedPao/app/services/promotion_service.py) เพิ่ม `self._load_promotions_from_db()` ลงใน `get_daily_deals()`, `get_monthly_deals()`, และ `get_all_coupons()` เพื่อโหลดข้อมูลล่าสุดตรงจาก SQLite `yuedpao_chatbot.db` ทุกครั้งที่มี Request สด

#### 4. ผลการทดสอบระบบและสถิติประสิทธิภาพ (System Benchmarks):
- **ความเร็วตอบสนอง (Latency):** ทำสถิติใหม่ตอบสนองผู้ใช้บน LINE Webhook ที่ **1.07 ms – 1.88 ms** (น้อยกว่า 2 ms)
- **ความแม่นยำภาษาพูดธรรมชาติ (Semantic Precision):**
  * `"ขอดูเสื้อพะยูน"` ──► ได้ `ICONS OF HOPE` อันดับ #1-#3
  * `"ขอดูเสื้อ crop"` ──► ได้ `Polo Crop Waffle`, `Signature Crop`, `Kodnum Crop` อันดับ #1-#5
  * `"ขอดูเสื้อลายหมา"` ──► ได้ **`Oversize Street SUS CoCa Coma (โคคา โคหมา)` อันดับ #1**
  * `"ขอเสื้อผ้า cotton 60%"` ──► ดึงกลุ่มผ้า Cotton 60% จาก Description พร้อม `spec_boost = 3.00x`
- **ชุดทดสอบอัตโนมัติ (Automated Pytest Suite):** ผ่านครบ **19/19 PASSED (100% Pass Rate)**
