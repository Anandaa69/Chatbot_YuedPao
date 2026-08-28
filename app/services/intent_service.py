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
    util = None

from app.utils.model_loader import ModelLoader

try:
    from pythainlp.tokenize import word_tokenize
    from pythainlp.corpus import thai_stopwords
    from pythainlp.soundex import soundex
except ImportError:
    word_tokenize = None
    thai_stopwords = None
    soundex = None


# Comprehensive Thai Kedmanee Keyboard Layout Proximity Matrix
ADJACENT_KEYS = {
    # Row 1 (Number Row)
    'ภ': ['ถ', 'ุ', 'ึ', '_', 'ๅ'],
    'ถ': ['ภ', 'ุ', 'พ'],
    'ุ': ['ภ', 'ึ', 'ะ', 'ั', 'ถ'],
    'ึ': ['ุ', 'ค', 'ั', 'ี'],
    'ค': ['ึ', 'ต', 'ี', 'ร'],
    'ต': ['ค', 'จ', 'ร', 'น'],
    'จ': ['ต', 'ข', 'น', 'ย'],
    'ข': ['จ', 'ช', 'ย', 'บ'],
    'ช': ['ข', 'บ', 'ล'],
    # Row 2 (Upper Row)
    'ๆ': ['ไ', 'ฟ', 'ๅ'],
    'ไ': ['ๆ', 'ำ', 'ฟ', 'ห'],
    'ำ': ['ไ', 'พ', 'ห', 'ก'],
    'พ': ['ำ', 'ะ', 'ก', 'ด', 'ถ'],
    'ะ': ['พ', 'ั', 'ด', 'เ', 'ุ'],
    'ั': ['ะ', 'ี', 'เ', '้', 'ึ'],
    'ี': ['ั', 'ร', '้', '่', 'ค'],
    'ร': ['ี', 'น', '่', 'า', 'ต'],
    'น': ['ร', 'ย', 'า', 'ส', 'จ'],
    'ย': ['น', 'บ', 'ส', 'ว', 'ข'],
    'บ': ['ย', 'ล', 'ว', 'ง', 'ช'],
    'ล': ['บ', 'ฃ', 'ง'],
    # Row 3 (Home Row)
    'ฟ': ['ห', 'ผ', 'ป', 'ๆ', 'ไ'],
    'ห': ['ฟ', 'ก', 'ป', 'แ', 'ไ', 'ำ'],
    'ก': ['ห', 'ด', 'แ', 'อ', 'ำ', 'พ'],
    'ด': ['ก', 'เ', 'อ', 'ิ', 'พ', 'ะ'],
    'เ': ['ด', '้', 'ิ', 'ื', 'ะ', 'ั'],
    '้': ['เ', '่', 'ื', 'ท', 'ั', 'ี'],
    '่': ['้', 'า', 'ท', 'ม', 'ี', 'ร'],
    'า': ['่', 'ส', 'ม', 'ใ', 'ร', 'น'],
    'ส': ['า', 'ว', 'ใ', 'ฝ', 'น', 'ย'],
    'ว': ['ส', 'ง', 'ฝ', 'ย', 'บ'],
    'ง': ['ว', 'ล', 'บ'],
    # Row 4 (Bottom Row)
    'ผ': ['ป', 'ฟ'],
    'ป': ['ผ', 'แ', 'ฟ', 'ห'],
    'แ': ['ป', 'อ', 'ห', 'ก', 'เ'],
    'อ': ['แ', 'ิ', 'ก', 'ด'],
    'ิ': ['อ', 'ื', 'ด', 'เ'],
    'ื': ['ิ', 'ท', 'เ', '้'],
    'ท': ['ื', 'ม', '้', '่'],
    'ม': ['ท', 'ใ', '่', 'า'],
    'ใ': ['ม', 'ฝ', 'า', 'ส'],
    'ฝ': ['ใ', 'ส', 'ว']
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
        
        # Load BERT model via ModelLoader singleton
        self.bert_model = ModelLoader.get_embedding_model()
                
        # Setup ChromaDB Few-Shot Vector Store in persistent root data/chroma directory
        self.chroma_collection = None
        if chromadb and self.bert_model and self.ground_truth:
            try:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                chroma_path = os.path.join(project_root, "data", "chroma")
                os.makedirs(chroma_path, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(path=chroma_path)
                self.chroma_collection = self.chroma_client.get_or_create_collection("intent_few_shot")
                self._index_fewshot_data()
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize ChromaDB: {e}")
                
        # Cache Passages Embedding for Tier 3 Fallback
        self.INTENT_PASSAGES = {
            "greeting": "passage: สวัสดี หวัดดี ดีจ้า ดีครับ ดีค่ะ hello hi ทักทาย มีใครอยู่ไหม บอทอยู่ไหม ช่วยได้ไหม ยินดีต้อนรับ เริ่มต้นใช้งาน",
            "product_search": "passage: ซื้อเสื้อ หาเสื้อ ขอดูเสื้อ อยากเห็นเสื้อ สั่งซื้อเสื้อผ้า เสื้อยืด กางเกง กระเป๋า ยีนส์ เสื้อโปโล เสื้อเชิ้ต ราคาสินค้า สี ไซส์ ทรงเสื้อ มีงบ มีราคา ไม่เกิน",
            "see_more_products": "passage: ขอดูเพิ่มเติม ดูเพิ่มเติม ขอดูเพิ่ม ขออีก ดูเพิ่ม ขอเพิ่ม ดูรุ่นอื่น ดูต่อ ขอเพิ่มอีก ขอดูอีก ถัดไป หน้าถัดไป",
            "size_recommendation": "passage: สอบถามไซส์ แนะนำไซส์เสื้อ ขนาดเสื้อ รอบอก สัดส่วนความสูงและน้ำหนัก ไซส์ไหนดี ใส่ไซส์อะไร เหมาะกับไซส์อะไร ส่วนสูง น้ำหนัก อก",
            "fabric_comparison": "passage: สอบถามเนื้อผ้า เปรียบเทียบคุณสมบัติผ้า ผ้าต่างกันยังไง ซักแล้วยับไหม ผ้านุ่ม ระบายอากาศ ดีกว่ายังไง คุณสมบัติของผ้า ระบายเหงื่อ สัมผัสเย็น ไม่ติดตัว ใส่ออกกำลังกาย",
            "coupon_ticket": "passage: คูปองส่วนลด โค้ดส่วนลด บัตรส่วนลด วอเชอร์ voucher code กดคัดลอกโค้ด สิทธิ์ส่วนลด คูปองยืดเปล่า",
            "promotion_deal": "passage: โปรโมชัน ดีลพิเศษ ประจำวัน ประจำเดือน แฟลชเซล flash sale ดีลเด็ด สินค้าลดราคา ส่งฟรี วันนี้ เดือนนี้",
            "random_recommendation": "passage: สุ่มแนะนำ สุ่มสินค้า สินค้าแนะนำ ลองดูอะไรดี เลือกให้หน่อย ไม่รู้จะซื้ออะไร แนะนำเสื้อ แนะนำตัวไหนดี"
        }
        self.intent_classes = list(self.INTENT_PASSAGES.keys())
        self.passage_embeddings = None
        if self.bert_model:
            self.passage_embeddings = self.bert_model.encode(list(self.INTENT_PASSAGES.values()), convert_to_tensor=True)

    def _load_domain_vocab(self) -> List[str]:
        path = os.path.join(self.data_dir, "domain_vocab.json")
        loaded_vocab = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded_vocab = (
                data.get("brand_colors", []) +
                data.get("product_styles", []) +
                data.get("fabric_technologies", []) +
                data.get("apparel_types", [])
            )
        core_vocab = [
            "เสื้อยืด", "ยืดเปล่า", "คอกลม", "คอวี", "โปโล", "เสื้อโปโล", "กางเกง", "กางเกงยีนส์", "กางเกงขาสั้น",
            "เด็ก", "เสื้อเด็ก", "ผู้หญิง", "ผู้ชาย", "เสื้อเชิ้ต", "กระเป๋า", "หมวก", "ถุงเท้า", "โอเวอร์ไซส์",
            "สีดำ", "สีขาว", "สีแดง", "สีครีม", "สีเขียว", "สีน้ำเงิน", "สีฟ้า", "สีชมพู", "สีเทา", "สีเหลือง", "สีส้ม", "สีม่วง", "สีชาไทย", "สีน้ำตาล",
            "Ultrasoft", "Tailor Cool", "Classic Cotton", "Ecotech", "Non-iron", "Oversize", "Crop", "BabyTee", "Babytee"
        ]
        return list(set(loaded_vocab + core_vocab))

    def _load_stopwords(self) -> set:
        raw_stopwords = set(thai_stopwords()) if thai_stopwords else set()
        PRESERVED_KEYWORDS = {
            "ไม่เกิน", "งบ", "ราคา", "ประมาณ", "สูง", "หนัก", "อก", "รอบอก", "ไซส์",
            "ต่าง", "ยังไง", "ผ้า", "ดีกว่า", "คุณสมบัติ", "หด", "ยับ", "ไม่", "ไม่ใช่",
            "วันนี้", "ประจำวัน", "เดือนนี้", "ประจำเดือน", "แฟลชเซล", "โค้ด", "คูปอง", "ดีล", "โปร"
        }
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
        if self.chroma_collection.count() == len(self.ground_truth):
            return
            
        # Re-index if ground truth dataset size changed
        try:
            self.chroma_client.delete_collection("intent_few_shot")
        except Exception:
            pass
        self.chroma_collection = self.chroma_client.create_collection(
            "intent_few_shot",
            metadata={"hnsw:space": "cosine"}
        )

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

    def _soundex_match(self, word: str) -> Optional[str]:
        """Phonetic soundex matching (LK82) against domain vocabulary."""
        if not soundex or len(word) <= 1 or word.isdigit():
            return None
        try:
            w_snd = soundex(word, engine="lk82")
            if not w_snd or w_snd == "0000":
                return None
            for dw in self.domain_vocab:
                if abs(len(dw) - len(word)) <= 2:
                    if soundex(dw, engine="lk82") == w_snd:
                        return dw
        except Exception:
            pass
        return None

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
        if not word or word.isdigit():
            return word
        
        TYPO_MAP = {
            "บืด": "ยืด",
            "บึด": "ยืด",
            "เสิ้อยืด": "เสื้อยืด",
            "เสื้อบืด": "เสื้อยืด",
            "เสื้อบึด": "เสื้อยืด",
            "เสือยืบ": "เสื้อยืด",
            "เสือยืด": "เสื้อยืด",
            "ยึดเป่า": "ยืดเปล่า",
            "ยึดเปล่า": "ยืดเปล่า",
            "ยืดเป่า": "ยืดเปล่า",
            "babytree": "babytee",
            "โอเวอไซ": "Oversize",
            "โอเวอร์ไซ": "Oversize",
            "อลตราซอฟ": "Ultrasoft",
            "อัลตราซอฟ": "Ultrasoft",
            "อันต้าซอบ": "Ultrasoft",
            "อันตร้าซอฟ": "Ultrasoft",
            "อันต้าซอฟ": "Ultrasoft",
            "ทเลอคูล": "Tailor Cool",
            "เสื้อเด": "เสื้อเด็ก",
            "เสื้อโปเล": "เสื้อโปโล",
            "โปเล": "โปโล",
            "เสื้อเปเล": "เสื้อโปโล",
            "เปเล": "โปโล",
            "เสื้อเปโล": "เสื้อโปโล",
            "เปโล": "โปโล",
            "โปลง": "โปโล",
            "สีดัม": "สีดำ",
            "สีคาว": "สีขาว",
            "เกงยีน": "กางเกงยีนส์",
            "เกงขาสั้น": "กางเกงขาสั้น"
        }
        word_lower = word.lower()
        if word_lower in TYPO_MAP:
            return TYPO_MAP[word_lower]
        if word in TYPO_MAP:
            return TYPO_MAP[word]

        if len(word) <= 1:
            return word

        for dw in self.domain_vocab:
            if dw.lower() == word_lower:
                return dw

        # 1. Thai Soundex matching
        snd_match = self._soundex_match(word)
        if snd_match:
            return snd_match

        # 2. Keyboard-aware weighted Levenshtein
        candidates = [dw for dw in self.domain_vocab if abs(len(dw) - len(word)) <= 2]
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
        if not sentence:
            return sentence, 0.0

        # Pre-tokenization Domain Phrase Normalization
        phrase_map = {
            "เสื้อบืด": "เสื้อยืด",
            "เสื้อบึด": "เสื้อยืด",
            "เสิ้อยืด": "เสื้อยืด",
            "เสื้อยึด": "เสื้อยืด",
            "เสือยืบ": "เสื้อยืด",
            "เสือยืด": "เสื้อยืด",
            "ยึดเป่า": "ยืดเปล่า",
            "ยืดเป่า": "ยืดเปล่า",
            "ยึดเปล่า": "ยืดเปล่า",
            "babytree": "babytee",
            "โอเวอไซ": "Oversize",
            "โอเวอร์ไซ": "Oversize",
            "อลตราซอฟ": "Ultrasoft",
            "อัลตราซอฟ": "Ultrasoft",
            "อันต้าซอบ": "Ultrasoft",
            "อันตร้าซอฟ": "Ultrasoft",
            "อันต้าซอฟ": "Ultrasoft",
            "สีดัม": "สีดำ",
            "สีคาว": "สีขาว",
            "โปลง": "โปโล",
            "ทเลอคูล": "Tailor Cool",
            "เทเลอร์คูล": "Tailor Cool",
            "ผ้านุม": "ผ้านุ่ม",
            "ยับยอก": "ยับยาก",
            "เกงยีน": "กางเกงยีนส์",
            "เบบี้ทีส์": "BabyTee",
            "คร็อป": "Crop",
            "เกงขาสั้น": "กางเกง",
            "คอกม": "คอกลม",
            "คอวึ": "คอวี",
            "ใส่วิ่งง": "ใส่วิ่ง",
            "แขนกุดด": "แขนกุด",
            "มัดย้อมม": "มัดย้อม",
            "คอปกก": "คอปก",
            # Kids / demographic typos
            "เสื้อ เด": "เสื้อเด็ก",
            "เสื้อเด": "เสื้อเด็ก",
            "เสื้อเด็ห": "เสื้อเด็ก",
            "เสิ้อเด็ก": "เสื้อเด็ก",
            "เด็ห": "เด็ก",
            "เด็กๆ": "เด็ก",
            "คิดส์": "เด็ก",
            "คิส": "เด็ก",
            "เดก": "เด็ก",
            "เด็ค": "เด็ก",
            "เดี่ยก": "เด็ก",
            # Polo typos
            "เสื้อโปเล": "เสื้อโปโล",
            "โปเล": "โปโล",
            "เสื้อเปเล": "เสื้อโปโล",
            "เปเล": "โปโล",
            "เสื้อเปโล": "เสื้อโปโล",
            "เปโล": "โปโล",
            "กางเกงวิ่ง": "กางเกงกีฬา",
            "เสื้อวิ่ง": "เสื้อออกกำลังกาย",
        }
        for typo, clean in phrase_map.items():
            if typo in sentence:
                sentence = sentence.replace(typo, clean)

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
        
        def _return_with_log(res_dict):
            print(f"🔍 [NLP Engine] Query: '{raw_query}' ──► Cleaned: '{res_dict['corrected_query']}' | Intent: '{res_dict['intent']}' | Tier: '{res_dict['tier_used']}' | Latency: {res_dict['latency_ms']:.2f}ms")
            return res_dict

        # --- Tier 0.5: Unsupported Category Guard ---
        unsupported_kws = ["รองเท้า", "นาฬิกา", "น้ำหอม", "แว่นตา", "เข็มขัด", "แหวน", "สร้อย", "ลิป", "กระเป๋าตังค์", "สเก็ตบอร์ด", "หูฟัง", "ตู้เย็น", "แก้วน้ำ", "หมอน", "เคสโทรศัพท์", "โน๊ตบุ๊ค"]
        has_unsupported = any(kw in raw_lower for kw in unsupported_kws) or bool(re.search(r'(?<!สี)ครีม', raw_lower))
        if has_unsupported:
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "product_search",
                "tier_used": "Tier 1: Priority Rule (Unsupported Guard)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

        # --- Tier 1 Priority Rules ---

        # --- Greeting Detection (Tier 1) ---
        greeting_triggers = [
            "สวัสดี", "หวัดดี", "ดีจ้า", "ดีครับ", "ดีค่ะ", "hello", "hi", "hey",
            "มีใครอยู่ไหม", "บอทอยู่ไหม", "อยู่ไหม", "ช่วยได้ไหม", "อยากถาม",
            "ยินดีต้อนรับ", "เริ่มต้น", "มีอะไรช่วยได้บ้าง", "ขอความช่วยเหลือ"
        ]
        # Greeting only when query is short and purely a greeting (no product keywords)
        product_hint_kws = ["เสื้อ", "กางเกง", "ราคา", "งบ", "สี", "ไซส์", "ผ้า", "ส่วนลด", "โปร"]
        is_pure_greeting = (
            any(gt in raw_lower for gt in greeting_triggers)
            and not any(pk in raw_lower for pk in product_hint_kws)
            and len(raw_query.strip()) <= 30
        )
        if is_pure_greeting:
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "greeting",
                "tier_used": "Tier 1: Priority Rule (Greeting)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

        search_help_triggers = ["วิธีการค้นหา", "วิธีค้นหา", "ค้นหายังไง", "วิธีค้นหาสินค้า", "ค้นหาทำยังไง", "ค้นหาอย่างไร"]
        if any(sht in raw_lower for sht in search_help_triggers):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "search_help",
                "tier_used": "Tier 1: Priority Rule (Search Help)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

        see_more_triggers = ["ขอดูเพิ่มเติม", "ดูเพิ่มเติม", "ขอดูเพิ่ม", "ขออีก", "ดูเพิ่ม", "ขอเพิ่ม", "ดูรุ่นอื่น", "ดูต่อ", "ขอเพิ่มอีก", "ขอดูอีก"]
        if any(smt in raw_lower for smt in see_more_triggers):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "see_more_products",
                "tier_used": "Tier 1: Priority Rule (See More)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

        is_size_fitting = bool(
            re.search(r'(?:สูง|หนัก)\s*\d+', raw_lower) or
            re.search(r'(?:รอบอก|อก)\s*(?:ประมาณ\s*)?\d+.*(?:ใส่|ควร|แนะนำ|ไซส์|อะไร)', raw_lower) or
            re.search(r'(?:ไซส์|ขนาด)(?:อะไร|ไหน|เท่าไหร่|ดี|เหมาะ)', raw_lower) or
            re.search(r'(?:ใส่|เลือก|คำนวณ|แนะนำ)\s*(?:ไซส์|ขนาด)', raw_lower) or
            re.search(r'เปรียบเทียบไซส์', raw_lower)
        )
        if is_size_fitting and not re.search(r'(?:ไม่เกิน|งบ|ราคา|บาท)', raw_lower):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "size_recommendation",
                "tier_used": "Tier 1: Priority Rule (Size)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })
            
        fabric_triggers = ["ต่างกันยังไง", "ต่างกับ", "ดีกว่ายังไง", "คุณสมบัติ", "ซักแล้ว", "หดไหม", "ไม่ยับและไม่ต้องรีด", "มีแบบไหนบ้าง", "มีรุ่นไหนบ้าง", "ระบายอากาศได้ดีที่สุด", "ทนทานแค่ไหน", "ดูแลยังไง", "เป็นยังไงบ้าง", "ดีมั้ย", "นุ่มแค่ไหน", "ยืดหยุ่นได้แค่ไหน", "เหมาะสำหรับ", "เหมาะกับคนที่"]
        if any(ft in raw_lower for ft in fabric_triggers) and not re.search(r'(?:ไม่เกิน|งบ|\d+\s*บาท)', raw_lower):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "fabric_comparison",
                "tier_used": "Tier 1: Priority Rule (Fabric)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })
            
        coupon_triggers = ["คูปอง", "โค้ด", "วอเชอร์", "voucher", "ส่วนลด"]
        if any(ct in raw_lower or ct in corrected_query for ct in coupon_triggers) and not re.search(r'(?:ไม่เกิน|งบ|\d+\s*บาท)', raw_lower):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "coupon_ticket",
                "tier_used": "Tier 1: Priority Rule (Coupon)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

        deal_triggers = ["แฟลชเซล", "flash sale", "ประจำวัน", "ประจำเดือน", "ดีลพิเศษ", "ดีล", "โปรโมชัน", "โปรโมชั่น", "โปรเด็ด", "ลดราคา", "โปร"]
        if any(dt in raw_lower or dt in corrected_query for dt in deal_triggers) and not re.search(r'(?:ไม่เกิน|งบ|\d+\s*บาท)', raw_lower):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "promotion_deal",
                "tier_used": "Tier 1: Priority Rule (Deal)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

        random_triggers = ["สุ่ม", "สุ่มแนะนำ", "แนะนำหน่อย", "สินค้าแนะนำ", "แนะนำเสื้อ", "ลองดูอะไรดี", "เลือกให้หน่อย", "ช่วยเลือก", "ไม่รู้จะซื้ออะไร", "ครั้งแรก", "พึ่งมา", "เพิ่งมา", "น่าสนใจ"]
        # If user is asking for general recommendation ("เพิ่งมาร้านนี้ครั้งแรกมีเสื้อน่าสนใจมั้ย"), route to random_recommendation unless specific spec/price is provided
        is_first_visit_recommendation = any(rt in raw_lower for rt in ["ครั้งแรก", "น่าสนใจ", "แนะนำหน่อย", "ไม่รู้จะซื้ออะไร"]) and not any(spec in raw_lower for spec in ["ราคา", "งบ", "ไม่เกิน", "บาท", "โปโล", "ยีนส์", "กระเป๋า", "สี", "เด็ก", "ผู้หญิง", "ผู้ชาย", "อก"])
        if any(rt in raw_lower for rt in ["สุ่ม", "สุ่มแนะนำ", "สินค้าแนะนำ", "ลองดูอะไรดี", "เลือกให้หน่อย", "ช่วยเลือก"]) or is_first_visit_recommendation:
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "random_recommendation",
                "tier_used": "Tier 1: Priority Rule (Random)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

        product_triggers = ["ไม่เกิน", "งบ", "บาท", "ขอดู", "อยากได้", "อยากเห็น", "หาเสื้อ", "มีเสื้อ", "ขอเสื้อ", "เนื้อผ้า", "ผ้า", "ราคาประมาณ", "สักตัว", "ขายดี", "ฮิต", "ยอดฮิต", "best seller", "นิยม", "กระเป๋า", "กางเกง", "ยีนส์", "โปโล", "เสื้อโปเล", "โปเล", "เสื้อเด็ก", "ครอป", "เบบี้ที", "บรา", "สปอร์ตบรา", "bra", "หมวก"]
        if any(pt in raw_lower or pt in corrected_query for pt in product_triggers):
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": "product_search",
                "tier_used": "Tier 1: Priority Rule (Product)",
                "corrected_query": corrected_query,
                "confidence": 1.0,
                "latency_ms": total_time
            })

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
                    return _return_with_log({
                        "intent": top_intent,
                        "tier_used": "Tier 2.5: ChromaDB Few-Shot Vector",
                        "corrected_query": corrected_query,
                        "confidence": float(similarity),
                        "latency_ms": total_time
                    })

        # --- Tier 3: BERT Passage Fallback ---
        if self.bert_model and self.passage_embeddings is not None:
            query_text = f"query: {corrected_query}"
            query_embedding = self.bert_model.encode(query_text, convert_to_tensor=True)
            cosine_scores = util.cos_sim(query_embedding, self.passage_embeddings)[0]
            best_idx = int(cosine_scores.argmax())
            total_time = (time.perf_counter() - start_t) * 1000.0
            return _return_with_log({
                "intent": self.intent_classes[best_idx],
                "tier_used": "Tier 3: BERT Passage Match",
                "corrected_query": corrected_query,
                "confidence": float(cosine_scores[best_idx]),
                "latency_ms": total_time
            })

        # Fallback
        total_time = (time.perf_counter() - start_t) * 1000.0
        return _return_with_log({
            "intent": "product_search",
            "tier_used": "Tier Default Fallback",
            "corrected_query": corrected_query,
            "confidence": 0.5,
            "latency_ms": total_time
        })
