"""
Product Repository & Search Service (DB Queries & Fair Top 5 Sampling)
"""

import os
import re
import sqlite3
import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    from pythainlp.tokenize import word_tokenize
except ImportError:
    word_tokenize = None

# --- Synonym & Preprocessing Dictionaries (Document Expansion 2.0) ---
FABRIC_SYNONYMS = {
    "Classic Cotton": "ผ้าฝ้าย ฝ้าย ฝ้ายธรรมชาติ ผิวแพ้ง่าย ไม่คัน เนื้อผ้าแน่น ทรงตรง ไม่ยืดหลังซัก พักผ่อน สบาย",
    "Ultrasoft": "ผ้านุ่ม นุ่มพิเศษ ไม่ยับ ไม่ต้องรีด อัลตราซอฟ อลตราซอฟ อัลตาซอฟ อัลตราซอฟท์ อัลตาซอฟท์ โคตรนุ่ม โคตนุ่ม ใส่สบาย สบายตา ผิวสัมผัสนุ่ม เดินห้าง แม่บ้าน ออฟฟิศ IT",
    "Tailor Cool": "ผ้าเย็น ระบายอากาศ ใส่ไม่ร้อน เทเลอร์คูล เทเลอร์ คูล ทเลอคูล ใส่สบาย ไม่หมองจากเหงื่อ ไม่หมอง สุภาพ ขับรถ ออฟฟิศ",
    "Ecotech": "ผ้านุ่มรักษ์โลก"
}

COLOR_SYNONYMS = {
    "Cream": "ครีม สีครีม Vanilla ครีมมี่ Creamy วานิลลา",
    "Creamy": "ครีม สีครีม Vanilla ครีมมี่ Creamy วานิลลา",
    "Vanilla": "ครีม สีครีม Vanilla ครีมมี่ Creamy วานิลลา",
    "Mint": "มิ้นท์ สีมิ้นท์ Mint Green มิสกรีน Misgreen Mist Green",
    "Mist Green": "มิ้นท์ สีมิ้นท์ Mint Green มิสกรีน Misgreen Mist Green",
    "Dark Gray": "เทาเข้ม เทาดำ Smoke Gray Smock Gray เทา",
    "Smoke Gray": "เทาเข้ม เทาดำ Smoke Gray Smock Gray เทา เทาควันบุหรี่",
    "Smock Gray": "เทาเข้ม เทาดำ Smoke Gray Smock Gray เทา เทาควันบุหรี่",
    "Coffee Brown": "น้ำตาล กาแฟ",
    "Maroon": "แดงเลือดหมู แดงเข้ม",
    "Lavender": "ม่วงพาสเทล ม่วงลาเวนเดอร์",
    "White": "ขาว สีขาว White",
    "Black": "ดำ สีดำ Black"
}

STYLE_SYNONYMS = {
    "Round Neck": "คอกลม คอกม คอกลมปกติ",
    "V Neck": "คอวี วี",
    "Long Sleeve": "แขนยาว แขนยาวผู้ชาย แขนยาวผู้หญิง",
    "Short Sleeve": "แขนสั้น แขนสั้นผู้ชาย แขนสั้นผู้หญิง",
    "Unisex": "ผู้ชาย ผู้หญิง ชาย หญิง Unisex ใส่ได้ทั้งชายและหญิง"
}

PERSONA_SYNONYMS = {
    # Style vibe keywords (เท่ สตรีท วินเทจ คูล) are intentionally EXCLUDED from Oversize here.
    # They are matched separately via STYLE_VIBE_KEYWORDS_MAP to prevent cross-contamination
    # into all OVERSIZED-category products (e.g. Babytee Striped) via document expansion.
    "Oversize": "เสื้อยืด ทรงหลวม อกใหญ่ เผื่อไหล่ ไหล่ตก คนอ้วน ตั้งครรภ์ ตัวใหญ่ ใส่สบาย วันพักผ่อน คอกลม โอเวอไซ โอเวอร์ไซ โอเวอร์ไซส์ โอเวอไซส์ ผู้ชาย ผู้หญิง ชาย หญิง สาวอวบ ซ่อนหน้าท้อง ซ่อนพุง คนท้อง",
    "Kid": "เด็ก เสื้อเด็ก ของขวัญเด็ก เด็กอนุบาล ลายน่ารัก kidซ คิดส์ คิด",
    "Polo": "ใส่ทำงาน พนักงานบริษัท พนักงานโรงแรม ยูนิฟอร์ม สุภาพ งานสังสรรค์ ประชุม ปกโปโล เสื้อโปโล ปกคอ คอปก เสื้อคอปก เสื้อมีปก ปก ผู้ใหญ่ อายุ 40 50 ดูดี ไม่ดูแก่ ไม่แก่",
    "Crop": "เสื้อครอป น่ารัก น่ารักๆ สาวๆ เที่ยวทะเล คอกลม ทรงสั้นเอว เอวสูง ตัวเล็ก คิ้วท์ๆ หวานๆ สดใส y2k",
    "Running": "ใส่วิ่ง ออกกำลังกาย ระบายอากาศ ระบายความร้อน อากาศไทย ไม่ร้อน รันนิ่ง สปอร์ต เดินป่า ไม่หมองจากเหงื่อ ไม่มีกลิ่นเหงื่อ",
    "Tie Dye": "มัดย้อม ไทด์ดาย ไทน์ดาย ซัมเมอร์ เที่ยว สีสดใส มัดยอม ฟัดย้อม ถ่ายรูป content อาร์ต",
    "Sleeveless": "แขนกุด อากาศร้อน ไม่อึดอัด เสื้อกล้าม โยคะ ยืดหยุ่น",
    "Running Roulette": "รันนิ่งรูเล็ต รันนิ่ง รูเล็ต เสื้อฟอก วินเทจ",
    "Babytee": "เบบี้ที เบบี้ทีส์ เสื้อตัวเล็ก เสื้อยืดตัวเล็ก เบบี้ทีมูนิมอล น่ารัก น่ารักๆ คิ้วท์ๆ หวานๆ สดใส y2k",
    "Bag": "กระเป๋า กระเป๋าสะพาย กระเป๋าสะพายข้าง กระเป๋าถือ bagก baggg crossbody carrybag tote",
    "Pants": "กางเกง กางเกงขาสั้น กางเกงขายาว กางเกงยีนส์ ยีนส์ คาร์โก้ cargo short shorts pant pants"
}

STYLE_VIBE_KEYWORDS_MAP = {
    "cool": ["เท่", "เท่ๆ", "สตรีท", "วินเทจ", "เสื้อฟอก", "ยีนส์", "คาร์โก้", "คูล", "คูลๆ", "แมนๆ"],
    "cute": ["น่ารัก", "น่ารักๆ", "คิ้วท์", "คิ้วท์ๆ", "หวานๆ", "สดใส", "คุณหนู", "y2k", "คาเฟ่"],
    "chic": ["สวย", "สวยๆ", "เรียบหรู", "ดูดี", "สุภาพ", "ใส่ทำงาน", "ชิค", "ชิคๆ", "คัตติ้งเนี๊ยบ"]
}

POPULAR_KEYWORDS = [
    "ขายดี", "ขายดีสุด", "ฮิต", "ฮิตๆ", "ยอดฮิต", "นิยม", "ยอดนิยม",
    "best seller", "bestseller", "top seller", "ตัวขายดี", "สินค้าขายดี", "ตัวฮิต"
]

KODNUM_SYNONYMS = {
    "Kodnum": "โคตรนุ่ม โคตนุ่ม โคตรนุม โคตนุม"
}

COLOR_KEYWORDS_MAP = {
    "red": ["red", "แดง", "สีแดง", "maroon", "wine", "แดงเลือดหมู", "แดงเข้ม", "ชาไทย", "cha thai", "scarlet", "rose", "rosewood", "ruby", "crimson"],
    "blue": ["blue", "น้ำเงิน", "สีน้ำเงิน", "ฟ้า", "สีฟ้า", "navy", "กรม", "สีกรม", "oxford blue", "sky blue", "snow blue"],
    "green": ["green", "เขียว", "สีเขียว", "mint", "มิ้นท์", "mist green", "forest green", "olive green", "neon green", "misgreen", "mountain green"],
    "yellow": ["yellow", "เหลือง", "สีเหลือง", "lemon yellow", "worm yellow", "gold"],
    "pink": ["pink", "ชมพู", "สีชมพู", "dusty pink", "peony", "ชมพูดัสตี้"],
    "purple": ["purple", "ม่วง", "สีม่วง", "lavender", "ม่วงลาเวนเดอร์", "ม่วงพาสเทล"],
    "orange": ["orange", "ส้ม", "สีส้ม", "cha thai", "ชาไทย", "sunset", "ซันเซ็ท"],
    "brown": ["brown", "น้ำตาล", "สีน้ำตาล", "coffee brown", "chocolate brown", "vintage brown", "กาแฟ"],
    "gray": ["gray", "grey", "เทา", "สีเทา", "smoke gray", "smock gray", "dark gray", "light gray", "เทาควันบุหรี่", "เทาเข้ม", "เทาดำ"],
    "white": ["white", "ขาว", "สีขาว", "vanilla", "cream", "cloud", "วานิลลา", "ครีม"],
    "black": ["black", "ดำ", "สีดำ", "classic black"],
    "vanilla": ["vanilla", "วานิลลา", "ครีม", "cream"],
    "cream": ["ครีม", "cream", "vanilla", "วานิลลา"],
    "mint": ["mint", "มิ้นท์", "มิสกรีน", "mist green"],
    "smoke gray": ["smoke gray", "smock gray", "เทาควันบุหรี่", "เทาเข้ม", "เทาดำ"],
    "dark gray": ["dark gray", "เทาเข้ม", "เทาดำ"],
    "coffee brown": ["coffee brown", "น้ำตาล", "กาแฟ"],
    "maroon": ["maroon", "แดง", "สีแดง", "แดงเลือดหมู", "แดงเข้ม"],
    "lavender": ["lavender", "ม่วงพาสเทล", "ม่วงลาเวนเดอร์"],
    "navy": ["navy", "สีกรม", "กรม", "น้ำเงิน"]
}

INTENT_MAP_KEYWORDS = {
    "polo": ["โปโล", "polo", "สุภาพ", "ทำงาน", "พนักงานโรงแรม", "ประชุม", "ผู้ใหญ่", "ไม่แก่", "คอปก", "เสื้อคอปก", "ปก", "เสื้อมีปก"],
    "babytee": ["เบบี้ที", "babytee", "baby tee", "เสื้อตัวเล็ก"],
    "ultrasoft": ["ผ้านุ่ม", "ไม่ยับ", "ไม่ต้องรีด", "อัลตราซอฟ", "อัลตราซอฟท์", "โคตรนุ่ม", "โคตนุ่ม", "เดินห้าง", "สบายตา"],
    "classic cotton": ["ฝ้าย", "cotton", "ผิวแพ้ง่าย", "ไม่คัน", "เนื้อผ้าแน่น", "ทรงตรง", "ไม่ยืดหลังซัก"],
    "tailor cool": ["ผ้าเย็น", "ไม่ร้อน", "เทเลอร์คูล", "ทเลอคูล", "ไม่หมอง", "ขับรถ"],
    "oversize": ["ทรงหลวม", "อกใหญ่", "ไหล่ตก", "คนอ้วน", "ตั้งครรภ์", "ตัวใหญ่", "โอเวอไซ", "โอเวอร์ไซส์", "สาวอวบ", "ซ่อนพุง", "คนท้อง"],
    "tie dye": ["มัดย้อม", "ไทด์ดาย", "ไทน์ดาย", "ซัมเมอร์", "สีสดใส", "มัดยอม", "ฟัดย้อม", "ถ่ายรูป content", "อาร์ต"],
    "crop": ["ครอป", "crop", "ทรงสั้นเอว", "เอวสูง"],
    "sleeveless": ["แขนกุด", "เสื้อกล้าม", "โยคะ"],
    "running": ["วิ่ง", "ออกกำลังกาย", "ระบายเหงื่อ", "รันนิ่ง", "เดินป่า", "ไม่มีกลิ่นเหงื่อ"],
    "jeans": ["ยีนส์", "เกงยีนส์", "กางเกงยีนส์", "เดนิม"],
    "bag": ["กระเป๋า", "กระเป๋าสะพาย", "กระเป๋าถือ", "bag", "bagg", "crossbody", "carrybag", "tote"],
    "pants": ["กางเกง", "กางเกงขาสั้น", "กางเกงขายาว", "ขาสั้น", "ขายาว", "คาร์โก้", "cargo", "shorts", "pants"]
}


class ProductService:
    _instance = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern to prevent reloading models on every service instantiation."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, "yuedpao_chatbot.db")
        
        self.bert_model = None
        if SentenceTransformer:
            try:
                self.bert_model = SentenceTransformer('intfloat/multilingual-e5-small')
            except Exception as e:
                print(f"⚠️ Warning: Could not load SentenceTransformer in ProductService: {e}")

        self.products = []
        self.doc_ids = []
        self.documents = []
        self.metadatas = []
        self._load_products_from_db()

        self.chroma_client = None
        self.chroma_collection = None
        if chromadb and self.bert_model and self.documents:
            try:
                chroma_path = os.path.join(base_dir, "data", "chroma")
                os.makedirs(chroma_path, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=chroma_path)
                collection_name = "yuedpao_products_e5_search"
                self.chroma_collection = self.chroma_client.get_or_create_collection(
                    name=collection_name, 
                    metadata={"hnsw:space": "cosine"}
                )
                if self.chroma_collection.count() != len(self.documents):
                    try:
                        self.chroma_client.delete_collection(collection_name)
                    except Exception:
                        pass
                    self.chroma_collection = self.chroma_client.create_collection(
                        name=collection_name, 
                        metadata={"hnsw:space": "cosine"}
                    )
                    self._index_chromadb()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize ChromaDB in ProductService: {e}")

        self.bm25_model = None
        self.bm25_corpus = []
        if self.documents and word_tokenize:
            try:
                self._build_bm25_index()
            except Exception as e:
                print(f"⚠️ Warning: Could not build BM25 Index in ProductService: {e}")

    def reload_and_index(self):
        """Forces reloading products from SQLite DB and re-building ChromaDB + BM25 indices."""
        self._load_products_from_db()
        if not self.chroma_client and chromadb and self.bert_model and self.documents:
            try:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                chroma_path = os.path.join(base_dir, "data", "chroma")
                os.makedirs(chroma_path, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize ChromaDB client in reload_and_index: {e}")

        if self.chroma_client and self.bert_model and self.documents:
            collection_name = "yuedpao_products_e5_search"
            try:
                self.chroma_client.delete_collection(collection_name)
            except Exception:
                pass
            self.chroma_collection = self.chroma_client.create_collection(
                name=collection_name, 
                metadata={"hnsw:space": "cosine"}
            )
            self._index_chromadb()

        if self.documents:
            self._build_bm25_index()
        return self.documents

    def _load_products_from_db(self):
        if not os.path.exists(self.db_path):
            print(f"⚠️ Warning: Database file not found at {self.db_path}")
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if products table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
            if not cursor.fetchone():
                conn.close()
                return

            # Check if is_available and sales_volume columns exist in products table
            cursor.execute("PRAGMA table_info(products);")
            columns = [col[1] for col in cursor.fetchall()]

            has_avail = "is_available" in columns
            has_sales = "sales_volume" in columns

            select_cols = ["product_id", "name", "category", "fabric_collection", "style_fit", "price", "description", "image_url", "product_url"]
            if has_avail:
                select_cols.append("is_available")
            if has_sales:
                select_cols.append("sales_volume")

            sql_stmt = f"SELECT {', '.join(select_cols)} FROM products"
            if has_avail:
                sql_stmt += " WHERE is_available = 1"

            cursor.execute(sql_stmt)
            product_rows = cursor.fetchall()
            
            cursor.execute("SELECT product_id, GROUP_CONCAT(DISTINCT color_name) FROM product_variants GROUP BY product_id")
            variant_color_map = dict(cursor.fetchall())
            conn.close()
        except Exception as e:
            print(f"⚠️ Warning: Error querying SQLite products table: {e}")
            return

        self.products = []
        for r in product_rows:
            p_id = r[0]
            colors_str = variant_color_map.get(p_id, "") or ""
            p_url = r[8] or f"https://www.yuedpao.com/physical/{p_id}"

            cur_idx = 9
            p_avail = 1
            if has_avail:
                p_avail = r[cur_idx] if len(r) > cur_idx else 1
                cur_idx += 1
            
            p_sales = 0
            if has_sales:
                p_sales = r[cur_idx] if len(r) > cur_idx and r[cur_idx] is not None else 0
                cur_idx += 1

            self.products.append({
                "product_id": p_id,
                "name": r[1],
                "category": r[2],
                "fabric": r[3],
                "style": r[4],
                "price": r[5],
                "description": r[6] or "",
                "image_url": r[7] or "",
                "product_url": p_url,
                "colors": colors_str,
                "is_available": p_avail,
                "sales_volume": int(p_sales)
            })

        self.documents = []
        self.doc_ids = []
        self.metadatas = []

        for p in self.products:
            clean_name = self._clean_text(p["name"])
            clean_cat = self._clean_text(p["category"])
            clean_desc = self._clean_text(p["description"])
            
            spaced_colors = p["colors"].replace(",", " ")
            colors_info = f"สี: {spaced_colors}" if spaced_colors else ""

            expansions = []
            full_text_lower = f"{clean_name} {clean_cat} {p['fabric']} {p['style']} {spaced_colors} {clean_desc}".lower()
            
            for fab_key, syns in FABRIC_SYNONYMS.items():
                if fab_key.lower() in full_text_lower:
                    expansions.append(syns)
            for col_key, syns in COLOR_SYNONYMS.items():
                if col_key.lower() in full_text_lower:
                    expansions.append(syns)
            for style_key, syns in PERSONA_SYNONYMS.items():
                if style_key.lower() in full_text_lower:
                    expansions.append(syns)
            for style_key, syns in STYLE_SYNONYMS.items():
                if style_key.lower() in full_text_lower:
                    expansions.append(syns)
            for k_key, syns in KODNUM_SYNONYMS.items():
                if k_key.lower() in full_text_lower:
                    expansions.append(syns)

            synonym_str = f" | คำค้นหาพ้อง: {' '.join(set(expansions))}" if expansions else ""
            sales_str = f" | ยอดขาย: {p['sales_volume']} ชิ้น สินค้าขายดี ยอดฮิต" if p["sales_volume"] > 50 else ""

            doc_text = (
                f"passage: สินค้า: {clean_name} | หมวดหมู่: {clean_cat} | "
                f"เทคโนโลยีผ้า: {p['fabric']} | ทรงเสื้อ: {p['style']} | ราคา: ฿{p['price']} | "
                f"{colors_info}{sales_str}{synonym_str} | รายละเอียดและจุดเด่น: {clean_desc}"
            )
            self.documents.append(doc_text)
            self.doc_ids.append(f"prod_{p['product_id']}")
            
            cat_val = p["category"]
            if p["style"]:
                cat_val = cat_val + " " + p["style"]
            if "round neck" in p["name"].lower() or "round neck" in p["style"].lower():
                cat_val = cat_val + " คอกลม"
            if "v neck" in p["name"].lower() or "v neck" in p["style"].lower():
                cat_val = cat_val + " คอวี"
            if "kid" in p["name"].lower() or "kid" in cat_val.lower():
                cat_val = cat_val + " Kids"
                
            color_val = p["colors"]
            if "mist green" in color_val.lower() or "misgreen" in color_val.lower():
                color_val = color_val + ",Mint"

            gender_val = self._classify_product_gender(p["name"], cat_val, p["style"], p["description"])

            item_haystack = f"{p['name']} {cat_val} {p['fabric']} {p['style']} {doc_text}".lower()
            item_color_text = f"{p['name']} {color_val}".lower()

            self.metadatas.append({
                "product_id": p["product_id"],
                "name": p["name"],
                "category": cat_val,
                "fabric": p["fabric"],
                "style": p["style"],
                "price": p["price"],
                "image_url": p["image_url"],
                "product_url": p["product_url"],
                "colors": color_val,
                "gender": gender_val,
                "is_available": p.get("is_available", 1),
                "sales_volume": p.get("sales_volume", 0),
                "haystack": item_haystack,
                "color_text": item_color_text
            })

    def _classify_product_gender(self, name: str, category: str, style: str, description: str) -> str:
        text = f"{name} {category} {style} {description}".lower()
        female_keywords = ["woman", "women", "crop", "babytee", "คุณผู้หญิง", "ผู้หญิง", "สำหรับผู้หญิง", "สาวๆ", "เอวสูง"]
        
        is_female = any(kw in text for kw in female_keywords)
        
        is_male = False
        for kw in ["คุณผู้ชาย", "ผู้ชาย", "สำหรับผู้ชาย"]:
            if kw in text:
                is_male = True
                break
        if not is_male:
            if re.search(r'\bmen\b|\bman\b', text):
                is_male = True
        
        if is_female and not is_male:
            return "female"
        elif is_male and not is_female:
            return "male"
        else:
            return "unisex"

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"ส่งฟรี\*?", "", text)
        text = text.replace("_", " ").replace("-", " ").replace("/", " ")
        text = re.sub(r"[\r\n]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _index_chromadb(self):
        embeddings = self.bert_model.encode(
            self.documents, 
            convert_to_tensor=False, 
            batch_size=32, 
            show_progress_bar=False
        ).tolist()
        self.chroma_collection.add(
            ids=self.doc_ids, 
            documents=self.documents, 
            embeddings=embeddings, 
            metadatas=self.metadatas
        )

    def _bm25_tokenizer(self, text: str) -> List[str]:
        if word_tokenize:
            clean_doc = text.replace("passage: ", "")
            tokens = word_tokenize(clean_doc, engine="newmm")
            return [t.strip().lower() for t in tokens if t.strip()]
        
        # High-precision Thai N-Gram Tokenizer (matches sub-words like 'พะยูน' without external NLP library)
        clean_doc = text.replace("passage: ", "")
        raw_tokens = re.findall(r'[a-zA-Z0-9%]+|[\u0E00-\u0E7F]+', clean_doc)
        final_tokens = []
        
        for tok in raw_tokens:
            if re.match(r'^[a-zA-Z0-9%]+$', tok):
                final_tokens.append(tok.lower())
            else:
                final_tokens.append(tok.lower())
                tok_len = len(tok)
                for n in range(2, 8):
                    for i in range(tok_len - n + 1):
                        final_tokens.append(tok[i:i+n])
                    
        return final_tokens

    def _build_bm25_index(self):
        try:
            from rank_bm25 import BM25Okapi
            self.bm25_corpus = [self._bm25_tokenizer(doc) for doc in self.documents]
            self.bm25_model = BM25Okapi(self.bm25_corpus)
        except ImportError:
            self.bm25_model = None
            self.bm25_corpus = []

    def _extract_price_bounds(self, query: str) -> Tuple[Optional[int], Optional[int]]:
        """Extracts (min_price, max_price) boundaries from raw query string."""
        query_lower = query.lower()
        min_price = None
        max_price = None

        # 0. Check Range Boundary (e.g., '100-200', '100 ถึง 200', '100 - 200')
        match_range = re.search(r'(\d+)\s*[-–—toถึง]\s*(\d+)', query_lower)
        if match_range:
            p1, p2 = int(match_range.group(1)), int(match_range.group(2))
            return min(p1, p2), max(p1, p2)

        # 1. Min Price Boundary (e.g., 'มากกว่า 500', 'เกิน 500' [แต่ต้องไม่ใช่ 'ไม่เกิน'], 'สูงกว่า 500', '500 ขึ้นไป')
        match_min = re.search(r'(?<!ไม่)(?:มากกว่า|เกิน|สูงกว่า|แพงกว่า)\s*(\d+)', query_lower)
        if match_min:
            min_price = int(match_min.group(1))
        else:
            match_min2 = re.search(r'(\d+)\s*(?:บาท|บ\.)?\s*(?:ขึ้นไป)', query_lower)
            if match_min2:
                min_price = int(match_min2.group(1))

        # 2. Max Price Boundary (e.g., 'ไม่เกิน 300', 'ต่ำกว่า 300', 'น้อยกว่า 300', 'งบ 300')
        match_max = re.search(r'(?:ไม่เกิน|งบ|ราคา|ต่ำกว่า|น้อยกว่า|งบประมาณ|ราคาประมาณ)\s*(?:ประมาณ|ไม่เกิน|ต่ำกว่า|น้อยกว่า)?\s*(\d+)', query_lower)
        if match_max:
            val = int(match_max.group(1))
            if min_price is None or val != min_price:
                max_price = val
        else:
            match_max2 = re.search(r'(\d+)\s*(?:บาท|บ\.)\s*(?:ลงมา|ต่ำกว่า)?', query_lower)
            if match_max2 and min_price is None:
                max_price = int(match_max2.group(1))

        return min_price, max_price

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return ProductService._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def _fuzzy_has_keyword(self, raw_query: str, target_keywords: List[str], max_edit: int = 1) -> bool:
        q_clean = raw_query.lower()
        # 1. Direct sub-string match (< 0.01ms)
        for target in target_keywords:
            t_low = target.lower()
            if t_low in q_clean:
                return True

        # 2. Pre-tokenization Sliding Window Fuzzy Match
        q_len = len(q_clean)
        if q_len < 3:
            return False

        for target in target_keywords:
            t_low = target.lower()
            t_len = len(t_low)
            if t_len < 3:
                continue
            min_w = max(2, t_len - 1)
            max_w = min(q_len + 1, t_len + 2)
            for w_len in range(min_w, max_w):
                for start_idx in range(0, q_len - w_len + 1):
                    window = q_clean[start_idx : start_idx + w_len]
                    if ProductService._levenshtein(window, t_low) <= max_edit:
                        return True
        return False

    def _detect_query_intents(self, query: str) -> List[str]:
        q_lower = query.lower()
        detected = []
        for intent_tag, kw_list in INTENT_MAP_KEYWORDS.items():
            if self._fuzzy_has_keyword(q_lower, kw_list, max_edit=1):
                detected.append(intent_tag)
        return detected

    def _detect_query_colors(self, query: str) -> List[str]:
        q_lower = query.lower()
        detected_cols = []
        for col_key, kw_list in COLOR_KEYWORDS_MAP.items():
            if any(kw in q_lower for kw in kw_list):
                detected_cols.append(col_key)
        return detected_cols

    def _detect_query_style_vibes(self, query: str) -> List[str]:
        q_lower = query.lower()
        detected_vibes = []
        for vibe_key, kw_list in STYLE_VIBE_KEYWORDS_MAP.items():
            if any(kw in q_lower for kw in kw_list):
                detected_vibes.append(vibe_key)
        return detected_vibes

    def _detect_query_gender(self, query: str) -> Optional[str]:
        q_lower = query.lower()
        
        # Check kids demographic first to prevent "เด็กชาย" matching adult "ชาย"
        if any(kw in q_lower for kw in ["เด็ก", "kid", "kids", "อนุบาล", "ลูก"]):
            if any(kw in q_lower for kw in ["เด็กหญิง", "ลูกสาว", "ผู้หญิง"]):
                return "kids_female"
            if any(kw in q_lower for kw in ["เด็กชาย", "ลูกชาย", "ผู้ชาย"]):
                return "kids_male"
            return "kids"

        female_query_kws = ["ผู้หญิง", "หญิง", "สำหรับผู้หญิง", "คุณผู้หญิง", "women", "woman", "สาว", "สาวๆ", "สวย", "น่ารัก", "น่ารักๆ", "คิ้วท์"]
        male_query_kws = ["ผู้ชาย", "สำหรับผู้ชาย", "คุณผู้ชาย", "men", "man", "หล่อ", "หล่อๆ", "แมน"]
        
        has_female = any(kw in q_lower for kw in female_query_kws) or (re.search(r'(?<!เด็ก)หญิง', q_lower) is not None)
        has_male = any(kw in q_lower for kw in male_query_kws) or (re.search(r'(?<!เด็ก)ชาย', q_lower) is not None)
        
        if has_male and not has_female:
            return "male"
        if has_female and not has_male:
            return "female"
        return None

    def _detect_query_popular(self, query: str) -> bool:
        q_lower = query.lower()
        return any(kw in q_lower for kw in POPULAR_KEYWORDS)

    def search_products(self, raw_query: str, top_k: int = 15, offset: int = 0, k_constant: int = 60, return_dict: bool = False) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Main entry point for product retrieval. Combines BM25 and Vector DB search 
        using Reciprocal Rank Fusion (RRF), with integrated Intent Boost, Color Match Boost,
        Gender Filtering, Sales Volume Boost, Smart Price Fallback, and Offset Pagination.
        """
        if not self.documents:
            return []

        unsupported_keywords = ["รองเท้า", "นาฬิกา", "น้ำหอม", "แว่นตา", "เข็มขัด", "แหวน", "สร้อย", "ลิป", "กระเป๋าตังค์", "สเก็ตบอร์ด", "หูฟัง", "ตู้เย็น", "แก้วน้ำ", "หมอน", "เคสโทรศัพท์", "โน๊ตบุ๊ค"]
        def is_unsupported(query: str) -> bool:
            q_low = query.lower()
            for kw in unsupported_keywords:
                if kw in q_low:
                    return True
            if re.search(r'(?<!สี)ครีม', q_low):
                return True
            return False

        if is_unsupported(raw_query):
            print(f"🔎 [Search Engine Safeguard] Query '{raw_query}' matched unsupported keyword ──► Returning 0 products")
            if return_dict:
                return {"products": [], "total_count": 0, "has_more": False, "fallback_msg": None}
            return []

        min_price, max_price = self._extract_price_bounds(raw_query)
        detected_intents = self._detect_query_intents(raw_query)
        requested_colors = self._detect_query_colors(raw_query)
        requested_gender = self._detect_query_gender(raw_query)
        requested_vibes = self._detect_query_style_vibes(raw_query)
        is_popular = self._detect_query_popular(raw_query)

        print(f"🔎 [Search Engine Debug] Query: '{raw_query}' ──► Popular Filter: '{is_popular}' | Gender Filter: '{requested_gender}' | Style Vibes: {requested_vibes} | Intents: {detected_intents} | Colors: {requested_colors} | Min Price: {min_price} | Max Price: {max_price}")

        # 1. BM25 ranks
        bm25_scores = [0.0] * len(self.documents)
        if self.bm25_model:
            query_tokens = self._bm25_tokenizer(raw_query)
            bm25_scores = self.bm25_model.get_scores(query_tokens)
        bm25_ranked_indices = np.argsort(bm25_scores)[::-1]

        # 2. Vector ranks
        vector_rank_map = {}
        if self.chroma_collection and self.bert_model:
            try:
                query_emb = self.bert_model.encode(f"query: {raw_query}", convert_to_tensor=False).tolist()
                chroma_results = self.chroma_collection.query(query_embeddings=[query_emb], n_results=len(self.documents))
                vector_rank_map = {doc_id: rank + 1 for rank, doc_id in enumerate(chroma_results["ids"][0])}
            except Exception as e:
                print(f"⚠️ ChromaDB Query Warning: {e}. Re-initializing collection...")
                try:
                    collection_name = "yuedpao_products_e5_search"
                    self.chroma_collection = self.chroma_client.get_or_create_collection(
                        name=collection_name, 
                        metadata={"hnsw:space": "cosine"}
                    )
                    if self.chroma_collection.count() != len(self.documents):
                        self._index_chromadb()
                    chroma_results = self.chroma_collection.query(query_embeddings=[query_emb], n_results=len(self.documents))
                    vector_rank_map = {doc_id: rank + 1 for rank, doc_id in enumerate(chroma_results["ids"][0])}
                except Exception as retry_e:
                    print(f"⚠️ ChromaDB Recovery Failed: {retry_e}")

        # Pre-compute query-level flags once (outside RRF loop for massive speedup)
        query_lower = raw_query.lower()
        requested_vibes = self._detect_query_style_vibes(raw_query)
        # Use fuzzy match for kids so typos like 'เด็ห', 'เดก', 'เด็ค' are caught
        query_has_kids = self._fuzzy_has_keyword(query_lower, ["เด็ก", "kid", "kids", "อนุบาล", "ลูก", "เด็กชาย", "เด็กหญิง", "เสื้อเด็ก"])
        query_has_crop = any(k in query_lower for k in ["crop", "ครอป", "เอวลอย"])
        query_not_shirt = any(neg in query_lower for neg in ["ไม่ใช่เสื้อ", "ไม่เอาเสื้อ", "นอกจากเสื้อ", "ไม่ ใช่ เสื้อ"]) or (re.search(r'ไม่.*เสื้อ', query_lower) is not None)
        query_has_bra = any(b in query_lower for b in ["บรา", "bra", "สปอร์ตบรา"])
        query_has_shirt = (any(k in query_lower for k in ["เสื้อ", "shirt", "tshirt", "t-shirt", "โปโล", "คอกลม", "คอวี", "ครอป", "เบบี้ที", "แขนยาว", "แขนสั้น"]) and not query_not_shirt and not query_has_bra)

        query_has_pants = self._fuzzy_has_keyword(query_lower, ["กางเกง", "ขายาว", "ขาสั้น", "ยีนส์", "pants", "shorts", "cargo"])
        query_has_unwear = self._fuzzy_has_keyword(query_lower, ["กางเกงใน", "กกน", "ชุดชั้นใน", "unwear", "briefs", "boxer"])
        query_has_bag = self._fuzzy_has_keyword(query_lower, ["กระเป๋า", "bag", "bagg", "crossbody", "tote", "carrybag"])
        
        match_pct = re.search(r'(\d+)\s*%', raw_query)
        match_pct_val = match_pct.group(1) if match_pct else None

        requested_color_syns = []
        if requested_colors:
            for req_col in requested_colors:
                requested_color_syns.extend(COLOR_KEYWORDS_MAP.get(req_col, [req_col]))

        # 3. RRF Fusion Helper
        def compute_rrf(apply_price_filter: bool, apply_strict_intent: bool = True):
            scores = {}
            for bm25_rank, idx in enumerate(bm25_ranked_indices):
                doc_id = self.doc_ids[idx]
                meta = self.metadatas[idx]
                price = meta["price"]

                if apply_price_filter:
                    if min_price is not None and price < min_price:
                        continue
                    if max_price is not None and price > max_price:
                        continue

                item_gender = meta.get("gender", "unisex")
                if requested_gender == "male" and item_gender == "female":
                    continue
                elif requested_gender == "female" and item_gender == "male":
                    continue

                r_bm25 = bm25_rank + 1
                r_vec = vector_rank_map.get(doc_id, 9999)
                base_score = (1.0 / (k_constant + r_bm25)) + (1.0 / (k_constant + r_vec))

                item_haystack = meta.get("haystack", "")

                # Strict Intent / Category Filter
                if apply_strict_intent:
                    if "polo" in detected_intents and not ("polo" in item_haystack or "โปโล" in item_haystack or "คอปก" in item_haystack or "เสื้อโปโล" in item_haystack or "หมวดหมู่: polo" in item_haystack):
                        continue
                    if "crop" in detected_intents and not ("crop" in item_haystack or "ครอป" in item_haystack):
                        continue
                    if "babytee" in detected_intents and not ("babytee" in item_haystack or "เบบี้ที" in item_haystack):
                        continue
                    if "oversize" in detected_intents and not ("oversize" in item_haystack or "โอเวอร์ไซส์" in item_haystack or "โอเวอไซ" in item_haystack or "ทรงหลวม" in item_haystack):
                        continue
                    if "jeans" in detected_intents and not ("jeans" in item_haystack or "ยีนส์" in item_haystack or "เดนิม" in item_haystack):
                        continue
                    if "running" in detected_intents and not ("running" in item_haystack or "วิ่ง" in item_haystack or "รันนิ่ง" in item_haystack or "ออกกำลังกาย" in item_haystack):
                        continue
                    if "bag" in detected_intents and not ("bag" in item_haystack or "กระเป๋า" in item_haystack or "crossbody" in item_haystack or "tote" in item_haystack):
                        continue
                    if "pants" in detected_intents and not ("pants" in item_haystack or "กางเกง" in item_haystack or "ขาสั้น" in item_haystack or "ขายาว" in item_haystack or "shorts" in item_haystack or "cargo" in item_haystack or "ยีนส์" in item_haystack):
                        continue

                # Intent Boost (1.60x for polo, 1.25x for others)
                intent_boost = 1.0
                if detected_intents and any(tag in item_haystack for tag in detected_intents):
                    intent_boost = 1.60 if "polo" in detected_intents and ("polo" in item_haystack or "โปโล" in item_haystack or "คอปก" in item_haystack) else 1.25

                # Color Match Boost & Non-match Demotion
                color_boost = 1.0
                if requested_color_syns:
                    item_col_text = meta.get("color_text", "")
                    if any(syn in item_col_text for syn in requested_color_syns):
                        color_boost = 2.50
                    else:
                        color_boost = 0.15

                # Style Vibe Match Boost (1.35x for match, demote female-only on cool/street vibes)
                style_vibe_boost = 1.0
                if requested_vibes:
                    vibe_matched = False
                    for req_vibe in requested_vibes:
                        syn_list = STYLE_VIBE_KEYWORDS_MAP.get(req_vibe, [req_vibe])
                        if any(syn in item_haystack for syn in syn_list):
                            style_vibe_boost = 1.35
                            vibe_matched = True
                            break
                    # For "cool" / "street" vibes: strongly boost true cool-category products
                    # and demote female-only items (Babytee, Crop) that only match due to description text
                    if "cool" in requested_vibes or "street" in requested_vibes:
                        item_style_lower = meta.get("style", "").lower()
                        item_name_lower = meta.get("name", "").lower()
                        is_true_cool = any(kw in item_style_lower or kw in item_name_lower for kw in
                                           ["oversize", "tie dye", "running roulette", "roulette", "jeans", "cargo", "screen", "collab"])
                        is_female_only_style = (item_gender == "female" and
                                                any(kw in item_style_lower or kw in item_name_lower for kw in
                                                    ["babytee", "crop", "baby tee"]))
                        if is_true_cool:
                            style_vibe_boost = max(style_vibe_boost, 2.00)
                        elif is_female_only_style and not requested_gender:
                            style_vibe_boost = min(style_vibe_boost, 0.30)

                # Gender Preference Match Boost (1.75x for specific gender products)
                gender_match_boost = 1.0
                if requested_gender == "female":
                    if item_gender == "female":
                        gender_match_boost = 1.75
                    elif item_gender == "unisex":
                        gender_match_boost = 1.0
                elif requested_gender == "male":
                    if item_gender == "male":
                        gender_match_boost = 1.75
                    elif item_gender == "unisex":
                        gender_match_boost = 1.0

                item_title_cat = f"{meta['name']} {meta.get('category', '')} {meta.get('style', '')}".lower()
                item_is_kids = "kid" in item_title_cat or "เด็ก" in item_title_cat
                item_is_crop = "crop" in item_title_cat or "ครอป" in item_title_cat
                item_cat_upper = meta.get("category", "").upper()

                # Symmetric Kids Boost / Adult Demotion
                if query_has_kids:
                    kids_boost = 2.50 if item_is_kids else 0.05
                else:
                    kids_boost = 0.15 if item_is_kids else 1.0

                crop_boost = 0.40 if (item_is_crop and not query_has_crop) else 1.0

                category_mismatch_boost = 1.0
                if query_has_bra:
                    item_is_bra = any(b in item_haystack for b in ["บรา", "bra", "สปอร์ตบรา", "rib bra"])
                    if item_is_bra:
                        category_mismatch_boost = 2.50
                    else:
                        category_mismatch_boost = 0.01
                elif query_has_bag:
                    item_is_bag = any(b in item_title_cat for b in ["bag", "กระเป๋า"])
                    if item_is_bag:
                        category_mismatch_boost = 3.50
                    else:
                        category_mismatch_boost = 0.01
                elif query_not_shirt:
                    item_title_cat_fab = f"{meta['name']} {meta.get('category', '')} {meta.get('fabric', '')}".lower()
                    item_is_non_shirt = any(non in item_title_cat_fab for non in ["accessories", "unwear", "jeans", "pants", "short", "cap", "bag", "socks", "หมวก", "กระเป๋า", "กางเกง", "ถุงเท้า"])
                    if item_is_non_shirt:
                        category_mismatch_boost = 2.50
                    else:
                        category_mismatch_boost = 0.01
                elif query_has_shirt:
                    # Demote non-shirt categories
                    if any(unwanted in item_cat_upper for unwanted in ["UNWEAR", "ACCESSORIES", "RIB BRA", "SOCKS"]):
                        category_mismatch_boost = 0.01
                    # Demote non-shirt items like caps and shorts inside multi-product categories (e.g. ULTRA FLOW)
                    if any(unwanted in item_haystack for unwanted in ["กางเกง", "หมวก", " cap", "cap_", "short", "shorts", "pants", "trousers"]):
                        category_mismatch_boost = 0.01
                elif query_has_pants and not query_has_unwear:
                    # Outerwear Pants Priority Boost (3.50x) & Demote Underwear/UNWEAR (0.01x) and Shirts (0.01x)
                    item_is_unwear = "unwear" in item_cat_upper or any(u in item_title_cat for u in ["unwear", "กางเกงใน", "briefs", "boxer"])
                    item_is_outer_pants = any(p in item_title_cat for p in ["กางเกง", "pants", "short", "shorts", "jeans", "ยีนส์", "cargo", "sweatpant"])
                    if item_is_unwear:
                        category_mismatch_boost = 0.01
                    elif item_is_outer_pants:
                        category_mismatch_boost = 3.50
                    elif any(unwanted in item_haystack for unwanted in ["เสื้อ", "shirt", "tshirt", "t-shirt", "polo", "crop", "babytee"]):
                        category_mismatch_boost = 0.01

                # Sales Volume / Popularity Match Boost
                sales_vol = meta.get("sales_volume", 0)
                sales_vol_boost = 1.0
                if is_popular:
                    sales_vol_boost = 1.0 + min(np.log1p(sales_vol) * 0.60, 4.0)
                else:
                    sales_vol_boost = 1.0 + min(np.log1p(sales_vol) * 0.02, 0.15)

                # Exact Percentage / Numeric Spec Boost (e.g., '60%', '100%')
                spec_boost = 1.0
                if match_pct_val:
                    if f"{match_pct_val}%" in item_haystack or f"{match_pct_val} %" in item_haystack or f"{match_pct_val} percent" in item_haystack:
                        spec_boost = 3.00
                    else:
                        spec_boost = 0.20

                final_score = base_score * intent_boost * color_boost * style_vibe_boost * gender_match_boost * kids_boost * crop_boost * category_mismatch_boost * sales_vol_boost * spec_boost

                scores[doc_id] = {
                    "score": final_score,
                    "metadata": meta
                }
            return scores

        # 1. Search with strict budget and strict intent constraint
        strict_scores = compute_rrf(apply_price_filter=True, apply_strict_intent=True)
        if is_popular:
            # Filter items that matched category guards (score > 0.01 threshold)
            valid_popular = [item for item in strict_scores.items() if item[1]["score"] > 0.01]
            invalid_popular = [item for item in strict_scores.items() if item[1]["score"] <= 0.01]
            sorted_valid = sorted(
                valid_popular, 
                key=lambda x: (x[1]["metadata"].get("sales_volume", 0), x[1]["score"]), 
                reverse=True
            )
            sorted_invalid = sorted(
                invalid_popular, 
                key=lambda x: x[1]["score"], 
                reverse=True
            )
            sorted_strict = sorted_valid + sorted_invalid
        else:
            sorted_strict = sorted(strict_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        strict_items = [res[1]["metadata"] for res in sorted_strict]

        # Demographic Filter Guard: If user specifically asked for kids products, exclude adult items if kids items exist
        query_has_kids = any(k in raw_query.lower() for k in ["เด็ก", "kid", "kids", "อนุบาล", "ลูก"])
        if query_has_kids:
            kids_only_items = [
                m for m in strict_items 
                if "kid" in (m.get("name", "") + m.get("category", "")).lower() or "เด็ก" in (m.get("name", "") + m.get("category", "")).lower()
            ]
            if kids_only_items:
                strict_items = kids_only_items

        fallback_message = None

        if len(strict_items) >= (offset + top_k) or (max_price is None and not detected_intents and len(strict_items) >= offset):
            all_candidate_items = strict_items
        else:
            # 2. Smart Fallback: Relax price constraint while keeping category/intent intact
            relaxed_scores = compute_rrf(apply_price_filter=False, apply_strict_intent=True)
            sorted_relaxed = sorted(relaxed_scores.items(), key=lambda x: x[1]["score"], reverse=True)
            relaxed_items = [res[1]["metadata"] for res in sorted_relaxed]

            strict_ids = {p["product_id"] for p in strict_items}
            needed = max(0, (offset + top_k) - len(strict_items))
            additional_items = []
            for p in relaxed_items:
                if p["product_id"] not in strict_ids:
                    p_copy = dict(p)
                    p_copy["is_recommended"] = True
                    additional_items.append(p_copy)

            all_candidate_items = strict_items + additional_items

            # Build human-friendly fallback message
            intent_label = ""
            if "polo" in detected_intents:
                intent_label = "เสื้อคอปก"
            elif "crop" in detected_intents:
                intent_label = "เสื้อครอป"
            elif "jeans" in detected_intents:
                intent_label = "กางเกงยีนส์"
            elif "babytee" in detected_intents:
                intent_label = "เสื้อเบบี้ที"
            elif "running" in detected_intents:
                intent_label = "เสื้อใส่วิ่งออกกำลังกาย"
            else:
                intent_label = "สินค้า"

            if len(strict_items) > 0 and len(additional_items) > 0 and offset == 0:
                fallback_message = f"พบ{intent_label}ตรงตามงบประมาณ {len(strict_items)} รายการ และขอแนะนำรุ่นสไตล์เดียวกันในงบใกล้เคียงเพิ่มเติมครับ:"
            elif len(strict_items) == 0 and len(all_candidate_items) > 0 and offset == 0:
                fallback_message = f"ไม่พบ{intent_label}ในงบประมาณดังกล่าว แต่ขอแนะนำรุ่นสไตล์เดียวกันในงบใกล้เคียงที่สุดให้ครับ:"

        total_count = len(all_candidate_items)
        final_items = all_candidate_items[offset : offset + top_k]

        if return_dict:
            return {
                "products": final_items,
                "fallback_message": fallback_message,
                "strict_count": len(strict_items),
                "total_count": total_count,
                "offset": offset,
                "has_more": (offset + len(final_items)) < total_count
            }

        return final_items

    def rrf_hybrid_search(self, raw_query: str, top_k: int = 15, offset: int = 0) -> List[Dict[str, Any]]:
        """Alias for search_products for backwards compatibility."""
        return self.search_products(raw_query=raw_query, top_k=top_k, offset=offset)

    def get_fair_top5_recommendations(self, candidate_pool: Optional[List[Dict[str, Any]]] = None, session_history: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Filters out items recently shown in the current user session,
        then randomly samples up to 5 items to generate a fresh, fair recommendation list.
        Modifies session_history in-place (keeps last 10 product IDs).
        """
        if candidate_pool is None:
            candidate_pool = self.products
        if session_history is None:
            session_history = []

        if not candidate_pool:
            return []

        fresh_pool = [
            item for item in candidate_pool 
            if item.get("product_id") not in session_history
        ]
        
        if len(fresh_pool) < 5:
            fresh_pool = candidate_pool
            
        sample_size = min(len(fresh_pool), 5)
        selected_items = random.sample(fresh_pool, sample_size)
        
        new_shown_ids = [item.get("product_id") for item in selected_items]
        session_history.extend(new_shown_ids)
        
        del session_history[:-10]
        
        recommended_items = []
        for item in selected_items:
            item_copy = dict(item)
            item_copy["is_recommended"] = True
            recommended_items.append(item_copy)
            
        return recommended_items
