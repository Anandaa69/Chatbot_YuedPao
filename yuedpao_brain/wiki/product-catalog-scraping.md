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
- **Size Charts**: Chest width (inches/cm), Shirt length, Waist circumference, Sleeve length.

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

## 🔗 Related Knowledge Pages
- [[nlp-spelling-correction]] — Utilizing the Scraped Domain Vocabulary for spelling correction.
- [[database-schema]] — Database tables where scraped data is saved.
- [[rubric-evaluation-checkpoints]] — Evaluation criteria for the scraping pipeline (25%).
