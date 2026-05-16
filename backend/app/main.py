from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging

from app.services.retriever import PaperRetriever
from app.services.generator import RAGGenerator
from app.services.ml_services import ml_classifier

logger = logging.getLogger(__name__)

# --- NEW: Lifespan Manager for efficient memory loading ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PaperVault Services...")
    # Load ML models into RAM once on startup
    ml_classifier.load_models()
    yield
    logger.info("Shutting down PaperVault Services...")

# Initialize FastAPI with the lifespan
app = FastAPI(
    title="PaperVault API",
    description="End-to-End RAG API for AI Research Papers",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG services (You can eventually move these into the lifespan manager too!)
logger.info("Initializing Vector Retriever...")
retriever = PaperRetriever()

logger.info("Initializing LangGraph Generator...")
generator = RAGGenerator()

# --- Pydantic Schema for the ML Endpoint ---
class AbstractRequest(BaseModel):
    abstract: str

@app.get("/")
def health_check():
    return {"status": "PaperVault Backend is actively running."}

@app.get("/api/rag")
def ask_papervault(
    q: str = Query(..., description="The natural language question to ask"),
    limit: int = Query(3, description="Number of papers to retrieve for context"),
    think: bool = Query(
        False,
        description="Enable model reasoning trace (Ollama think=true; requires a thinking-capable model)",
    ),
):
    """Executes the full Retrieval-Augmented Generation pipeline."""
    logger.info(f"RAG Request received: '{q}' (think={think})")

    retrieved_papers = retriever.search(query=q, limit=limit)
    result = generator.generate_answer(query=q, retrieved_papers=retrieved_papers, think=think)

    return {
        "query": q,
        "answer": result["answer"],
        "thinking": result.get("thinking") or None,
        "sources": retrieved_papers,
    }

# --- NEW: Machine Learning Classification Endpoint ---
@app.post("/api/predict")
def predict_paper_category(request: AbstractRequest):
    """Predicts the scientific domain of an ArXiv abstract using the Stacking Ensemble."""
    if not request.abstract.strip():
        raise HTTPException(status_code=400, detail="Abstract text cannot be empty.")
        
    try:
        result = ml_classifier.predict_category(request.abstract)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal ML processing error.")