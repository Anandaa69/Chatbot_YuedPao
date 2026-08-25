"""
Product Repository & Search Service (DB Queries & Fair Top 5 Sampling)
"""

import os
import re
import sqlite3
import random
import numpy as np
from typing import List, Dict, Any, Optional

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

# --- Synonym & Preprocessing Dictionaries ---
FABRIC_SYNONYMS = {
    "Classic Cotton": "ผ้าฝ้าย ฝ้าย ฝ้ายธรรมชาติ",
    "Ultrasoft": "ผ้านุ่ม นุ่มพิเศษ ไม่ยับ ไม่ต้องรีด อัลตราซอฟ อลตราซอฟ อัลตาซอฟ อัลตราซอฟท์ โคตรนุ่ม โคตนุ่ม ใส่สบาย",
    "Tailor Cool": "ผ้าเย็น ระบายอากาศ ใส่ไม่ร้อน เทเลอร์คูล เทเลอร์ คูล ทเลอคูล ใส่สบาย",
    "Ecotech": "ผ้านุ่มรักษ์โลก"
}

COLOR_SYNONYMS = {
    "Cream": "ครีม สีครีม Vanilla ครีมมี่ Creamy",
    "Creamy": "ครีม สีครีม Vanilla ครีมมี่ Creamy",
    "Vanilla": "ครีม สีครีม Vanilla ครีมมี่ Creamy",
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

PERSONA_SYNONYMS = {
    "Oversize": "เสื้อยืด ทรงหลวม อกใหญ่ เผื่อไหล่ ไหล่ตก คนอ้วน ตั้งครรภ์ ตัวใหญ่ ใส่สบาย วันพักผ่อน คอกลม โอเวอไซ โอเวอร์ไซ โอเวอร์ไซส์ โอเวอไซส์ ผู้ชาย ผู้หญิง ชาย หญิง",
    "Kid": "เด็ก เสื้อเด็ก ของขวัญเด็ก เด็กอนุบาล ลายน่ารัก kidซ คิดส์ คิด",
    "Polo": "ใส่ทำงาน พนักงานบริษัท สุภาพ งานสังสรรค์ ประชุม ปกโปโล เสื้อโปโล ปกคอ",
    "Crop": "เสื้อครอป น่ารัก สาวๆ เที่ยวทะเล คอกลม",
    "Running": "ใส่วิ่ง ออกกำลังกาย ระบายความร้อน อากาศไทย ไม่ร้อน รันนิ่ง",
    "Tie Dye": "มัดย้อม ซัมเมอร์ เที่ยว สีสดใส มัดยอม ฟัดย้อม",
    "Sleeveless": "แขนกุด อากาศร้อน ไม่อึดอัด เสื้อกล้าม",
    "Running Roulette": "รันนิ่งรูเล็ต รันนิ่ง รูเล็ต เสื้อฟอก วินเทจ"
}

STYLE_SYNONYMS = {
    "Round Neck": "คอกลม คอกม คอกลมปกติ",
    "V Neck": "คอวี วี",
    "Long Sleeve": "แขนยาว แขนยาวผู้ชาย แขนยาวผู้หญิง",
    "Short Sleeve": "แขนสั้น แขนสั้นผู้ชาย แขนสั้นผู้หญิง",
    "Unisex": "ผู้ชาย ผู้หญิง ชาย หญิง Unisex ใส่ได้ทั้งชายและหญิง"
}

KODNUM_SYNONYMS = {
    "Kodnum": "โคตรนุ่ม โคตนุ่ม โคตรนุม โคตนุม"
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
        # Determine paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.db_path = os.path.join(base_dir, "yuedpao_chatbot.db")
        
        # Load SentenceTransformer model
        self.bert_model = None
        if SentenceTransformer:
            try:
                self.bert_model = SentenceTransformer('intfloat/multilingual-e5-small')
            except Exception as e:
                print(f"⚠️ Warning: Could not load SentenceTransformer in ProductService: {e}")

        # Fetch products from SQLite
        self.products = []
        self.doc_ids = []
        self.documents = []
        self.metadatas = []
        self._load_products_from_db()

        # Initialize ChromaDB Vector Store (in-memory)
        self.chroma_collection = None
        if chromadb and self.bert_model and self.documents:
            try:
                self.chroma_client = chromadb.Client()
                collection_name = "yuedpao_products_e5_search"
                if collection_name in [c.name for c in self.chroma_client.list_collections()]:
                    self.chroma_client.delete_collection(collection_name)
                self.chroma_collection = self.chroma_client.create_collection(
                    name=collection_name, 
                    metadata={"hnsw:space": "cosine"}
                )
                self._index_chromadb()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize ChromaDB in ProductService: {e}")

        # Initialize BM25 Model
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
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT product_id, name, category, fabric_collection, style_fit, price, description, image_url FROM products")
        product_rows = cursor.fetchall()
        
        cursor.execute("SELECT product_id, GROUP_CONCAT(DISTINCT color_name) FROM product_variants GROUP BY product_id")
        variant_color_map = dict(cursor.fetchall())
        conn.close()

        self.products = []
        for r in product_rows:
            p_id = r[0]
            colors_str = variant_color_map.get(p_id, "") or ""
            self.products.append({
                "product_id": p_id,
                "name": r[1],
                "category": r[2],
                "fabric": r[3],
                "style": r[4],
                "price": r[5],
                "description": r[6] or "",
                "image_url": r[7] or "",
                "colors": colors_str
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

            doc_text = (
                f"passage: สินค้า: {clean_name} | หมวดหมู่: {clean_cat} | "
                f"เทคโนโลยีผ้า: {p['fabric']} | ทรงเสื้อ: {p['style']} | ราคา: ฿{p['price']} | "
                f"{colors_info}{synonym_str} | รายละเอียดและจุดเด่น: {clean_desc}"
            )
            self.documents.append(doc_text)
            self.doc_ids.append(f"prod_{p['product_id']}")
            
            # Align metadata for keyword compatibility in downstream filters/evaluations
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

            self.metadatas.append({
                "product_id": p["product_id"],
                "name": p["name"],
                "category": cat_val,
                "fabric": p["fabric"],
                "style": p["style"],
                "price": p["price"],
                "image_url": p["image_url"],
                "colors": color_val
            })

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
        match = re.search(r'(?:ไม่เกิน|งบ|ราคาประมาณ|งบประมาณ|ราคา)\s*(\d+)', query_lower)
        if match:
            return int(match.group(1))
        match2 = re.search(r'(\d+)\s*(?:บาท|บ\.)', query_lower)
        if match2:
            return int(match2.group(1))
        return None

    def search_products(self, raw_query: str, top_k: int = 15, k_constant: int = 60) -> List[Dict[str, Any]]:
        """
        Main entry point for product retrieval. Combines BM25 and Vector DB search 
        using Reciprocal Rank Fusion (RRF), with integrated hard price filtering.
        
        Returns a list of raw product dictionaries containing metadata ready for carousel rendering.
        """
        # Fallback if indices are not built
        if not self.documents:
            return []

        max_price = self._extract_max_price(raw_query)

        # 1. BM25 ranks
        bm25_scores = [0.0] * len(self.documents)
        if self.bm25_model:
            query_tokens = self._bm25_tokenizer(raw_query)
            bm25_scores = self.bm25_model.get_scores(query_tokens)
        bm25_ranked_indices = np.argsort(bm25_scores)[::-1]

        # 2. Vector ranks
        vector_rank_map = {}
        if self.chroma_collection and self.bert_model:
            query_emb = self.bert_model.encode(f"query: {raw_query}", convert_to_tensor=False).tolist()
            chroma_results = self.chroma_collection.query(query_embeddings=[query_emb], n_results=len(self.documents))
            vector_rank_map = {doc_id: rank + 1 for rank, doc_id in enumerate(chroma_results["ids"][0])}

        # 3. RRF fusion with hard price constraints
        rrf_scores = {}
        for bm25_rank, idx in enumerate(bm25_ranked_indices):
            doc_id = self.doc_ids[idx]
            meta = self.metadatas[idx]
            price = meta["price"]

            # Filter out products exceeding budget
            if max_price is not None and price > max_price:
                continue

            r_bm25 = bm25_rank + 1
            r_vec = vector_rank_map.get(doc_id, 9999)
            
            rrf_scores[doc_id] = {
                "score": (1.0 / (k_constant + r_bm25)) + (1.0 / (k_constant + r_vec)),
                "metadata": meta
            }

        # Sort and return up to top_k products
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:top_k]
        return [res[1]["metadata"] for res in sorted_rrf]

    def get_fair_top5_recommendations(self, candidate_pool: List[Dict[str, Any]], session_history: List[str]) -> List[Dict[str, Any]]:
        """
        Filters out items recently shown in the current user session,
        then randomly samples up to 5 items to generate a fresh, fair recommendation list.
        Modifies session_history in-place (keeps last 10 product IDs).
        """
        if not candidate_pool:
            return []

        # 1. Exclude recently shown product IDs
        fresh_pool = [
            item for item in candidate_pool 
            if item["product_id"] not in session_history
        ]
        
        # 2. Fallback to full pool if fresh pool is depleted (< 5)
        if len(fresh_pool) < 5:
            fresh_pool = candidate_pool
            
        # 3. Fair Random Sampling
        sample_size = min(len(fresh_pool), 5)
        selected_items = random.sample(fresh_pool, sample_size)
        
        # 4. Update session history cache (keep last 10 product_ids)
        new_shown_ids = [item["product_id"] for item in selected_items]
        session_history.extend(new_shown_ids)
        
        # Mutate list to keep the last 10 elements in-place
        del session_history[:-10]
        
        return selected_items
