"""
#Gyan Labs - Chroma & In-Memory Hybrid Vector Store
===================================================
Manages document indexing, vector embeddings, similarity search,
and Maximal Marginal Relevance (MMR) re-ranking with persistence.
"""

from typing import List, Dict, Any, Optional, Tuple
import math
import json
import os
from pathlib import Path
from uuid import uuid4
from src.ingestion.text_splitter import DocumentChunk
from src.vectorstore.embeddings import BaseEmbeddingModel, HuggingFaceSentenceEmbeddings


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


class VectorRecord:
    def __init__(self, doc_id: str, content: str, embedding: List[float], metadata: Dict[str, Any]):
        self.doc_id = doc_id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorRecord":
        return cls(
            doc_id=data["doc_id"],
            content=data["content"],
            embedding=data["embedding"],
            metadata=data.get("metadata", {})
        )


class HybridVectorStore:
    def __init__(
        self,
        collection_name: str = "gyanlabs_knowledge",
        embedding_function: Optional[BaseEmbeddingModel] = None,
        persist_directory: Optional[str] = None
    ):
        self.collection_name = collection_name
        self.embedding_function = embedding_function or HuggingFaceSentenceEmbeddings()
        self.persist_directory = persist_directory
        self.records: List[VectorRecord] = []

        if self.persist_directory:
            os.makedirs(self.persist_directory, exist_ok=True)
            self._load_from_disk()

    def _get_store_file_path(self) -> Path:
        return Path(self.persist_directory) / f"{self.collection_name}_store.json"

    def _load_from_disk(self):
        file_path = self._get_store_file_path()
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = [VectorRecord.from_dict(r) for r in data]
            except Exception as e:
                print(f"Warning: Could not load vectorstore from {file_path}: {e}")

    def persist(self):
        if self.persist_directory:
            file_path = self._get_store_file_path()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in self.records], f, indent=2)

    def add_documents(self, documents: List[DocumentChunk], ids: Optional[List[str]] = None) -> List[str]:
        if not documents:
            return []

        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_function.embed_documents(texts)
        generated_ids = ids or [str(uuid4()) for _ in range(len(documents))]

        for doc, emb, doc_id in zip(documents, embeddings, generated_ids):
            record = VectorRecord(
                doc_id=doc_id,
                content=doc.page_content,
                embedding=emb,
                metadata=doc.metadata
            )
            self.records.append(record)

        self.persist()
        return generated_ids

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Performs semantic vector search with cosine similarity scoring.
        """
        if not self.records:
            return []

        query_vec = self.embedding_function.embed_query(query)
        scored_results = []

        for r in self.records:
            # Metadata filter check
            if filter_metadata:
                match = all(r.metadata.get(k) == v for k, v in filter_metadata.items())
                if not match:
                    continue

            score = cosine_similarity(query_vec, r.embedding)
            if score >= score_threshold:
                chunk = DocumentChunk(content=r.content, metadata=r.metadata)
                scored_results.append((chunk, score))

        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:k]

    def mmr_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.7
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Maximal Marginal Relevance (MMR) search for diversity and non-redundancy.
        """
        if not self.records:
            return []

        query_vec = self.embedding_function.embed_query(query)
        candidates = []

        for idx, r in enumerate(self.records):
            sim = cosine_similarity(query_vec, r.embedding)
            candidates.append((idx, sim))

        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = candidates[:fetch_k]

        selected_indices = []
        selected_records = []

        while len(selected_indices) < min(k, len(candidates)):
            best_score = -float("inf")
            best_cand_idx = None
            best_cand_pos = None

            for cand_idx, query_sim in candidates:
                if cand_idx in selected_indices:
                    continue

                cand_rec = self.records[cand_idx]
                max_redundancy = 0.0
                if selected_records:
                    max_redundancy = max(
                        cosine_similarity(cand_rec.embedding, sel.embedding)
                        for sel in selected_records
                    )

                # MMR score formula
                mmr_score = lambda_mult * query_sim - (1.0 - lambda_mult) * max_redundancy
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_cand_idx = cand_idx
                    best_cand_pos = query_sim

            if best_cand_idx is not None:
                selected_indices.append(best_cand_idx)
                rec = self.records[best_cand_idx]
                selected_records.append(rec)

        results = []
        for idx in selected_indices:
            r = self.records[idx]
            sim = cosine_similarity(query_vec, r.embedding)
            results.append((DocumentChunk(content=r.content, metadata=r.metadata), sim))

        return results

    def reset(self):
        self.records.clear()
        if self.persist_directory:
            file_path = self._get_store_file_path()
            if file_path.exists():
                os.remove(file_path)

    def count(self) -> int:
        return len(self.records)

    def get_indexed_sources(self) -> List[str]:
        sources = set()
        for r in self.records:
            s = r.metadata.get("source") or r.metadata.get("title")
            if s:
                sources.add(s)
        return sorted(list(sources))
