import logging
from typing import Dict, TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

# 1. Define the state that will be passed between our LangGraph nodes
class GraphState(TypedDict):
    query: str
    context: str
    generation: str

class RAGGenerator:
    def __init__(self):
        logger.info("Initializing Ollama (Gemma 4 E2B) and LangGraph...")
        
        # Connect to your local Ollama instance using the new Gemma 4 E2B model
        self.llm = ChatOllama(
            model="gemma4:e2b", 
            temperature=0.2  # Low temperature for factual grounding
        )
        
        # 2. Build the LangGraph Workflow
        workflow = StateGraph(GraphState)
        
        # Add our single generation node
        workflow.add_node("generate", self.generate_node)
        
        # Define the flow
        workflow.set_entry_point("generate")
        workflow.add_edge("generate", END)
        
        # Compile the graph into an executable app
        self.app = workflow.compile()

    def generate_node(self, state: GraphState) -> Dict:
        """The actual node that calls the LLM with the context and query."""
        query = state["query"]
        context = state["context"]
        
        # 1. Keep the System Message laser-focused on persona and rules
        # Gemma 4 handles native system prompts beautifully
        system_instruction = (
            "You are PaperVault, an expert AI research assistant. "
            "You MUST answer the user's question based ONLY on the provided context. "
            "If the answer is not in the context, explicitly state that you do not know. "
            "CRITICAL: When referencing a paper, you MUST use inline markdown hyperlinks formatted exactly like this: [Paper Title](URL). "
            "Do NOT list URLs at the end; embed them naturally within your analysis sentences."
        )
        
        # 2. Wrap the heavy context and the query into the Human Message
        human_prompt = (
            f"Please answer the following question using the research context below.\n\n"
            f"QUESTION: {query}\n\n"
            f"AVAILABLE CONTEXT:\n{context}"
        )
        
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=human_prompt)
        ]
        
        # Trigger Ollama
        logger.info("Generating response with RAG context...")
        response = self.llm.invoke(messages)
        
        return {"generation": response.content}

    def generate_answer(self, query: str, retrieved_papers: list) -> str:
        """Public method to format the context and trigger the graph."""
        
        # Format the papers into a single context string
        context_str = ""
        for idx, paper in enumerate(retrieved_papers):
            title = paper.get("title", "Unknown Title")
            raw_abstract = paper.get("abstract", "Abstract not available.")
            url = paper.get("arxiv_url", "URL not available") 
            
            # Truncate abstract to 500 characters to prevent context window overflow
            abstract = raw_abstract[:500] + ("..." if len(raw_abstract) > 500 else "")
            
            # Inject the URL into the LLM's reading context
            context_str += f"--- Paper {idx+1}: {title} ---\nURL: {url}\nAbstract: {abstract}\n\n"

        # Initialize the state and run the graph
        initial_state = {"query": query, "context": context_str}
        
        logger.info("Triggering LangGraph generation node with Gemma 4 E2B...")
        result = self.app.invoke(initial_state)
        
        return result["generation"]