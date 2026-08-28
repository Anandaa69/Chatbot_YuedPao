"""
Shared Model Loader Singleton Utility for YuedPao Chatbot
Prevents redundant reloading of HuggingFace SentenceTransformer models across multiple services.
"""

import threading
from typing import Optional, Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class ModelLoader:
    _lock = threading.Lock()
    _embedding_models: dict = {}

    @classmethod
    def get_embedding_model(cls, model_name: str = "intfloat/multilingual-e5-small") -> Optional[Any]:
        """
        Thread-safe singleton getter for SentenceTransformer models.
        Returns the cached model instance if already loaded.
        """
        if SentenceTransformer is None:
            return None

        if model_name not in cls._embedding_models:
            with cls._lock:
                if model_name not in cls._embedding_models:
                    try:
                        cls._embedding_models[model_name] = SentenceTransformer(model_name)
                    except Exception as e:
                        print(f"⚠️ Warning: ModelLoader failed to load '{model_name}': {e}")
                        return None

        return cls._embedding_models.get(model_name)
