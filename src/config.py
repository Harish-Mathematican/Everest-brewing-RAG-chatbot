"""
#Gyan Labs - Enterprise RAG Global Configuration
================================================
Centralized configuration parameters for document chunking, embedding models,
vector store persist paths, intent routing, and LLM inference providers.

DISCLAIMER:
Developed exclusively for educational, research, and open-source demonstration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "enterprise_docs"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
DB_PATH = DATA_DIR / "enterprise_analytics.db"

# Ensure directories exist
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Chunking & Preprocessing Settings
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", 150))

# Embedding Settings
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION_NAME = "gyanlabs_enterprise_knowledge"

# LLM Inference Providers
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "llama-3.3-70b-versatile")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 1024))

# Retrieval & Ranking Parameters
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 4))
SCORE_THRESHOLD = float(os.getenv("SIMILARITY_SCORE_THRESHOLD", 0.45))
USE_MMR = os.getenv("USE_MMR", "true").lower() == "true"
MMR_LAMBDA = 0.7
