"""
#Gyan Labs - Enterprise RAG REST API (FastAPI)
==============================================
Production-grade RESTful endpoints for multi-source document ingestion,
semantic vector search, text-to-SQL execution, and RAG synthesis.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from src.pipeline import EnterpriseRAGPipeline

app = FastAPI(
    title="#Gyan Labs Enterprise RAG API",
    description="High-performance REST API for Retrieval-Augmented Generation, Semantic Routing, and Text-to-SQL Analytics.",
    version="1.0.0"
)

# Initialize pipeline
pipeline = EnterpriseRAGPipeline()


class QueryRequest(BaseModel):
    query: str = Field(..., example="What is the zero-trust security policy at Gyan Labs?")
    force_route: Optional[str] = Field(None, example="knowledge_retrieval")
    top_k: Optional[int] = Field(4, example=4)


class IngestURLsRequest(BaseModel):
    urls: List[str] = Field(..., example=["https://en.wikipedia.org/wiki/Retrieval-augmented_generation"])


class SQLRequest(BaseModel):
    query: str = Field(..., example="List all active GPU nodes")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "#Gyan Labs Enterprise RAG Platform"}


@app.get("/stats")
def get_stats():
    return pipeline.get_system_stats()


@app.post("/query")
def execute_query(req: QueryRequest):
    try:
        res = pipeline.query(user_query=req.query, force_route=req.force_route, top_k=req.top_k)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/urls")
def ingest_urls(req: IngestURLsRequest):
    try:
        res = pipeline.ingest_urls(req.urls)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sql")
def execute_sql(req: SQLRequest):
    try:
        res = pipeline.sql_agent.generate_and_execute(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
