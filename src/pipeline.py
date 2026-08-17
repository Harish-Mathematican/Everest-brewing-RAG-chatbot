"""
#Gyan Labs - Unified Enterprise RAG Pipeline
============================================
The central orchestrator coordinating document ingestion, semantic chunking,
hybrid vector storage, intent routing, SQL querying, and grounded LLM generation.
"""

from typing import List, Dict, Any, Optional
import time
from pathlib import Path

from src.config import (
    DOCS_DIR,
    VECTORSTORE_DIR,
    DB_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RESULTS,
    SCORE_THRESHOLD,
    USE_MMR,
    MMR_LAMBDA
)
from src.ingestion import RecursiveTextSplitter, UniversalDocumentLoader, WebURLLoader
from src.vectorstore import HybridVectorStore, HuggingFaceSentenceEmbeddings
from src.router import SemanticIntentRouter
from src.generation import RAGGenerationChain, SQLAnalyticsAgent


class EnterpriseRAGPipeline:
    def __init__(
        self,
        vectorstore_dir: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        self.vectorstore_dir = vectorstore_dir or str(VECTORSTORE_DIR)
        self.db_path = db_path or str(DB_PATH)

        # 1. Initialize Embeddings & Vector Store
        self.embedding_model = HuggingFaceSentenceEmbeddings()
        self.vector_store = HybridVectorStore(
            collection_name="gyanlabs_enterprise_knowledge",
            embedding_function=self.embedding_model,
            persist_directory=self.vectorstore_dir
        )

        # 2. Ingestion Tools
        self.text_splitter = RecursiveTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        self.doc_loader = UniversalDocumentLoader()
        self.url_loader = WebURLLoader()

        # 3. Router, Generator & SQL Agent
        self.router = SemanticIntentRouter(embedding_function=self.embedding_model)
        self.rag_chain = RAGGenerationChain()
        self.sql_agent = SQLAnalyticsAgent(db_path=self.db_path)

        # If vectorstore is empty, auto-ingest default enterprise docs
        if self.vector_store.count() == 0 and Path(DOCS_DIR).exists():
            self.ingest_directory(str(DOCS_DIR))

    def ingest_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Scrapes, chunks, and indexes web articles from URLs.
        """
        docs = self.url_loader.load_urls(urls)
        chunks = self.text_splitter.split_documents(docs)
        ids = self.vector_store.add_documents(chunks)
        return {
            "urls_processed": len(docs),
            "chunks_indexed": len(chunks),
            "total_store_count": self.vector_store.count()
        }

    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """
        Loads, chunks, and indexes a single local document (Markdown, Text, PDF, JSON, CSV).
        """
        docs = self.doc_loader.load_file(file_path)
        chunks = self.text_splitter.split_documents(docs)
        ids = self.vector_store.add_documents(chunks)
        return {
            "file": Path(file_path).name,
            "chunks_indexed": len(chunks),
            "total_store_count": self.vector_store.count()
        }

    def ingest_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        Recursively ingests all supported documents in a directory.
        """
        docs = self.doc_loader.load_directory(dir_path)
        chunks = self.text_splitter.split_documents(docs)
        ids = self.vector_store.add_documents(chunks)
        return {
            "documents_loaded": len(docs),
            "chunks_indexed": len(chunks),
            "total_store_count": self.vector_store.count()
        }

    def query(
        self,
        user_query: str,
        force_route: Optional[str] = None,
        top_k: int = TOP_K_RESULTS
    ) -> Dict[str, Any]:
        """
        Main query entrypoint: routes intent, retrieves context/SQL, and synthesizes answers.
        """
        start_time = time.time()

        # Step 1: Semantic Intent Routing
        if force_route:
            route, route_confidence = force_route, 1.0
        else:
            route, route_confidence = self.router.route_query(user_query)

        # Step 2: Branch based on Route
        if route == "small_talk":
            answer = self.rag_chain.generate_small_talk_answer(user_query)
            return {
                "route": "small_talk",
                "route_confidence": route_confidence,
                "answer": answer,
                "sources": [],
                "confidence_score": 0.99,
                "latency_seconds": round(time.time() - start_time, 3)
            }

        elif route == "fast_faq":
            faq_ans = self.router.get_faq_answer(user_query)
            if faq_ans:
                return {
                    "route": "fast_faq",
                    "route_confidence": route_confidence,
                    "answer": faq_ans,
                    "sources": [{"source": "#Gyan Labs Enterprise FAQ", "score": 1.0, "preview": "Official FAQ"}],
                    "confidence_score": 1.0,
                    "latency_seconds": round(time.time() - start_time, 3)
                }

        elif route == "structured_sql":
            sql_res = self.sql_agent.generate_and_execute(user_query)
            # Format tabular answer
            rows = sql_res.get("rows", [])
            cols = sql_res.get("columns", [])
            formatted_table = f"**Executed SQL Query:** `{sql_res['sql']}`\n\n"
            if rows:
                header = "| " + " | ".join(cols) + " |"
                sep = "| " + " | ".join(["---"] * len(cols)) + " |"
                data_rows = []
                for r in rows[:10]:
                    data_rows.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
                formatted_table += header + "\n" + sep + "\n" + "\n".join(data_rows)
            else:
                formatted_table += "No records returned from analytics database."

            return {
                "route": "structured_sql",
                "route_confidence": route_confidence,
                "answer": formatted_table,
                "sql_data": sql_res,
                "sources": [{"source": "enterprise_analytics.db", "score": 0.98, "preview": sql_res["sql"]}],
                "confidence_score": 0.95,
                "latency_seconds": round(time.time() - start_time, 3)
            }

        # Step 3: Deep Knowledge Retrieval (Default)
        if USE_MMR:
            retrieved = self.vector_store.mmr_search(
                query=user_query,
                k=top_k,
                fetch_k=20,
                lambda_mult=MMR_LAMBDA
            )
        else:
            retrieved = self.vector_store.similarity_search(
                query=user_query,
                k=top_k,
                score_threshold=SCORE_THRESHOLD
            )

        rag_output = self.rag_chain.generate_rag_answer(user_query, retrieved)
        rag_output["route"] = "knowledge_retrieval"
        rag_output["route_confidence"] = route_confidence
        rag_output["retrieved_chunks_count"] = len(retrieved)
        return rag_output

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Returns real-time pipeline status, vector counts, and indexed sources.
        """
        return {
            "total_vectors": self.vector_store.count(),
            "indexed_sources": self.vector_store.get_indexed_sources(),
            "embedding_model": self.embedding_model.__class__.__name__,
            "database_tables": ["compute_nodes", "ai_projects", "model_telemetry"]
        }
