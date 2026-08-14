import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Append backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import ChatRequest, ChatResponse, LiveDocumentIngest
from app.kb_loader import KBLoader
from app.rag_engine import RAGEngine
from app.live_telemetry import TelemetryManager

app = FastAPI(
    title="Everest Brewing RAG AI Platform & Operations Control Center",
    description="Enterprise Retrieval-Augmented Generation (RAG) AI Chatbot and Real-time Dashboard",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Engine and Telemetry Manager
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "everest_kb")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

kb_loader = KBLoader(DATA_DIR)
rag_engine = RAGEngine(kb_loader)
telemetry_mgr = TelemetryManager()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "company": "Everest Brewing Company",
        "kb_documents_count": len(kb_loader.documents),
        "engine": "Hybrid Vector-Semantic RAG v1.0"
    }

@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    try:
        telemetry = telemetry_mgr.get_live_telemetry()
        response = rag_engine.query(
            query=request.query,
            department=request.department or "All",
            top_k=request.top_k or 3,
            live_telemetry=telemetry["data"]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
def get_dashboard_metrics():
    telemetry = telemetry_mgr.get_live_telemetry()
    return {
        "company": "Everest Brewing Company - Operational Control Center",
        "timestamp": telemetry["timestamp"],
        "telemetry": telemetry["data"],
        "kb_summary": {
            "total_documents": len(kb_loader.documents),
            "departments": ["Logistics", "Brewing", "Production", "Administration", "Other"]
        }
    }

@app.post("/api/ingest")
def ingest_live_document(doc: LiveDocumentIngest):
    doc_dict = doc.dict()
    kb_loader.add_live_document(doc_dict)
    return {
        "message": f"Document '{doc.title}' successfully ingested into RAG Knowledge Base.",
        "id": doc.id,
        "total_kb_documents": len(kb_loader.documents)
    }

@app.post("/api/telemetry/update")
def update_telemetry(department: str, key: str, value: str):
    success = telemetry_mgr.update_telemetry_metric(department, key, value)
    if not success:
        raise HTTPException(status_code=400, detail=f"Department {department} not recognized.")
    return {"message": "Telemetry updated successfully", "telemetry": telemetry_mgr.get_live_telemetry()}

@app.get("/api/kb")
def get_kb_documents():
    return {"documents": kb_loader.documents}
