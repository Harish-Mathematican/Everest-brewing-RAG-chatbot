from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    query: str = Field(..., example="What is the standard fermentation temperature for Everest Premium Lager?")
    department: Optional[str] = Field("All", example="Brewing")
    top_k: Optional[int] = Field(3, ge=1, le=10)

class RAGSource(BaseModel):
    id: str
    department: str
    title: str
    subsection: str
    score: float
    excerpt: str

class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[RAGSource]
    department_filter: str
    confidence_score: float
    execution_time_ms: float

class LiveDocumentIngest(BaseModel):
    id: str
    department: str
    title: str
    subsection: str
    content: str

class TelemetryData(BaseModel):
    timestamp: str
    brewing: Dict[str, Any]
    production: Dict[str, Any]
    logistics: Dict[str, Any]
    administration: Dict[str, Any]
    hr_compliance: Dict[str, Any]
