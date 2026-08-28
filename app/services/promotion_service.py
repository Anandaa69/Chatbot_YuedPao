"""
Promotion Service Engine for YuedPao Chatbot
Manages SQLite 'promotions' table data, incremental ChromaDB indexing ('yuedpao_promotions_e5'),
and RRF Hybrid Search for promotion deals and discounts.
"""

import os
import re
import sys
import sqlite3
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

from app.utils.model_loader import ModelLoader

try:
    from pythainlp.tokenize import word_tokenize
except ImportError:
    word_tokenize = None


class PromotionService:
    _instance = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern to prevent reloading models on every instantiation."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, "yuedpao_chatbot.db")
        self.chroma_path = os.path.join(base_dir, "data", "chroma")
        
        # Load BERT model via ModelLoader singleton
        self.bert_model = ModelLoader.get_embedding_model()

        self.promotions = []
        self.documents = []
        self.doc_ids = []
        self.metadatas = []
        
        self.chroma_client = None
        self.chroma_collection = None
        self.bm25_model = None
        self.bm25_corpus = []

        self.reload_and_index()

    def _load_promotions_from_db(self):
        self.promotions = []
        self.documents = []
        self.doc_ids = []
        self.metadatas = []

        if not os.path.exists(self.db_path):
            print(f"⚠️ Warning: Database file not found at {self.db_path}")
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Load promotions
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promotions';")
        if cursor.fetchone():
            cursor.execute("""
                SELECT p.promo_id, p.product_id, p.name, p.deal_type, p.deal_title, p.discount_tag, p.deal_price, p.original_price, p.image_url, p.product_url, p.description, p.colors, pr.image_url AS prod_img
                FROM promotions p
                LEFT JOIN products pr ON p.product_id = pr.product_id
            """)
            rows = cursor.fetchall()

            # Pre-fetch fallback image catalog from products table
            cursor.execute("SELECT name, image_url FROM products WHERE image_url IS NOT NULL AND image_url != ''")
            product_catalog = cursor.fetchall()

            for r in rows:
                p_id = r[1]
                p_name = r[2]
                d_type = r[3]
                d_title = r[4]
                disc_tag = r[5] or ""
                d_price = r[6]
                orig_price = r[7] or d_price
                raw_img = r[8] or ""
                prod_img = r[12] or ""
                p_url = r[9] or ""
                desc = r[10] or ""
                colors = r[11] or ""

                # Smart Image Lookup: Prefer direct product image -> category keyword match -> default logo
                img_url = ""
                if prod_img and not prod_img.endswith(".svg"):
                    img_url = prod_img
                elif raw_img and not raw_img.endswith(".svg") and "free-delivery" not in raw_img:
                    img_url = raw_img
                else:
                    # Keyword fallback search in products catalog
                    p_name_lower = p_name.lower()
                    for cat_name, cat_img in product_catalog:
                        cat_lower = cat_name.lower()
                        if any(kw in p_name_lower and kw in cat_lower for kw in ["jeans", "ยีนส์", "polo", "longsleeve", "crop", "cargo", "short"]):
                            img_url = cat_img
                            break
                    if not img_url:
                        img_url = "https://mp-static.yuedpao.com/images/logo.png"

                promo_item = {
                    "promo_id": r[0],
                    "product_id": p_id,
                    "name": p_name,
                    "deal_type": d_type,
                    "deal_title": d_title,
                    "discount_tag": disc_tag,
                    "deal_price": d_price,
                    "original_price": orig_price,
                    "image_url": img_url,
                    "product_url": p_url,
                    "description": desc,
                    "colors": colors
                }
                self.promotions.append(promo_item)

                clean_desc = desc.replace("\n", " ").strip()
                if len(clean_desc) > 120:
                    clean_desc = clean_desc[:117] + "..."

                doc_text = (
                    f"passage: โปรโมชันดีลพิเศษ: {p_name} | หัวข้อดีล: {d_title} | ป้ายส่วนลด: {disc_tag} | "
                    f"ราคาพิเศษ: ฿{d_price} (ปกติ ฿{orig_price}) | เฉดสี: {colors} | จุดเด่น: {clean_desc}"
                )
                self.documents.append(doc_text)
                self.doc_ids.append(f"promo_{r[0]}")
                self.metadatas.append({
                    "type": "promotion",
                    "product_id": p_id,
                    "name": p_name,
                    "deal_type": d_type,
                    "deal_title": d_title,
                    "discount_tag": disc_tag,
                    "deal_price": d_price,
                    "original_price": orig_price,
                    "image_url": img_url,
                    "product_url": p_url,
                    "colors": colors
                })

        # 2. Load coupons
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coupons';")
        if cursor.fetchone():
            cursor.execute("""
                SELECT coupon_id, badge_title, badge_bg_color, discount_title, coupon_code, min_spend, expiry_date, valid_duration, detailed_condition, eligibility_tag
                FROM coupons
            """)
            c_rows = cursor.fetchall()
            for r in c_rows:
                c_id, b_title, b_color, d_title, code, min_sp, exp, duration, cond, tag = r
                doc_text = (
                    f"passage: คูปองส่วนลด YuedPao: {b_title} | โค้ดส่วนลด: {code} | หัวข้อส่วนลด: {d_title} | "
                    f"ขั้นต่ำ: {min_sp} บาท | เงื่อนไขเพิ่มเติม: {cond} | ระยะเวลาใช้งาน: {duration} | สิทธิ์ผู้ใช้: {tag}"
                )
                self.documents.append(doc_text)
                self.doc_ids.append(f"coupon_{c_id}")
                self.metadatas.append({
                    "type": "coupon",
                    "coupon_id": c_id,
                    "badge_title": b_title,
                    "badge_bg_color": b_color,
                    "discount_title": d_title,
                    "coupon_code": code,
                    "min_spend": min_sp,
                    "expiry_date": exp,
                    "valid_duration": duration,
                    "detailed_condition": cond,
                    "eligibility_tag": tag
                })

        conn.close()

    def reload_and_index(self):
        """
        Fast Incremental Refresh: Reads promotions from SQLite DB and updates ChromaDB + BM25 index (< 0.5s).
        """
        self._load_promotions_from_db()

        if chromadb and self.bert_model and self.documents:
            try:
                os.makedirs(self.chroma_path, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
                collection_name = "yuedpao_promotions_e5"
                
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
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize ChromaDB in PromotionService: {e}")

        if self.documents and word_tokenize:
            try:
                from rank_bm25 import BM25Okapi
                self.bm25_corpus = [[t.strip().lower() for t in word_tokenize(doc.replace("passage: ", ""), engine="newmm") if t.strip()] for doc in self.documents]
                self.bm25_model = BM25Okapi(self.bm25_corpus)
            except Exception as e:
                print(f"⚠️ Warning: Could not build BM25 Index in PromotionService: {e}")

    def search_promotions(self, raw_query: str, top_k: int = 5, k_constant: int = 60, deal_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Performs Hybrid RRF Search across promotion deal items.
        """
        if not self.documents:
            return []

        # Detect deal_type_filter if not explicitly passed
        if not deal_type_filter:
            raw_lower = raw_query.lower()
            if any(k in raw_lower for k in ["ประจำวัน", "วันนี้", "แฟลชเซล", "flash sale"]):
                deal_type_filter = "daily_deal"
            elif any(k in raw_lower for k in ["ประจำเดือน", "เดือนนี้"]):
                deal_type_filter = "monthly_deal"

        # 1. BM25 score
        bm25_scores = [0.0] * len(self.documents)
        if self.bm25_model and word_tokenize:
            query_tokens = [t.strip().lower() for t in word_tokenize(raw_query, engine="newmm") if t.strip()]
            bm25_scores = self.bm25_model.get_scores(query_tokens)
        bm25_ranked_indices = np.argsort(bm25_scores)[::-1]

        # 2. Vector score
        vector_rank_map = {}
        if self.chroma_collection and self.bert_model:
            try:
                query_emb = self.bert_model.encode(f"query: {raw_query}", convert_to_tensor=False).tolist()
                chroma_results = self.chroma_collection.query(query_embeddings=[query_emb], n_results=len(self.documents))
                vector_rank_map = {doc_id: rank + 1 for rank, doc_id in enumerate(chroma_results["ids"][0])}
            except Exception as e:
                print(f"⚠️ ChromaDB Promotion Query Warning: {e}. Re-initializing collection...")
                try:
                    collection_name = "yuedpao_promotions_e5"
                    self.chroma_collection = self.chroma_client.get_or_create_collection(
                        name=collection_name, 
                        metadata={"hnsw:space": "cosine"}
                    )
                    if self.chroma_collection.count() != len(self.documents):
                        self.reload_and_index()
                    chroma_results = self.chroma_collection.query(query_embeddings=[query_emb], n_results=len(self.documents))
                    vector_rank_map = {doc_id: rank + 1 for rank, doc_id in enumerate(chroma_results["ids"][0])}
                except Exception as retry_e:
                    print(f"⚠️ ChromaDB Promotion Recovery Failed: {retry_e}")

        # 3. RRF Fusion
        scores = {}
        for bm25_rank, idx in enumerate(bm25_ranked_indices):
            doc_id = self.doc_ids[idx]
            meta = self.metadatas[idx]
            
            # Apply deal_type filter if specified
            if deal_type_filter:
                if meta.get("type") != "promotion" or meta.get("deal_type") != deal_type_filter:
                    continue

            r_bm25 = bm25_rank + 1
            r_vec = vector_rank_map.get(doc_id, 9999)
            rrf_score = (1.0 / (k_constant + r_bm25)) + (1.0 / (k_constant + r_vec))
            scores[doc_id] = {
                "score": rrf_score,
                "metadata": meta
            }

        sorted_rrf = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:top_k]
        return [res[1]["metadata"] for res in sorted_rrf]

    def get_daily_deals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Direct Rule-Based SQL Query: Fetches Daily Deals (daily_deal) directly from SQLite DB (0% Vector uncertainty).
        """
        self._load_promotions_from_db()
        daily_items = [p for p in self.promotions if p.get("deal_type") == "daily_deal"]
        return daily_items[:limit]

    def get_monthly_deals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Direct Rule-Based SQL Query: Fetches Monthly Deals (monthly_deal) directly from SQLite DB (0% Vector uncertainty).
        """
        self._load_promotions_from_db()
        monthly_items = [p for p in self.promotions if p.get("deal_type") == "monthly_deal"]
        return monthly_items[:limit]

    def get_all_coupons(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Direct Rule-Based SQL Query: Fetches Coupon Tickets directly from SQLite DB.
        """
        self._load_promotions_from_db()
        coupon_items = [m for m in self.metadatas if m.get("type") == "coupon"]
        return coupon_items[:limit]
