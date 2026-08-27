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
    "Oversize": "เสื้อยืด ทรงหลวม อกใหญ่ เผื่อไหล่ ไหล่ตก คนอ้วน ตั้งครรภ์ ตัวใหญ่ ใส่สบาย วันพักผ่อน คอกลม โอเวอไซ โอเวอร์ไซ โอเวอร์ไซส์ โอเวอไซส์ ผู้ชาย ผู้หญิง ชาย หญิง สาวอวบ ซ่อนหน้าท้อง ซ่อนพุง คนท้อง เท่ เท่ๆ สตรีท วินเทจ คูลๆ ชิคๆ",
    "Kid": "เด็ก เสื้อเด็ก ของขวัญเด็ก เด็กอนุบาล ลายน่ารัก kidซ คิดส์ คิด",
    "Polo": "ใส่ทำงาน พนักงานบริษัท พนักงานโรงแรม ยูนิฟอร์ม สุภาพ งานสังสรรค์ ประชุม ปกโปโล เสื้อโปโล ปกคอ คอปก เสื้อคอปก เสื้อมีปก ปก ผู้ใหญ่ อายุ 40 50 ดูดี ไม่ดูแก่ ไม่แก่ สวย สวยๆ เรียบหรู คัตติ้งเนี๊ยบ",
    "Crop": "เสื้อครอป น่ารัก น่ารักๆ สาวๆ เที่ยวทะเล คอกลม ทรงสั้นเอว เอวสูง ตัวเล็ก คิ้วท์ๆ หวานๆ สดใส y2k",
    "Running": "ใส่วิ่ง ออกกำลังกาย ระบายอากาศ ระบายความร้อน อากาศไทย ไม่ร้อน รันนิ่ง สปอร์ต เดินป่า ไม่หมองจากเหงื่อ ไม่มีกลิ่นเหงื่อ",
    "Tie Dye": "มัดย้อม ไทด์ดาย ไทน์ดาย ซัมเมอร์ เที่ยว สีสดใส มัดยอม ฟัดย้อม ถ่ายรูป content อาร์ต สตรีท เท่ๆ",
    "Sleeveless": "แขนกุด อากาศร้อน ไม่อึดอัด เสื้อกล้าม โยคะ ยืดหยุ่น",
    "Running Roulette": "รันนิ่งรูเล็ต รันนิ่ง รูเล็ต เสื้อฟอก วินเทจ เท่ เท่ๆ สตรีท",
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
    "vanilla": ["vanilla", "วานิลลา", "ครีม", "cream"],
    "cream": ["ครีม", "cream", "vanilla", "วานิลลา"],
    "mint": ["mint", "มิ้นท์", "มิสกรีน", "mist green"],
    "smoke gray": ["smoke gray", "smock gray", "เทาควันบุหรี่", "เทาเข้ม", "เทาดำ"],
    "dark gray": ["dark gray", "เทาเข้ม", "เทาดำ"],
    "coffee brown": ["coffee brown", "น้ำตาล", "กาแฟ"],
    "maroon": ["maroon", "แดงเลือดหมู", "แดงเข้ม"],
    "lavender": ["lavender", "ม่วงพาสเทล", "ม่วงลาเวนเดอร์"],
    "white": ["white", "ขาว", "สีขาว"],
    "black": ["black", "ดำ", "สีดำ"],
    "navy": ["navy", "สีกรม", "กรม"],
    "forest green": ["forest green", "เขียวฟอเรสต์", "เขียวเข้ม"],
    "wine": ["wine", "สีไวน์", "ไวน์"],
    "dusty pink": ["dusty pink", "ชมพูดัสตี้", "ชมพู"],
    "olive green": ["olive green", "เขียวโอลิฟ", "เขียวขี้ม้า"],
    "sky blue": ["sky blue", "ฟ้า", "สีฟ้า"],
    "lemon yellow": ["lemon yellow", "เหลือง"],
    "peach": ["peach", "พีช"],
    "neon green": ["neon green", "เขียวนีออน"],
    "chocolate brown": ["chocolate brown", "น้ำตาลช็อคโกแลต"],
    "sunset": ["sunset", "ซันเซ็ท"],
    "peony": ["peony", "พีโอนี"]
}

INTENT_MAP_KEYWORDS = {
    "polo": ["โปโล", "polo", "สุภาพ", "ทำงาน", "พนักงานโรงแรม", "ประชุม", "ผู้ใหญ่", "ไม่แก่", "คอปก", "เสื้อคอปก", "ปก", "เสื้อมีปก"],
    "babytee": ["เบบี้ที", "babytee", "baby tee", "เสื้อตัวเล็ก"],
    "ultrasoft": ["ผ้านุ่ม", "ไม่ยับ", "ไม่ต้องรีด", "อัลตราซอฟ", "อลตราซอฟ", "อัลตราซอฟท์", "โคตรนุ่ม", "โคตนุ่ม", "เดินห้าง", "สบายตา"],
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
                "sales_volume": p.get("sales_volume", 0)
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
        if not word_tokenize:
            return [t.strip().lower() for t in text.split() if t.strip()]
        clean_doc = text.replace("passage: ", "")
        tokens = word_tokenize(clean_doc, engine="newmm")
        return [t.strip().lower() for t in tokens if t.strip()]

    def _build_bm25_index(self):
        from rank_bm25 import BM25Okapi
        self.bm25_corpus = [self._bm25_tokenizer(doc) for doc in self.documents]
        self.bm25_model = BM25Okapi(self.bm25_corpus)

    def _extract_max_price(self, query: str) -> Optional[int]:
        query_lower = query.lower()
        match = re.search(r'(?:ไม่เกิน|งบ|ราคา|ต่ำกว่า|น้อยกว่า|งบประมาณ|ราคาประมาณ)\s*(?:ประมาณ|ไม่เกิน|ต่ำกว่า|น้อยกว่า)?\s*(\d+)', query_lower)
        if match:
            return int(match.group(1))
        match2 = re.search(r'(\d+)\s*(?:บาท|บ\.)', query_lower)
        if match2:
            return int(match2.group(1))
        return None

    def _detect_query_intents(self, query: str) -> List[str]:
        q_lower = query.lower()
        detected = []
        for intent_tag, kw_list in INTENT_MAP_KEYWORDS.items():
            if any(kw in q_lower for kw in kw_list):
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
        female_query_kws = ["ผู้หญิง", "หญิง", "สำหรับผู้หญิง", "คุณผู้หญิง", "women", "woman", "สาว", "สาวๆ", "สวย", "น่ารัก", "น่ารักๆ", "คิ้วท์"]
        male_query_kws = ["ผู้ชาย", "ชาย", "สำหรับผู้ชาย", "คุณผู้ชาย", "men", "man", "หล่อ", "หล่อๆ", "แมน"]
        
        has_female = any(kw in q_lower for kw in female_query_kws)
        has_male = any(kw in q_lower for kw in male_query_kws)
        
        if has_male and not has_female:
            return "male"
        if has_female and not has_male:
            return "female"
        return None

    def _detect_query_popular(self, query: str) -> bool:
        q_lower = query.lower()
        return any(kw in q_lower for kw in POPULAR_KEYWORDS)

    def search_products(self, raw_query: str, top_k: int = 15, k_constant: int = 60, return_dict: bool = False) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Main entry point for product retrieval. Combines BM25 and Vector DB search 
        using Reciprocal Rank Fusion (RRF), with integrated Intent Boost, Color Match Boost,
        Gender Filtering, Sales Volume Boost, and Smart Price Fallback.
        """
        if not self.documents:
            return []

        max_price = self._extract_max_price(raw_query)
        detected_intents = self._detect_query_intents(raw_query)
        requested_colors = self._detect_query_colors(raw_query)
        requested_gender = self._detect_query_gender(raw_query)
        requested_vibes = self._detect_query_style_vibes(raw_query)
        is_popular = self._detect_query_popular(raw_query)

        print(f"🔎 [Search Engine Debug] Query: '{raw_query}' ──► Popular Filter: '{is_popular}' | Gender Filter: '{requested_gender}' | Style Vibes: {requested_vibes} | Intents: {detected_intents} | Colors: {requested_colors} | Max Price: {max_price}")

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

        # 3. RRF Fusion Helper
        def compute_rrf(apply_price_filter: bool, apply_strict_intent: bool = True):
            scores = {}
            for bm25_rank, idx in enumerate(bm25_ranked_indices):
                doc_id = self.doc_ids[idx]
                meta = self.metadatas[idx]
                price = meta["price"]

                if apply_price_filter and max_price is not None and price > max_price:
                    continue

                item_gender = meta.get("gender", "unisex")
                if requested_gender == "male" and item_gender == "female":
                    continue
                elif requested_gender == "female" and item_gender == "male":
                    continue

                r_bm25 = bm25_rank + 1
                r_vec = vector_rank_map.get(doc_id, 9999)
                base_score = (1.0 / (k_constant + r_bm25)) + (1.0 / (k_constant + r_vec))

                item_haystack = f"{meta['name']} {meta['category']} {meta['fabric']} {meta['style']} {self.documents[idx]}".lower()

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

                # Color Match Boost (1.30x)
                color_boost = 1.0
                if requested_colors:
                    item_color_text = f"{meta['name']} {meta['colors'] or ''}".lower()
                    for req_col in requested_colors:
                        syn_list = COLOR_KEYWORDS_MAP.get(req_col, [req_col])
                        if any(syn in item_color_text for syn in syn_list):
                            color_boost = 1.30
                            break

                # Style Vibe Match Boost (1.35x)
                style_vibe_boost = 1.0
                requested_vibes = self._detect_query_style_vibes(raw_query)
                if requested_vibes:
                    for req_vibe in requested_vibes:
                        syn_list = STYLE_VIBE_KEYWORDS_MAP.get(req_vibe, [req_vibe])
                        if any(syn in item_haystack for syn in syn_list):
                            style_vibe_boost = 1.35
                            break

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

                # Demographic Demotion Factors for broad queries
                query_lower = raw_query.lower()
                query_has_kids = any(k in query_lower for k in ["เด็ก", "kid", "kids", "อนุบาล", "ลูก"])
                query_has_crop = any(k in query_lower for k in ["crop", "ครอป", "เอวลอย"])

                item_is_kids = "kid" in item_haystack or "เด็ก" in item_haystack
                item_is_crop = "crop" in item_haystack or "ครอป" in item_haystack

                kids_boost = 0.15 if (item_is_kids and not query_has_kids) else 1.0
                crop_boost = 0.40 if (item_is_crop and not query_has_crop) else 1.0

                # Sales Volume / Popularity Match Boost
                sales_vol = meta.get("sales_volume", 0)
                sales_vol_boost = 1.0
                if is_popular:
                    sales_vol_boost = 1.0 + min(np.log1p(sales_vol) * 0.25, 1.8)
                else:
                    sales_vol_boost = 1.0 + min(np.log1p(sales_vol) * 0.02, 0.15)

                final_score = base_score * intent_boost * color_boost * style_vibe_boost * gender_match_boost * kids_boost * crop_boost * sales_vol_boost

                scores[doc_id] = {
                    "score": final_score,
                    "metadata": meta
                }
            return scores

        # 1. Search with strict budget and strict intent constraint
        strict_scores = compute_rrf(apply_price_filter=True, apply_strict_intent=True)
        sorted_strict = sorted(strict_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        strict_items = [res[1]["metadata"] for res in sorted_strict]

        fallback_message = None

        if len(strict_items) >= top_k or (max_price is None and not detected_intents):
            final_items = strict_items[:top_k]
        else:
            # 2. Smart Fallback: Relax price constraint while keeping category/intent intact
            relaxed_scores = compute_rrf(apply_price_filter=False, apply_strict_intent=True)
            sorted_relaxed = sorted(relaxed_scores.items(), key=lambda x: x[1]["score"], reverse=True)
            relaxed_items = [res[1]["metadata"] for res in sorted_relaxed]

            strict_ids = {p["product_id"] for p in strict_items}
            needed = top_k - len(strict_items)
            additional_items = [p for p in relaxed_items if p["product_id"] not in strict_ids][:needed]

            final_items = strict_items + additional_items

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

            if len(strict_items) > 0 and len(additional_items) > 0:
                fallback_message = f"พบ{intent_label}ตรงตามงบประมาณ {len(strict_items)} รายการ และขอแนะนำรุ่นสไตล์เดียวกันในงบใกล้เคียงเพิ่มเติมครับ:"
            elif len(strict_items) == 0 and len(final_items) > 0:
                fallback_message = f"ไม่พบ{intent_label}ในงบประมาณดังกล่าว แต่ขอแนะนำรุ่นสไตล์เดียวกันในงบใกล้เคียงที่สุดให้ครับ:"

        if return_dict:
            return {
                "products": final_items,
                "fallback_message": fallback_message,
                "strict_count": len(strict_items)
            }

        return final_items

    def rrf_hybrid_search(self, raw_query: str, top_k: int = 15) -> List[Dict[str, Any]]:
        """Alias for search_products for backwards compatibility."""
        return self.search_products(raw_query=raw_query, top_k=top_k)

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
        return selected_items
