"""
#Gyan Labs - Unit Test Suite for Enterprise RAG Platform
=========================================================
Tests ingestion, text splitters, vector store, MMR search,
semantic intent routing, SQL agent, and end-to-end RAG pipeline.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion import RecursiveTextSplitter, UniversalDocumentLoader, WebURLLoader
from src.vectorstore import HybridVectorStore, DenseSemanticEmbeddings
from src.router import SemanticIntentRouter
from src.generation import SQLAnalyticsAgent, RAGGenerationChain
from src.pipeline import EnterpriseRAGPipeline


@pytest.fixture
def splitter():
    return RecursiveTextSplitter(chunk_size=200, chunk_overlap=30)


@pytest.fixture
def vector_store():
    embedder = DenseSemanticEmbeddings(vector_dim=128)
    store = HybridVectorStore(collection_name="test_collection", embedding_function=embedder)
    return store


@pytest.fixture
def pipeline(tmp_path):
    return EnterpriseRAGPipeline(
        vectorstore_dir=str(tmp_path / "test_vecs"),
        db_path=str(tmp_path / "test_db.sqlite")
    )


def test_recursive_text_splitter(splitter):
    sample_text = (
        "# Introduction\n\n"
        "Retrieval-Augmented Generation (RAG) is a technique for enhancing LLM responses.\n\n"
        "It combines dense semantic vector search with prompt engineering to reduce hallucinations.\n\n"
        "## Core Principles\n\n"
        "Grounding context with verified sources ensures enterprise accuracy."
    )
    chunks = splitter.split_text(sample_text)
    assert len(chunks) >= 2
    assert all(len(c) <= 350 for c in chunks)


def test_document_loader(tmp_path):
    loader = UniversalDocumentLoader()
    doc_file = tmp_path / "sample_doc.md"
    doc_file.write_text("# Test Title\nThis is a sample document content for testing.", encoding="utf-8")

    loaded = loader.load_file(str(doc_file))
    assert len(loaded) == 1
    assert "sample document" in loaded[0]["content"]
    assert loaded[0]["metadata"]["source"] == "sample_doc.md"


def test_vector_store_and_mmr(vector_store, splitter):
    docs = [
        {"content": "Zero-trust architecture enforces cryptographic hardware tokens like YubiKeys.", "metadata": {"source": "security.md"}},
        {"content": "NVIDIA H100 GPU clusters are used for distributed training of large models.", "metadata": {"source": "gpu.md"}},
        {"content": "Maximal Marginal Relevance (MMR) balances relevance and diversity in RAG search.", "metadata": {"source": "rag.md"}}
    ]
    chunks = splitter.split_documents(docs)
    ids = vector_store.add_documents(chunks)
    assert len(ids) == len(chunks)
    assert vector_store.count() == len(chunks)

    # Search
    results = vector_store.similarity_search("Tell me about GPU training clusters", k=2)
    assert len(results) > 0
    assert "GPU" in results[0][0].page_content or "H100" in results[0][0].page_content

    # MMR Search
    mmr_res = vector_store.mmr_search("Zero-trust hardware security", k=2)
    assert len(mmr_res) > 0


def test_intent_router():
    router = SemanticIntentRouter()

    # Small-talk
    route, conf = router.route_query("Hello there! Good morning.")
    assert route == "small_talk"

    # SQL query
    route, conf = router.route_query("How many compute nodes do we have in total?")
    assert route == "structured_sql"

    # Knowledge retrieval
    route, conf = router.route_query("Explain the hybrid cloud deployment architecture and zero-trust security")
    assert route == "knowledge_retrieval"


def test_sql_agent(tmp_path):
    db_file = tmp_path / "test_analytics.db"
    agent = SQLAnalyticsAgent(db_path=str(db_file))

    res = agent.execute_query("SELECT * FROM compute_nodes;")
    assert "columns" in res
    assert len(res["rows"]) >= 6

    # Test natural language translation
    nl_res = agent.generate_and_execute("List all active GPU nodes")
    assert len(nl_res["rows"]) > 0


def test_end_to_end_pipeline(pipeline):
    # Test small talk
    res_chat = pipeline.query("Hi there!")
    assert res_chat["route"] == "small_talk"
    assert len(res_chat["answer"]) > 0

    # Test SQL query
    res_sql = pipeline.query("Show all GPU compute nodes")
    assert res_sql["route"] == "structured_sql"
    assert "Executed SQL Query" in res_sql["answer"]

    # Test Knowledge Query
    res_rag = pipeline.query("What is the zero-trust security policy at Gyan Labs?")
    assert res_rag["route"] == "knowledge_retrieval"
    assert "answer" in res_rag
    assert res_rag["latency_seconds"] >= 0
