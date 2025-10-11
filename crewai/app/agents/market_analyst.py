from crewai import Agent
from langchain_community.llms import Ollama
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

def create_market_analyst(
    ticker: str,
    llm_config: Optional[dict] = None,
    tools: Optional[List] = None,
    custom_instructions: Optional[str] = None
) -> Agent:
    """
    Factory function to create Market Research Analyst with dynamic configuration.
    This approach follows CrewAI best practices for modular agent creation.
    """
    
    # Default LLM configuration optimized for analysis precision
    default_llm_config = {
        "model": "mistral-nemo:12b-instruct-2407-q5_K_M",
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "temperature": 0.1,  # Low temperature for consistent analysis
        "max_tokens": 4000,
        "top_p": 0.9
    }
    
    # Merge custom config with defaults
    final_config = {**default_llm_config, **(llm_config or {})}
    
    try:
        # Initialize LLM with configuration
        analyst_llm = Ollama(**final_config)
        logger.info(f"LLM initialized for market analyst: {final_config['model']}")
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise
    
    # Dynamic goal and backstory based on ticker
    base_goal = f"""Condurre un'analisi finanziaria approfondita e multi-dimensionale di {ticker}, 
    fornendo insights quantitativi e qualitativi per supportare decisioni di investimento informate."""
    
    # Add custom instructions if provided
    if custom_instructions:
        enhanced_goal = f"{base_goal}\n\nIstruzioni aggiuntive: {custom_instructions}"
    else:
        enhanced_goal = base_goal
    
    # Professional backstory
    backstory = """Sei un analista finanziario senior con oltre 15 anni di esperienza 
    nell'analisi di mercati azionari e nella valutazione di aziende. 
    Hai una solida formazione in analisi tecnica e fondamentale, econometria e behavioral finance. 
    Sei noto per la tua capacità di sintetizzare dati complessi in insights azionabili e per la tua 
    precisione nell'identificare trend emergenti. Hai una particolare expertise nell'utilizzo di 
    strumenti quantitativi e fonti di dati multiple per costruire una visione completa del contesto di mercato."""
    
    # Create agent with dynamic configuration
    agent = Agent(
        role='Senior Market Research Analyst',
        goal=enhanced_goal,
        backstory=backstory,
        verbose=True,
        allow_delegation=False,
        max_iter=15,
        max_rpm=None,
        memory=True,
        tools=tools or [],  # Tools will be injected by caller
        llm=analyst_llm,
        # Enhanced configuration for robustness
        max_retry_limit=3,
        request_timeout=300
    )
    
    logger.info(f"Market Analyst created successfully for ticker: {ticker}")
    return agent
