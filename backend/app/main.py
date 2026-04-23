from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services.retriever import PaperRetriever
from app.services.generator import RAGGenerator
import logging

logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="PaperVault API",
    description="End-to-End RAG API for AI Research Papers",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize our services
logger.info("Initializing Vector Retriever...")
retriever = PaperRetriever()

logger.info("Initializing LangGraph Generator...")
generator = RAGGenerator()

@app.get("/")
def health_check():
    return {"status": "PaperVault Backend is actively running."}

@app.get("/api/rag")
def ask_papervault(
    q: str = Query(..., description="The natural language question to ask"), 
    limit: int = Query(3, description="Number of papers to retrieve for context")
):
    """
    Executes the full Retrieval-Augmented Generation pipeline.
    """
    logger.info(f"RAG Request received: '{q}'")
    
    # 1. Retrieve the context
    retrieved_papers = retriever.search(query=q, limit=limit)
    
    # 2. Generate the answer via Ollama
    answer = generator.generate_answer(query=q, retrieved_papers=retrieved_papers)
    
    # 3. Return the complete package to the frontend
    return {
        "query": q,
        "answer": answer,
        "sources": retrieved_papers
    }