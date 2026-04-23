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
        logger.info("Initializing Ollama (Gemma 2B) and LangGraph...")
        
        # Connect to your local Ollama instance
        self.llm = ChatOllama(model="gemma:2b", temperature=0.2)
        
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
        
        system_instruction = (
            "You are PaperVault, an expert AI research assistant. "
            "Read the retrieved context below carefully. Provide a highly detailed, descriptive, and technical summary answering the user's query. "
            "Structure your response beautifully using Markdown headings, bullet points, and deep analysis. "
            "You MUST include inline markdown hyperlinks to the papers using the provided URLs. Do not just give 3 points; provide an in-depth synthesis.\n\n"
            f"CONTEXT:\n{context}"
        )
        
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=query)
        ]
        
        # Trigger Ollama
        response = self.llm.invoke(messages)
        
        # Update the state with the generation
        return {"generation": response.content}

    def generate_answer(self, query: str, retrieved_papers: list) -> str:
        """Public method to format the context and trigger the graph."""
        
        # Format the papers into a single context string
        context_str = ""
        for idx, paper in enumerate(retrieved_papers):
            # Ensure we are extracting the title, abstract, and URL safely
            title = paper.get("title", "Unknown Title")
            abstract = paper.get("abstract", "Abstract not available.")
            url = paper.get("arxiv_url", "URL not available") 
            
            # Inject the URL into the LLM's reading context
            context_str += f"--- Paper {idx+1}: {title} ---\nURL: {url}\nAbstract: {abstract}\n\n"

        # Initialize the state and run the graph
        initial_state = {"query": query, "context": context_str}
        
        logger.info("Triggering LangGraph generation node...")
        result = self.app.invoke(initial_state)
        
        return result["generation"]