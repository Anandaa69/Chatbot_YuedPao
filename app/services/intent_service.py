"""
Intent Service Engine for YuedPao Chatbot
Includes Tier 0 (Spell Correction), Tier 1 (Priority Rules), Tier 2.5 (ChromaDB Few-Shot Vector Lookup), and Tier 3 (BERT Passage Fallback).
"""

import json
import os
import re
import time
from typing import Dict, Any, Tuple, List, Optional

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None

try:
    from pythainlp.tokenize import word_tokenize
    from pythainlp.corpus import thai_stopwords
except ImportError:
    word_tokenize = None
    thai_stopwords = None


ADJACENT_KEYS = {
    'เ': ['แ', 'ร', 'ี', '้', '่'],
    'แ': ['เ', 'ฟ', 'ห', 'อ'],
    'ก': ['ด', 'ฟ', 'ห', 'ว', 'ิ'],
    'ด': ['ก', 'เ', 'แ', '้', '่', 'ท'],
    '้': ['่', 'ด', 'เ', 'า', 'ส'],
    '่': ['้', 'ด', 'เ', 'า', 'ส', 'เอก'],
    'อ': ['ิ', 'ท', 'แ', 'ิ', 'ส', 'ม'],
    'ร': ['เ', 'น', 'ี', 'ส', 'ย']
}


class IntentService:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
        
        self.data_dir = data_dir
        self.domain_vocab = self._load_domain_vocab()
        self.stop_words = self._load_stopwords()
        self.ground_truth = self._load_ground_truth()
        
        # Load BERT model
        self.bert_model = None
        if SentenceTransformer:
            try:
                self.bert_model = SentenceTransformer('intfloat/multilingual-e5-small')
            except Exception as e:
                print(f"⚠️ Warning: Could not load BERT model: {e}")
                
        # Setup ChromaDB Few-Shot Vector Store
        self.chroma_collection = None
        if chromadb and self.bert_model and self.ground_truth:
            try:
                self.chroma_client = chromadb.Client()
                self.chroma_collection = self.chroma_client.get_or_create_collection("intent_few_shot")
                self._index_fewshot_data()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize ChromaDB: {e}")
                
        # Cache Passages Embedding for Tier 3 Fallback
        self.INTENT_PASSAGES = {
            "product_search": "passage: ซื้อเสื้อ หาเสื้อ ขอดูเสื้อ สั่งซื้อเสื้อผ้า เสื้อยืด กางเกง เสื้อโปโล เสื้อเชิ้ต ราคาสินค้า สี ไซส์ ทรงเสื้อ มีงบ มีราคา ไม่เกิน",
            "size_recommendation": "passage: สอบถามไซส์ แนะนำไซส์เสื้อ ขนาดเสื้อ รอบอก สัดส่วนความสูงและน้ำหนัก ไซส์ไหนดี ใส่ไซส์อะไร เหมาะกับไซส์อะไร",
            "fabric_comparison": "passage: สอบถามเนื้อผ้า เปรียบเทียบคุณสมบัติผ้า ผ้าต่างกันยังไง ซักแล้วยับไหม ผ้านุ่ม ระบายอากาศ ดีกว่ายังไง คุณสมบัติของผ้า"
        }
        self.intent_classes = list(self.INTENT_PASSAGES.keys())
        self.passage_embeddings = None
        if self.bert_model:
            self.passage_embeddings = self.bert_model.encode(list(self.INTENT_PASSAGES.values()), convert_to_tensor=True)

    def _load_domain_vocab(self) -> List[str]:
        path = os.path.join(self.data_dir, "domain_vocab.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return list(set(
                data.get("brand_colors", []) +
                data.get("product_styles", []) +
                data.get("fabric_technologies", []) +
                data.get("apparel_types", [])
            ))
        return ["เสื้อยืด", "คอกลม", "คอวี", "โปโล", "กางเกง", "Ultrasoft", "Non-iron", "Oversize", "Crop"]

    def _load_stopwords(self) -> set:
        raw_stopwords = set(thai_stopwords()) if thai_stopwords else set()
        PRESERVED_KEYWORDS = {"ไม่เกิน", "งบ", "ราคา", "ประมาณ", "สูง", "หนัก", "อก", "รอบอก", "ไซส์", "ต่าง", "ยังไง", "ผ้า", "ดีกว่า", "คุณสมบัติ", "หด", "ยับ"}
        POLITE_PARTICLES = {"ครับ", "ค่ะ", "จ้า", "นะ", "หน่อย", "ด้วย", "มั้ย", "ไหม", "จ๊ะ", "ะ", "ขอ", "อยาก", "ได้"}
        return (raw_stopwords - PRESERVED_KEYWORDS) | POLITE_PARTICLES

    def _load_ground_truth(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "nlp_ground_truth.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _index_fewshot_data(self):
        if not self.chroma_collection or not self.ground_truth:
            return
        if self.chroma_collection.count() > 0:
            return
            
        docs = [f"query: {item['query']}" for item in self.ground_truth]
        embeddings = self.bert_model.encode(docs, convert_to_tensor=False).tolist()
        ids = [f"gt_{i}" for i in range(len(self.ground_truth))]
        metadatas = [{"intent": item["expected_intent"], "query": item["query"]} for item in self.ground_truth]
        
        self.chroma_collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=[item['query'] for item in self.ground_truth]
        )

    def _custom_edit_distance(self, s1: str, s2: str) -> float:
        s1, s2 = s1.lower(), s2.lower()
        m, n = len(s1), len(s2)
        dp = [[0.0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = float(i)
        for j in range(n + 1):
            dp[0][j] = float(j)
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    char1, char2 = s1[i-1], s2[j-1]
                    sub_cost = 0.5 if (char1 in ADJACENT_KEYS and char2 in ADJACENT_KEYS[char1]) else 1.0
                    dp[i][j] = min(dp[i-1][j] + 1.0, dp[i][j-1] + 1.0, dp[i-1][j-1] + sub_cost)
        return dp[m][n]

    def _correct_word(self, word: str, max_dist: float = 1.5) -> str:
        if not word or len(word) <= 1 or word.isdigit():
            return word
        word_lower = word.lower()
        for dw in self.domain_vocab:
            if dw.lower() == word_lower:
                return dw
        candidates = [dw for dw in self.domain_vocab if abs(len(dw) - len(word)) <= 1]
        if not candidates:
            return word
        best_match = word
        min_dist = float('inf')
        for dw in candidates:
            dist = self._custom_edit_distance(word, dw)
            if dist < min_dist:
                min_dist = dist
                best_match = dw
        return best_match if min_dist <= max_dist else word

    def correct_spelling(self, sentence: str) -> Tuple[str, float]:
        start_t = time.perf_counter()
        if not word_tokenize:
            return sentence, 0.0
            
        tokens = word_tokenize(sentence, engine="newmm")
        filtered_tokens = [t for t in tokens if t.strip() and t.lower() not in self.stop_words]
        if not filtered_tokens:
            filtered_tokens = tokens
        corrected_tokens = [self._correct_word(st) for st in filtered_tokens]
        corrected_sentence = " ".join(corrected_tokens)
        latency_ms = (time.perf_counter() - start_t) * 1000.0
        return corrected_sentence, latency_ms

    def predict_intent(self, raw_query: str) -> Dict[str, Any]:
        start_t = time.perf_counter()
        corrected_query, spell_time = self.correct_spelling(raw_query)
        raw_lower = raw_query.lower()
        
        # --- Tier 1 Priority Rules ---
        is_size_fitting = bool(
            re.search(r'(?:สูง|หนัก)\s*\d+', raw_lower) or
            re.search(r'(?:รอบอก|อก)\s*(?:ประมาณ\s*)?\d+.*(?:ใส่|ควร|แนะนำ|ไซส์|อะไร)', raw_lower) or
            re.search(r'(?:ไซส์|ขนาด)(?:อะไร|ไหน|เท่าไหร่|ดี|เหมาะ)', raw_lower) or
            re.search(r'(?:ใส่|เลือก|คำนวณ|แนะนำ)\s*(?:ไซส์|ขนาด)', raw_lower) or
            re.search(r'เปรียบเทียบไซส์', raw_lower)
        )
        if is_size_fitting and not re.search(r'(?:ไม่เกิน|งบ|ราคา|บาท)', raw_lower):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return {
                "intent": "size_recommendation",
                "tier_used": "Tier 1: Priority Rule (Size)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            }
            
        fabric_triggers = ["ต่างกันยังไง", "ต่างกับ", "ดีกว่ายังไง", "คุณสมบัติ", "ซักแล้ว", "หดไหม", "ไม่ยับและไม่ต้องรีด", "มีแบบไหนบ้าง", "มีรุ่นไหนบ้าง", "ระบายอากาศได้ดีที่สุด", "ทนทานแค่ไหน", "ดูแลยังไง", "เป็นยังไงบ้าง", "ดีมั้ย", "นุ่มแค่ไหน", "ยืดหยุ่นได้แค่ไหน", "เหมาะสำหรับ", "เหมาะกับคนที่"]
        if any(ft in raw_lower for ft in fabric_triggers) and not re.search(r'(?:ไม่เกิน|งบ|\d+\s*บาท)', raw_lower):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return {
                "intent": "fabric_comparison",
                "tier_used": "Tier 1: Priority Rule (Fabric)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            }
            
        product_triggers = ["ไม่เกิน", "งบ", "บาท", "ขอดู", "อยากได้", "หาเสื้อ", "มีเสื้อ", "ราคาประมาณ", "โปรโมชัน", "ลดราคา", "สักตัว"]
        if any(pt in raw_lower for pt in product_triggers):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return {
                "intent": "product_search",
                "tier_used": "Tier 1: Priority Rule (Product)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            }

        # --- Tier 2.5: ChromaDB Few-Shot Vector Search ---
        if self.chroma_collection and self.bert_model:
            query_emb = self.bert_model.encode(f"query: {raw_query}", convert_to_tensor=False).tolist()
            results = self.chroma_collection.query(
                query_embeddings=[query_emb],
                n_results=1
            )
            if results and results.get("distances") and results["distances"][0]:
                dist = results["distances"][0][0]
                similarity = 1.0 - dist
                top_intent = results["metadatas"][0][0]["intent"]
                if similarity >= 0.70:
                    total_time = (time.perf_counter() - start_t) * 1000.0
                    return {
                        "intent": top_intent,
                        "tier_used": "Tier 2.5: ChromaDB Few-Shot Vector",
                        "corrected_query": corrected_query,
                        "confidence": float(similarity),
                        "latency_ms": total_time
                    }

        # --- Tier 3: BERT Passage Fallback ---
        if self.bert_model and self.passage_embeddings is not None:
            query_text = f"query: {corrected_query}"
            query_embedding = self.bert_model.encode(query_text, convert_to_tensor=True)
            cosine_scores = util.cos_sim(query_embedding, self.passage_embeddings)[0]
            best_idx = int(cosine_scores.argmax())
            total_time = (time.perf_counter() - start_t) * 1000.0
            return {
                "intent": self.intent_classes[best_idx],
                "tier_used": "Tier 3: BERT Passage Match",
                "corrected_query": corrected_query,
                "confidence": float(cosine_scores[best_idx]),
                "latency_ms": total_time
            }

        # Fallback
        total_time = (time.perf_counter() - start_t) * 1000.0
        return {
            "intent": "product_search",
            "tier_used": "Tier Default Fallback",
            "corrected_query": corrected_query,
            "confidence": 0.5,
            "latency_ms": total_time
        }
