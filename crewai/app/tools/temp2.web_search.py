# Versione aggiornata per CrewAI moderno
from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import BaseTool  
from typing import Dict, Any
from pydantic import Field

import logging

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Cerca informazioni aggiornate sul web per un determinato argomento"
    
    #def __init__(self):
    #    super().__init__()
    #    self.search_engine = DuckDuckGoSearchRun()
    #    self.cache = {}
    
    # ✅ CORRETTO: Dichiarare tutti i field come attributi di classe
    search_engine: Any = Field(default_factory=DuckDuckGoSearchRun, exclude=True)
    cache: Dict[str, str] = Field(default_factory=dict, exclude=True)

    def _run(self, query: str) -> str:
        """Enhanced search with caching and error handling"""
        
        if query in self.cache:
            logger.info(f"Cache hit per query: {query}")
            return self.cache[query]
        
        try:
            result = self.search_engine.run(query)
            
            if not result or len(result) < 10:
                logger.warning(f"Risultati limitati per query: {query}")
                return f"Pochi risultati trovati per: {query}. Risultato: {result}"
            
            self.cache[query] = result
            logger.info(f"Search completata per: {query}")
            return result
            
        except Exception as e:
            error_msg = f"Errore nella ricerca per '{query}': {str(e)}"
            logger.error(error_msg)
            return error_msg
