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
        
        self.bert_model = None
        if SentenceTransformer:
            try:
                self.bert_model = SentenceTransformer('intfloat/multilingual-e5-small')
            except Exception as e:
                print(f"⚠️ Warning: Could not load SentenceTransformer in PromotionService: {e}")

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
        if not os.path.exists(self.db_path):
            print(f"⚠️ Warning: Database file not found at {self.db_path}")
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='promotions';")
        if not cursor.fetchone():
            conn.close()
            return

        cursor.execute("""
            SELECT promo_id, product_id, name, deal_type, deal_title, discount_tag, deal_price, original_price, image_url, product_url, description, colors
            FROM promotions
        """)
        rows = cursor.fetchall()
        conn.close()

        self.promotions = []
        self.documents = []
        self.doc_ids = []
        self.metadatas = []

        for r in rows:
            p_id = r[1]
            p_name = r[2]
            d_type = r[3]
            d_title = r[4]
            disc_tag = r[5] or ""
            d_price = r[6]
            orig_price = r[7] or d_price
            img_url = r[8] or ""
            p_url = r[9] or ""
            desc = r[10] or ""
            colors = r[11] or ""

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
                "product_id": p_id,
                "name": p_name,
                "deal_title": d_title,
                "discount_tag": disc_tag,
                "deal_price": d_price,
                "original_price": orig_price,
                "image_url": img_url,
                "product_url": p_url,
                "colors": colors
            })

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
                
                # Reset collection for fast atomic refresh
                if collection_name in [c.name for c in self.chroma_client.list_collections()]:
                    self.chroma_client.delete_collection(collection_name)
                    
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

    def search_promotions(self, raw_query: str, top_k: int = 5, k_constant: int = 60) -> List[Dict[str, Any]]:
        """
        Performs Hybrid RRF Search across promotion deal items.
        """
        if not self.documents:
            return []

        # 1. BM25 score
        bm25_scores = [0.0] * len(self.documents)
        if self.bm25_model and word_tokenize:
            query_tokens = [t.strip().lower() for t in word_tokenize(raw_query, engine="newmm") if t.strip()]
            bm25_scores = self.bm25_model.get_scores(query_tokens)
        bm25_ranked_indices = np.argsort(bm25_scores)[::-1]

        # 2. Vector score
        vector_rank_map = {}
        if self.chroma_collection and self.bert_model:
            query_emb = self.bert_model.encode(f"query: {raw_query}", convert_to_tensor=False).tolist()
            chroma_results = self.chroma_collection.query(query_embeddings=[query_emb], n_results=len(self.documents))
            vector_rank_map = {doc_id: rank + 1 for rank, doc_id in enumerate(chroma_results["ids"][0])}

        # 3. RRF Fusion
        scores = {}
        for bm25_rank, idx in enumerate(bm25_ranked_indices):
            doc_id = self.doc_ids[idx]
            meta = self.metadatas[idx]
            r_bm25 = bm25_rank + 1
            r_vec = vector_rank_map.get(doc_id, 9999)
            rrf_score = (1.0 / (k_constant + r_bm25)) + (1.0 / (k_constant + r_vec))
            scores[doc_id] = {
                "score": rrf_score,
                "metadata": meta
            }

        sorted_rrf = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)[:top_k]
        return [res[1]["metadata"] for res in sorted_rrf]
