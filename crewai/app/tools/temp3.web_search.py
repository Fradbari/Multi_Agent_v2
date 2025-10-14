from langchain_community.tools import DuckDuckGoSearchRun
import logging

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool:
    """Simplified search tool without BaseTool inheritance - compatibile con CrewAI"""
    
    def __init__(self):
        self.name = "DuckDuckGo Search"
        self.description = "Cerca informazioni aggiornate sul web per un determinato argomento"
        self.search_engine = DuckDuckGoSearchRun()
        self.cache = {}
    
    def run(self, query: str) -> str:
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

# Factory function per creare l'istanza
def get_search_tool():
    return DuckDuckGoSearchTool()
