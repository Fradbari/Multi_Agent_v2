from crewai import Agent
from langchain_community.llms import Ollama
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)

def create_investment_strategist(
    ticker: str,
    llm_config: Optional[dict] = None,
    custom_instructions: Optional[str] = None
) -> Agent:
    """
    Factory function to create Investment Strategist with dynamic configuration.
    Optimized for strategic decision-making with moderate creativity.
    """
    
    # LLM config optimized for strategic thinking
    default_llm_config = {
        "model": "mistral-nemo:12b-instruct-2407-q5_K_M",
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "temperature": 0.3,  # Moderate creativity for innovative strategies
        #"max_tokens": 4000,
        "top_p": 0.9
    }
    
    final_config = {**default_llm_config, **(llm_config or {})}
    
    try:
        strategist_llm = Ollama(**final_config)
        logger.info(f"LLM initialized for investment strategist: {final_config['model']}")
        
    except Exception as e:
        logger.error(f"Failed to initialize strategist LLM: {e}")
        raise
    
    # Dynamic goal with ticker context
    base_goal = f"""Sviluppare una tesi di investimento strategica e raccomandazioni azionabili 
    per {ticker} basate sull'analisi del Market Research Analyst, considerando fattori di rischio, 
    potenziale di crescita e condizioni di mercato per fornire una chiara strategia buy/hold/sell 
    con razionale dettagliato."""
    
    if custom_instructions:
        enhanced_goal = f"{base_goal}\n\nConsiderazioni strategiche aggiuntive: {custom_instructions}"
    else:
        enhanced_goal = base_goal
    
    backstory = """Sei uno stratega degli investimenti di alto livello con 20+ anni di 
    esperienza nella gestione di portafogli e nella formulazione di strategie di investimento. 
    Hai gestito fondi per oltre €500M e hai un track record comprovato nell'identificazione 
    di opportunità di investimento in mercati volatili. La tua expertise include valutazione del rischio, 
    asset allocation, e timing di mercato. Sei riconosciuto per la tua capacità di tradurre 
    analisi complesse in strategie di investimento chiare e implementabili, considerando sempre 
    il profilo di rischio-rendimento ottimale."""
    
    agent = Agent(
        role='Senior Financial Investment Strategist',
        goal=enhanced_goal,
        backstory=backstory,
        verbose=True,
        allow_delegation=False,
        max_iter=12,
        memory=True,
        llm=strategist_llm,
        # Configuration for reliability
        max_retry_limit=3,
        request_timeout=200
    )
    
    logger.info(f"Investment Strategist created successfully for ticker: {ticker}")
    return agent
