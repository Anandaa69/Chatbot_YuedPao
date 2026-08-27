---
title: Product Catalog Scraping & Data Pipeline Specs
date: 2026-08-23
tags: [scraping, data-pipeline, yuedpao, catalog, domain-vocabulary]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 🕷️ Product Catalog Scraping & Data Pipeline Specs

Backlink: [[index]]

---

## 📌 Data Pipeline Rationale

> [!CAUTION]
> **Never run scrapers synchronously in real-time when a user sends a chat message.** Real-time scraping introduces network delay (2–5 seconds) and risks failing if the Yuedpao website structure changes dynamically.

Scraping is executed as an **offline background batch process** (Daily/Weekly cron job). Cleaned scraped data is populated directly into the [[database-schema|SQLite / Supabase Database]].

---

## 📦 5 Scraped Data Targets

### 1. Product Catalog (Product Details)
- **SKU / Product Name**: Unique product identifier (e.g. `Tailor Cool Polo Innovation`, `Ultra Flow Short`).
- **Category Hierarchy**:
  - เสื้อยืด (คอกลม / คอวี / Oversize)
  - เสื้อเชิ้ต / ลูกฟูก
  - กางเกง (ยีนส์ / Cargo)
  - ชุดกีฬา (MotionSkin / Ultra Flow)
  - กางเกงใน (Unwear)
- **Pricing & Discounts**: Full price, discounted promo price, discount percentage.
- **Product Variants**:
  - Color names & Hex/Palette (e.g. `Classic Navy #1B263B`, `Dark Moss #354F52`, `Coffee Brown #4A3B32`, `Amber Wood`, `Shadow Gray`, `Salmon Rose`, `Cha Thai`).
  - Available Sizes (`XS`, `S`, `M`, `L`, `XL`, `2XL`, `3XL`).
  - Stock Status (`In-Stock` vs `Out-of-Stock`).
- **Media & Links**: Primary image URL, detail model image URLs, direct checkout URL.

---

### 2. Fabric & Material Specifications
- **Fabric Collections**: Non-iron, Ultrasoft, Tailor Cool, MotionSkin, Feather Comfort.
- **Key Features & USPs**: Wrinkle-free, ultra-soft touch, 4-way stretch, moisture-wicking.
- **Size Charts**: Chest width (inches/cm), Shirt length, Waist circumference, Sleeve length. ดึงลิงก์รูปภาพตารางไซส์สินค้าแต่ละประเภท (ดึงจากแท็ก `img` ที่มีคลาส `mpe-no-image-placeholder` และ URL จะอยู่ภายใต้รูปแบบ `/physical/[product_id]/image/[image_id]` เช่น `https://mp-static.yuedpao.com/physical/.../image/...`)

---

### 3. FAQ & Customer Service Policies
- **After-Sales Policy**: Size exchange rules, return window (e.g. within 7 days with tags attached).
- **Shipping Info**: Standard delivery time, shipping rates, free shipping thresholds.
- **Care Instructions**: Washing machine settings, ironing rules (e.g. do not iron non-iron series), tumble dry warnings.

---

### 4. Physical Store Locations (O2O Store Locator)
- **Branch Name**: Mall name & floor (e.g. `Central WestGate 2nd Floor`, `The Mall Bangkapi`).
- **Geolocation**: Latitude and Longitude coordinates.
- **Google Maps Link**: Direct navigation URL (`https://maps.google.com/?q=...`).
- **Operating Hours & Phone**: Mall opening/closing times (e.g. `10:00 - 22:00`), branch phone number.

---

### 5. Domain Vocabulary Dictionary

The Scraper builds an explicit **Domain Vocabulary Dictionary** used by the [[nlp-spelling-correction|NLP Edit Distance Engine]]:

```json
{
  "brand_colors": ["Amber Wood", "Shadow Gray", "Salmon Rose", "Cha Thai", "Classic Navy", "Dark Moss", "Coffee Brown"],
  "product_styles": ["Oversize", "Crop", "Unisex", "Cargo", "Boxer Briefs", "Crewneck", "V-Neck"],
  "fabric_technologies": ["Non-iron", "Ultrasoft", "Tailor Cool", "MotionSkin", "Ultra Flow", "Feather Comfort"],
  "apparel_types": ["เสื้อยืด", "เสื้อเชิ้ต", "โปโล", "กางเกงยีนส์", "ชุดกีฬา", "กางเกงใน"]
}
```

---

## 🛠️ Data Pipeline Robustness Rules

1. **Rate Limiting & Anti-Blocking**: Include `time.sleep(1.0 - 2.0)` between requests and rotate User-Agent headers.
2. **Data Cleaning & Normalization**:
   - Strip leading/trailing whitespaces (`.strip()`).
   - Remove special HTML characters and unescape HTML entities.
   - Convert prices to integer values (`"450 บาท"` $\rightarrow$ `450`).
3. **Graceful Fallbacks**:
   - Wrap element parsing in `try-except` blocks.
   - Fall back missing image URLs to a default Yuedpao placeholder image (`/assets/images/yuedpao_placeholder.png`).
   - Set missing price values to `-1` to flag for audit.

---

## 📅 Scraping Strategy & Stock Availability Spec

### 1. ความจริงของระบบ Chatbot (Chatbot as a Showroom & Finder)
* **ค้นหา & แนะนำสินค้าเท่านั้น**: Chatbot ทำหน้าที่ในการแนะนำสินค้า (Product Discovery) และค้นหาสินค้าที่เหมาะสม ไม่ใช่ระบบตัวตัดสต็อกแบบเรียลไทม์ (Real-time Checkout)
* **ส่งต่อไปยังหน้าเว็บจริง**: ปลายทางของปุ่มสั่งซื้อในการ์ดสินค้า (Carousel / Flex Message) จะเป็น **Direct URL** เพื่อนำลูกค้าเข้าสู่ระบบสั่งชื้อและชำระเงินของเว็บไซต์ Yuedpao โดยตรง ซึ่งจะไปตัดสต็อกจริงและระบุไซส์/สีในระบบเว็บบอร์ดของ Yuedpao อยู่แล้ว
* **หลีกเลี่ยง Real-time Scraping**: ห้ามทำการยิง Scrape หน้าเว็บ Yuedpao ทุกครั้งที่ลูกค้ากดคุยเด็ดขาด เนื่องจากจะส่งผลให้:
  - ค่า Latency ช้าเกินความเร็วที่กำหนด (ต้อง < 1.5–2 วินาที แต่ Real-time Scrape จะใช้เวลา 3–10 วินาที)
  - เสี่ยงต่อการโดน Web Server ของ Yuedpao บล็อก IP (HTTP 429 Too Many Requests)

### 2. ความถี่ในการอัปเดตข้อมูล (Scraping Schedule)
การอัปเดตข้อมูลสินค้าจะแบ่งออกเป็น 2 ระดับหลัก:
1. **Batch Scheduled Scrape (แนะนำ)**: รันอัตโนมัติวันละ 1 ครั้ง (ช่วงเวลาตี 2 – ตี 4) หรือทุกๆ 6–12 ชั่วโมงโดยใช้ Cron Job / GitHub Actions / Celery เพื่อทำการ:
   - เพิ่มสินค้าชิ้นใหม่ / ตรวจสอบและลบสินค้าที่เลิกจำหน่าย
   - ตรวจเช็กสถานะการสต็อกสินค้าทั่วไป (`is_available` หรือ `is_in_stock`)
   - อัปเดตราคาสินค้าช่วง Flash Sale
2. **Triggered / Manual Scrape**: รันแบบสั่งการด้วยตัวเองผ่าน Terminal / CLI เมื่อมีการทดสอบระบบหรือการแก้ไขโค้ดฝั่ง Scraper

### 3. การออกแบบฐานข้อมูลและการเก็บข้อมูล (Data Storage & Caching)
* **Master Dataset**: ข้อมูลที่ดึงได้จะถูกแปลงและบันทึกเป็น `products.json` หรือ SQLite Database ในเครื่อง
* **Fast Caching**: โหลดข้อมูลทั้งหมดขึ้นมาเก็บใน Memory / Cache (เช่น `redis` หรือ Local Memory dict) ทันทีที่ระบบ Chatbot ทำการ Start-up เพื่อช่วยให้ขั้นตอนการประมวลผล NLP & Product Randomizer ทำงานได้รวดเร็วขึ้นในระดับ **< 50 ms**
* **ฟิลด์ตรวจสอบสต็อกและการดักจับสินค้าหมด (`is_available`)**:
  * **Authoritative Guard Rule**: ตรวจเช็กเจาะจงเฉพาะ Tag หัวเรื่องหลัก `<h4 ...>สินค้าหมด</h4>` (หรือ `<h5 ...>สินค้าหมด</h5>`) ด้านบนสินค้าเท่านั้น เพื่อป้องกันปัญหาจากคำว่า `"สินค้าหมด"` ในโซน *"สินค้าที่คุณอาจชอบ"* (Footer Carousel) ด้านล่างเว็บ:
    ```python
    out_of_stock_h4 = soup.find(lambda tag: tag.name in ["h4", "h5"] and "สินค้าหมด" in tag.get_text())
    is_available = (out_of_stock_h4 is None)
    ```
* **การสั่งรันบังคับ Re-Scrape**: คำสั่งรัน Scraper อัปเดตข้อมูลทั้งหมดใหม่ทับฐานข้อมูลเดิม:
  ```powershell
  python -m app.scripts.run_scraper --all --force
  ```

### 4. การจัดการ Chat UX บน LINE Chatbot กรณีสินค้าหมด (Graceful Fallback)
เพื่อป้องกันความสับสนของลูกค้าและเพิ่มคะแนน UX การนำเสนอสินค้าต้องใช้เทคนิคดังนี้:
* **การกรองข้อมูลตอนสุ่ม**: กรองสินค้าที่หมดออกก่อนนำมาแนะนำลูกค้าเสมอ:
  ```sql
  SELECT * FROM products 
  WHERE category = 'oversize' AND is_available = 1 
  ORDER BY RANDOM() LIMIT 5;
  ```
* **ใส่ Micro-copy กากับไว้ใต้ภาพ**: ใส่ตัวอักษรเล็กๆ สีเทาใต้การ์ดสินค้า เช่น *"⚡ เช็กสต็อกและขนาดล่าสุดได้ที่หน้าสั่งซื้อ"*
* **ปุ่มลิงก์สั่งซื้อที่ชัดเจน**: กำหนดข้อความบนปุ่มเป็น `"สั่งซื้อบนเว็บ"` หรือ `"ดูรายละเอียด / สั่งซื้อ"` แทนการใช้คำว่า "ซื้อทันที" เพื่อสร้างความเข้าใจที่ถูกต้องแก่ผู้ใช้ว่าการทำรายการสุดท้ายจะทำผ่านบราว์เซอร์จริง
* **Graceful Fallback**: เมื่อลูกค้าเข้าสู่หน้าเว็บจริง หากสินค้านั้นๆ หมด ระบบหน้าเว็บดั้งเดิมของ Yuedpao จะแนะนำรุ่นอื่นๆ ที่ใกล้เคียงให้กับลูกค้าทดแทนได้ทันที

---

## 🔗 Related Knowledge Pages
- [[nlp-spelling-correction]] — Utilizing the Scraped Domain Vocabulary for spelling correction.
- [[database-schema]] — Database tables where scraped data is saved.
- [[rubric-evaluation-checkpoints]] — Evaluation criteria for the scraping pipeline (25%).
