# 👕 Chatbot YuedPao (ยืดเปล่า แชตบอต)
> **AI-Powered LINE E-Commerce Chatbot for YuedPao Brand**  
> ขับเคลื่อนด้วย **4-Tier Thai NLP Intent Engine**, **Soundex & Kedmanee Keyboard Typo Resilience**, และ **Two-Pass Hybrid Product Retrieval (BM25 + ChromaDB Vector RRF)**

---

## 📌 บทนำและภาพรวมโปรเจกต์ (Project Overview)

**Chatbot YuedPao** เป็นระบบแชตบอตสนทนาและค้นหาสินค้าอัตโนมัติบนแพลตฟอร์ม **LINE Official Account (LINE Messaging API v3)** สำหรับแบรนด์เสื้อผ้า *YuedPao (ยืดเปล่า)* 

ระบบถูกออกแบบด้วยสถาปัตยกรรมระดับ **Production-Ready (Layered Architecture & Separation of Concerns)** เพื่อรองรับการสื่อสารภาษาไทยที่เป็นธรรมชาติ เข้าใจการพิมพ์ผิด (Typo & Slang), ค้นหาสินค้าตามสเปกและสัมผัสเนื้อผ้าแบบ Semantic Search, แนะนำโปรโมชัน/คูปองส่วนลดแบบ Real-time, และตอบสนองได้อย่างรวดเร็วในระดับ **Milliseconds (< 5 ms)**

---

## 🌟 ฟีเจอร์เด่นของระบบ (Key Features)

1. **4-Tier Hierarchical Intent Pipeline (การจำแนกเจตนา 4 ระดับ):**
   - **Tier 0 (Spell & Clean):** แก้ไขคำผิดด้วย **Domain Vocab (~375 คำศัพท์แบรนด์)**, **Thai Soundex (LK82)**, และ **Kedmanee 4-Row Keyboard Distance Matrix**
   - **Tier 1 (Priority Rules):** จับคำถามสำคัญ (งบประมาณ, เทียบเนื้อผ้า, ตารางไซส์, ทักทาย) ด้วย Regex กฎความสำคัญสูง (< 1 ms)
   - **Tier 2.5 (ChromaDB Few-Shot Vector Lookup):** เปรียบเทียบความหมายกับ Ground Truth 136 ตัวอย่างแบบ Cosine Similarity ($\ge 0.70$)
   - **Tier 3 (BERT E5 Fallback):** จำแนกเจตนาขั้นสูงด้วยโมเดล `intfloat/multilingual-e5-small`

2. **Two-Pass Hybrid Product Retrieval (ระบบค้นหาสินค้าไฮบริด 2 ชั้น):**
   - ผสานการค้นหาแบบ **Exact Keyword Matching (BM25)** และ **Natural Language Semantic Search (ChromaDB Vector)**
   - รวมคะแนนและจัดอันดับด้วยอัลกอริทึม **Reciprocal Rank Fusion (RRF)**
   - **Two-Pass Query Relaxation:** หากผู้ใช้พิมพ์ผิดรุนแรงจน Pass 1 (Raw Query) ไม่พบสินค้า ระบบจะสลับไปค้นหา Pass 2 ด้วยคำที่ผ่านการแก้ไข (Corrected Query) ให้อัตโนมัติ

3. **LINE Flex UI & Quick Replies:**
   - แสดงการ์ดสินค้าแบบ **Flex Carousel** สวยงาม คัดกรองเฉพาะสินค้าที่มีในสต็อก (`is_available = 1`)
   - แสดงการ์ดคูปองโปรโมชันพร้อมปุ่ม **`📋 คัดลอกโค้ด` (Clipboard Action)** กดก๊อปปี้รหัสส่วนลดลงคลิปบอร์ดได้ทันที
   - ปุ่ม **Quick Replies อัจฉริยะ** นำทางผู้ใช้ไปยังคำถามที่เกี่ยวข้อง

4. **High Performance & Low Memory Footprint:**
   - ใช้ **Singleton Model Loader** โหลดโมเดล SentenceTransformer เพียง 1 ครั้งตอนบูต ประหยัด RAM กว่า 1 GB+
   - ประมวลผลลัพธ์คำถามรวดเร็วเฉลี่ย **~0.5 - 4.0 ms**

---

## 🏗️ สถาปัตยกรรมระบบ (System Architecture)

```
                       [ LINE User ]
                             │
                             ▼ (HTTPS Webhook)
                   [ Cloudflare Tunnel ]
                             │
                             ▼ (Port 5000)
             [ app.controllers.webhook_controller ] ◄── Signature Verification
                             │
                             ▼
               [ app.services.tiered_router ]
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
[ IntentService (NLP) ]                 [ ProductService / PromotionService ]
  - Tier 0: Soundex + Spell Matrix        - Pass 1: Raw Query Hybrid (BM25 + ChromaDB)
  - Tier 1: Priority Rules                - Pass 2: Query Relaxation Fallback
  - Tier 2.5: ChromaDB Few-Shot           - RRF Fusion Scoring
  - Tier 3: Multilingual-E5-Small         - Strict Category & Demographic Filters
         │                                       │
         └───────────────────┬───────────────────┘
                             ▼
               [ app.views.flex_carousel ] ◄── LINE Flex & Quick Replies
                             │
                             ▼ (LINE Messaging API v3)
                       [ LINE User ]
```

---

## 📁 โครงสร้างโฟลเดอร์โปรเจกต์ (Project Structure)

```text
Chatbot_YuedPao/
├── app/                          # 📁 Application Source Code (Stateless)
│   ├── config.py                 # จัดการ Config และโหลด Environment (.env)
│   ├── main.py                   # Entrypoint เซิร์ฟเวอร์ Flask Webhook
│   ├── controllers/
│   │   └── webhook_controller.py # จัดการ Endpoint /callback และตรวจสอบ Signature
│   ├── models/
│   │   ├── product.py            # Data Model ของสินค้าและตัวเลือกสินค้า
│   │   └── session.py            # Data Model สำหรับเก็บสถานะบทสนทนา
│   ├── services/
│   │   ├── intent_service.py     # 4-Tier Intent Engine + Soundex + Edit Distance
│   │   ├── product_service.py    # Two-Pass Hybrid RRF Search Engine
│   │   ├── promotion_service.py  # บริการข้อมูลโปรโมชันและคูปองส่วนลด
│   │   ├── scraper_service.py    # Service สำหรับสแครปข้อมูลเว็บ YuedPao
│   │   └── tiered_router.py      # ตัวควบคุม Flow การตัดสินใจส่วนกลาง (Central Router)
│   ├── utils/
│   │   └── model_loader.py       # Thread-safe Singleton Shared Embedding Model
│   ├── views/
│   │   ├── flex_carousel.py      # สร้าง LINE Flex Carousel (สินค้า / คูปอง)
│   │   ├── flex_fabric.py        # สร้างการ์ดเทียบคุณสมบัติเนื้อผ้า & ตารางไซส์
│   │   ├── quick_replies.py      # สร้างปุ่ม Quick Reply นำทาง
│   │   └── rich_menu_views.py    # แมป Action จากการกด Rich Menu
│   ├── scripts/
│   │   ├── run_scraper.py        # CLI สแครปข้อมูลสินค้าเข้า Database
│   │   └── run_promotion_scraper_runner.py
│   └── data/                     # 📄 Static JSON Config (Read-Only)
│       ├── domain_vocab.json     # พจนานุกรมศัพท์เฉพาะแบรนด์สำหรับแก้คำผิด
│       └── nlp_ground_truth.json # ข้อมูล Few-Shot สำหรับแยก Intent
│
├── data/                         # 💾 Persistent Data Layer (Stateful - นอก app/)
│   ├── yuedpao_chatbot.db        # 🗄️ ฐานข้อมูล SQLite (สินค้า, คูปอง, โปรโมชัน)
│   └── chroma/                   # 🧠 เวกเตอร์ Embeddings (Few-shot, Products, Promos)
│
├── notebooks/                    # 📓 สมุดบันทึกการวิจัยและการทดลอง NLP
│   └── intent_rank/              # การทดลอง BM25, RRF, BERT, และ QA Benchmarks
│
├── tests/                        # 🧪 Automated Test Suite (44 Tests, 100% Pass)
│   ├── test_all_intents.py
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_typo_resilience.py
│   ├── test_views.py
│   └── test_webhook.py
│
├── .env                          # 🔑 ไฟล์เก็บค่า Secrets (ห้ามนำขึ้น Git)
├── .env.example                  # ตัวอย่างการตั้งค่า Environment Variables
├── pyproject.toml                # การจัดการ Dependencies และโปรเจกต์ด้วย Poetry
├── poetry.lock                   # Lockfile ของ Dependencies ทั้งหมด
└── README.md                     # เอกสารคู่มือโปรเจกต์
```

---

## 💻 ความต้องการของระบบ (System Prerequisites)

- **Python:** เวอร์ชัน `3.11` ขึ้นไป
- **Poetry:** เครื่องมือจัดการแพ็กเกจและ Dependencies ([ติดตั้ง Poetry](https://python-poetry.org/docs/#installation))
- **LINE Official Account:** บัญชี LINE Official Account พร้อมเปิดใช้งาน **Messaging API** จาก [LINE Developers Console](https://developers.line.biz/)
- **Tunneling Tool:** [Cloudflare Tunnel (`cloudflared`)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) หรือ [ngrok](https://ngrok.com/) สำหรับ Forward พอร์ตเครื่อง Local ออกสู่ Internet

---

## 🚀 ขั้นตอนการติดตั้งและการรันระบบ (Step-by-Step Setup Guide with Poetry)

### 1. ติดตั้ง Dependencies ด้วย Poetry

Poetry จะสร้าง Virtual Environment และติดตั้งไลบรารีทั้งหมดให้โดยอัตโนมัติ:

```bash
# 1. เข้าสู่โฟลเดอร์โปรเจกต์
cd Chatbot_YuedPao

# 2. ติดตั้ง Dependencies ทั้งหมดผ่าน Poetry
poetry install
```

---

### 2. ตั้งค่า Environment Variables (`.env`)

คัดลอกไฟล์ `.env.example` เป็น `.env`:

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

จากนั้นเปิดไฟล์ `.env` และกรอก **LINE Keys** ที่ได้จาก LINE Developers Console:

```env
# LINE Messaging API Credentials
LINE_CHANNEL_SECRET=ใส่_Channel_Secret_ของคุณที่นี่
LINE_CHANNEL_ACCESS_TOKEN=ใส่_Channel_Access_Token_ของคุณที่นี่

# Database Path
DATABASE_URL=sqlite:///./data/yuedpao_chatbot.db
ENVIRONMENT=development
PORT=5000
HOST=0.0.0.0
```

---

### 3. รันเซิร์ฟเวอร์ Webhook (Run Application)

คุณสามารถรันเซิร์ฟเวอร์ผ่านคำสั่ง `poetry run`:

```bash
# รัน Webhook Server ด้วย Poetry
poetry run python app/main.py

# หรือเข้าสู่ Shell ของ Poetry ก่อน แล้วค่อยสั่งรัน:
# poetry shell
# python app/main.py
```

เมื่อเซิร์ฟเวอร์ทำงานสำเร็จ จะแสดงข้อความ:
```text
Loading weights: 100%|██████████| 199/199
 * Serving Flask app 'main'
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

---

### 4. เปิด Cloudflare Tunnel เชื่อมต่อไปยัง LINE Webhook

เปิดหน้าต่าง Terminal ใหม่อีก 1 หน้าต่าง แล้วรันคำสั่ง **Cloudflare Tunnel**:

```bash
cloudflared tunnel --url http://127.0.0.1:5000
```

*(หรือหากใช้ ngrok: `ngrok http 5000`)*

ระบบจะสร้าง URL สาธารณะแบบ HTTPS ให้ เช่น:
```text
https://random-subdomain.trycloudflare.com
```

---

### 5. ตั้งค่า Webhook URL ใน LINE Developers Console

1. เข้าไปที่ [LINE Developers Console](https://developers.line.biz/) ➔ เลือก Channel ของคุณ
2. ไปที่แท็บ **Messaging API** ➔ หัวข้อ **Webhook settings**
3. กรอก **Webhook URL** โดยนำ URL จาก Cloudflare มาต่อท้ายด้วย `/callback` เช่น:
   ```text
   https://random-subdomain.trycloudflare.com/callback
   ```
4. กดปุ่ม **Update** แล้วกด **Verify** (ต้องขึ้นสถานะ `Success`)
5. **เปิดใช้งานสวิตช์ "Use Webhook" เป็น ON**
6. เปิดแอป LINE บนมือถือ แล้วเริ่มส่งข้อความคุยกับแชตบอตได้ทันที! 💬✨

---

## 🧪 การรันชุดทดสอบความถูกต้อง (Automated Testing)

โปรเจกต์มีชุดทดสอบอัตโนมัติครอบคลุมทุกโมดูล (NLP Intent, Database Models, Hybrid Search, Two-Pass Typo, Flex UI, Webhook Callback):

```bash
# รันชุดทดสอบ Pytest ผ่าน Poetry
poetry run pytest

# หรือหากอยู่ใน Virtual Environment
# python -m pytest
```

**ผลลัพธ์การทดสอบ:**
```text
============================= test session starts =============================
collected 44 items

tests\test_all_intents.py ...................                            [ 43%]
tests\test_models.py ...                                                 [ 50%]
tests\test_services.py ..........                                        [ 72%]
tests\test_typo_resilience.py .....                                      [ 84%]
tests\test_views.py .....                                                [ 95%]
tests\test_webhook.py ..                                                 [100%]

============================= 44 passed in 28.57s =============================
```

---

## 📊 ผลการทดสอบประสิทธิภาพ (Performance & Benchmark)

| หัวข้อการทดสอบ | รายละเอียด / เมตริก | ผลลัพธ์ |
| :--- | :--- | :---: |
| **Intent Classification Accuracy** | ทดสอบบน Ground Truth 125 Scenarios | **96.80%** |
| **NLP Pipeline Latency** | ความเร็วเฉลี่ยต่อคำถาม (Tier 0 ➔ Tier 3) | **~0.5 - 4.0 ms** |
| **Hybrid Search Hit Rate@5** | ความแม่นยำ Top-5 สินค้า (QA Benchmark 100 ข้อ) | **92.0%** |
| **Typo Resilience** | อัตราดึงสินค้าถูกต้องเมื่อผู้ใช้พิมพ์ผิด / พิมพ์เสียงเพี้ยน | **100.0%** |
| **RAM Footprint (Singleton Model)** | ประหยัดหน่วยความจำจากการใช้ ModelLoader Singleton | **ประหยัด ~1.0 GB+** |

---

## 👥 ผู้จัดทำ (Author)

- **นายอนันดา ศิลปโชติ (Anandaa69)**
- **Email:** anandasinlapachote0@gmail.com
- **Repository:** `Chatbot_YuedPao`
