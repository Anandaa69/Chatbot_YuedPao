---
title: Core Features & Rich Menu Specification
date: 2026-08-23
tags: [features, rich-menu, line-bot, UX, o2o, liff]
sources: ["sources/ออกแบบฟังก์ชัน LINE Chatbot สำหรับ Yuedpao.md"]
---

# 📱 Core Features & Rich Menu Specification

Backlink: [[index]]

---

## 📌 Rich Menu Layout (6-Grid Standard)

The LINE Official Account Rich Menu serves as the main navigation hub. It uses a standard 6-tile grid layout (2 rows $\times$ 3 columns).

| Tile Position | Title | Postback Payload / Action | Core Target Feature |
|---|---|---|---|
| **Grid 1 (Top-Left)** | **แนะนำไซส์ & รุ่นเสื้อ** | `action=smart_fitting` | Smart Fitting & Fabric Guide |
| **Grid 2 (Top-Middle)** | **แคตตาล็อก & โปรโมชัน** | `action=shopping_promo` | Product Catalog & Flash Sales |
| **Grid 3 (Top-Right)** | **เช็กสาขาใกล้บ้าน** | `action=store_locator` | O2O Store Locator & Geolocation |
| **Grid 4 (Bottom-Left)** | **สมาชิก & ส่วนลด** | `action=crm_liff` | CRM Loyalty & LIFF Registration |
| **Grid 5 (Bottom-Middle)** | **ติดตามพัสดุ / เคลมสินค้า** | `action=after_sales` | Order Tracking & Defect Claim |
| **Grid 6 (Bottom-Right)** | **ติดต่อแอดมิน** | `action=live_agent` | Live Agent Handover & Tagging |

---

## ⚙️ Detailed Breakdown of 6 Core Features

### ① ระบบผู้ช่วยเลือกเนื้อผ้าและแนะนำไซส์ (Smart Fitting & Fabric Guide)
Addresses customer hesitancy regarding clothing size and fabric feel.
- **Size Recommendation Bot**: Users input `Height (cm)` + `Weight (kg)` or `Chest Circumference (inches)`. The bot calculates ideal sizing across **Unisex**, **Oversized**, **Crop**, or **Kids** styles and renders an image table of exact size specs.
- **Interactive Fabric Guide**: 1-click comparison of Yuedpao's signature fabric innovations:
  - *Non-iron*: Wash, shake, dry, wear immediately without ironing.
  - *Ultrasoft*: Premium soft touch, ultra-breathable, available in Crewneck & V-neck.
  - *Tailor Cool Polo*: Professional polo look with active heat dissipation.
  - *MotionSkin / Ultra Flow*: High-flex 4-way stretch activewear, quick-dry.

---

### ② แคตตาล็อกสินค้า & โปรโมชัน (Shopping & Promotions)
- **Category Browsing**: Filtered sub-categories: เสื้อยืด (คอกลม/คอวี/Oversize), โปโล, เสื้อเชิ้ต/ลูกฟูก, กางเกง (ยีนส์/Cargo), ชุดกีฬา MotionSkin, กางเกงใน Unwear.
- **Flash Sale & Monthly Deals**: Carousel of discount cards pulled from web promotions.
- **Direct Checkout**: Links lead directly to Yuedpao.com product pages or LINE SHOPPING checkout.

---

### ③ ค้นหาสาขาหน้าร้าน (Store Locator - O2O)
- **LINE Location Sharing**: User presses "Send Location" within LINE.
- **Nearby Branch Engine**: System calculates Haversine distance to Yuedpao shopping mall branches, returning the 3 nearest branches, operating hours, stock status, and Google Maps links.

---

### ④ บริการหลังการขาย & เคลมสินค้า (After-Sales & Self-Service)
- **Order Tracking**: User inputs `Order ID` or `Phone Number` $\rightarrow$ System fetches shipment status and direct tracking carrier URLs.
- **Defective Item / Exchange Form**: Guided flow for size exchanges (within warranty period with tags intact). Supports uploading photo evidence of defective items for automated claim filing.

---

### ⑤ ระบบสมาชิก & สะสมแต้ม (CRM & Loyalty Program)
- **LINE LIFF Registration**: 1-click account creation leveraging LINE UID and phone number authentication.
- **Reward Points & Birthday Perks**: Check point balances, redeem discount coupons, and claim birthday promotions.

---

### ⑥ ระบบส่งต่อแอดมิน (Live Agent Handover)
- **Pre-handover Categorization**: Users select topic:
  - `[สอบถามการสั่งซื้อ]` (Order Inquiry)
  - `[แจ้งปัญหาเปลี่ยนสินค้า]` (Exchange Request)
  - `[สั่งผลิต B2B / เสื้อองค์กร]` (Corporate Wholesale B2B)
- Tags cases automatically and routes conversation to the correct support desk.

---

## 💬 Sample Automated Intent Conversation

```text
[User]     : สนใจเสื้อยืด แต่ไม่แน่ใจเรื่องเนื้อผ้า
[Chatbot]  : ยืดเปล่ามีเนื้อผ้าหลัก 3 สไตล์ให้เลือกครับ:
             1. Non-iron (ไม่ต้องรีด ซักสะบัดใส่ได้เลย)
             2. Ultrasoft (เน้นนุ่ม เบาสบาย เหมาะกับวันชิลๆ)
             3. Tailor Cool (เนื้อผ้าเรียบหรู อยู่ทรง ดูดี)
             👉 [ดูเปรียบเทียบผ้า]  [ช่วยเลือกไซส์]  [สั่งซื้อเลย]
```

---

## 🔗 Related Knowledge Pages
- [[architecture-tiered-router]] — Routing payloads from Rich Menu buttons.
- [[carousel-randomization]] — Flex Message design guidelines for promo & catalog cards.
- [[database-schema]] — Tables storing store locations, orders, and user points.
