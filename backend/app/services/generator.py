import logging
import os
from typing import Dict, TypedDict

import httpx
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")


class GraphState(TypedDict):
    query: str
    context: str
    think: bool
    generation: str
    thinking: str


class RAGGenerator:
    def __init__(self):
        logger.info("Initializing Ollama (%s) and LangGraph...", OLLAMA_MODEL)

        workflow = StateGraph(GraphState)
        workflow.add_node("generate", self.generate_node)
        workflow.set_entry_point("generate")
        workflow.add_edge("generate", END)
        self.app = workflow.compile()

    def _ollama_chat(self, messages: list[dict], think: bool) -> tuple[str, str]:
        """Call Ollama /api/chat; returns (answer, thinking trace)."""
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "think": think,
            "options": {"temperature": 0.2},
        }
        url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        with httpx.Client(timeout=httpx.Timeout(300.0)) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        message = data.get("message", {})
        content = message.get("content", "") or ""
        thinking = message.get("thinking", "") or ""
        return content, thinking

    def generate_node(self, state: GraphState) -> Dict:
        query = state["query"]
        context = state["context"]
        think = state.get("think", False)

        system_instruction = (
            "You are PaperVault, an expert AI research assistant. "
            "You MUST answer the user's question based ONLY on the provided context. "
            "If the answer is not in the context, explicitly state that you do not know. "
            "CRITICAL: When referencing a paper, you MUST use inline markdown hyperlinks formatted exactly like this: [Paper Title](URL). "
            "Do NOT list URLs at the end; embed them naturally within your analysis sentences."
        )

        human_prompt = (
            f"Please answer the following question using the research context below.\n\n"
            f"QUESTION: {query}\n\n"
            f"AVAILABLE CONTEXT:\n{context}"
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": human_prompt},
        ]

        logger.info("Generating response (think=%s)...", think)
        content, thinking = self._ollama_chat(messages, think=think)
        return {"generation": content, "thinking": thinking}

    def generate_answer(self, query: str, retrieved_papers: list, think: bool = False) -> Dict[str, str]:
        context_str = ""
        for idx, paper in enumerate(retrieved_papers):
            title = paper.get("title", "Unknown Title")
            raw_abstract = paper.get("abstract", "Abstract not available.")
            url = paper.get("arxiv_url", "URL not available")
            abstract = raw_abstract[:500] + ("..." if len(raw_abstract) > 500 else "")
            context_str += f"--- Paper {idx+1}: {title} ---\nURL: {url}\nAbstract: {abstract}\n\n"

        initial_state: GraphState = {
            "query": query,
            "context": context_str,
            "think": think,
            "generation": "",
            "thinking": "",
        }

        logger.info("Triggering LangGraph generation node...")
        result = self.app.invoke(initial_state)

        return {
            "answer": result["generation"],
            "thinking": result.get("thinking", "") or "",
        }
