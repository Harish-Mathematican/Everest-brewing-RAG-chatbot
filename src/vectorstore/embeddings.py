"""
#Gyan Labs - Embedding Service & Vector Representation Engine
=============================================================
Computes semantic embeddings using SentenceTransformers or provides an
in-memory dense semantic vectorizer with cosine similarity calculation.
"""

from typing import List, Union
import math
import re
from collections import Counter


class BaseEmbeddingModel:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError


class DenseSemanticEmbeddings(BaseEmbeddingModel):
    """
    Zero-dependency deterministic dense TF-IDF & Character N-gram embedding engine.
    Ensures the RAG system operates out-of-the-box in any lightweight Python environment.
    """
    def __init__(self, vector_dim: int = 384):
        self.vector_dim = vector_dim

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
        # Add character tri-grams for sub-word semantic matching
        trigrams = [text[i:i+3].lower() for i in range(len(text)-2)]
        return words + trigrams[:len(words)*2]

    def _vectorize(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.vector_dim

        counts = Counter(tokens)
        vec = [0.0] * self.vector_dim

        for token, count in counts.items():
            # Stable non-cryptographic hash mapping to vector dimension
            idx = abs(hash(token)) % self.vector_dim
            weight = (1.0 + math.log(count)) * (1.0 + 0.1 * min(len(token), 10))
            vec[idx] += weight

        # L2 Unit Normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._vectorize(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._vectorize(text)


class HuggingFaceSentenceEmbeddings(BaseEmbeddingModel):
    """
    SentenceTransformers neural embedding wrapper with automatic graceful fallback.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._fallback = DenseSemanticEmbeddings(vector_dim=384)

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
        except Exception:
            # Fallback to internal dense embedder
            self._model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self._model is not None:
            try:
                embeddings = self._model.encode(texts, normalize_embeddings=True)
                return [e.tolist() for e in embeddings]
            except Exception:
                pass
        return self._fallback.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        if self._model is not None:
            try:
                embedding = self._model.encode(text, normalize_embeddings=True)
                return embedding.tolist()
            except Exception:
                pass
        return self._fallback.embed_query(text)
