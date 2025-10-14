from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import logging
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)

class SearchInput(BaseModel):
    """Input schema for search tool"""
    query: str = Field(..., description="Query di ricerca per trovare informazioni aggiornate sul web")

class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Cerca informazioni aggiornate sul web su un argomento specifico"
    args_schema: Type[BaseModel] = SearchInput
    
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    def _run(self, query: str) -> str:
        """Execute web search"""
        
        # Check cache first
        if query in self.cache:
            logger.info(f"🎯 Cache hit per query: {query}")
            return self.cache[query]
        
        try:
            # Simplified search approach using DuckDuckGo Instant API
            search_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process results
            results = []
            
            # Abstract (direct answer)
            if data.get('Abstract'):
                results.append(f"📋 Risposta Diretta: {data['Abstract']}")
            
            # Related topics
            if data.get('RelatedTopics'):
                results.append("\n🔗 Argomenti Correlati:")
                for topic in data['RelatedTopics'][:3]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append(f"• {topic['Text'][:200]}...")
            
            # Answer if available  
            if data.get('Answer'):
                results.append(f"\n💡 Informazione: {data['Answer']}")
            
            if results:
                final_result = "\n".join(results)
                self.cache[query] = final_result
                logger.info(f"✅ Ricerca completata per: {query}")
                return final_result
            else:
                fallback_result = f"🔍 Query eseguita per '{query}'. Suggerisco di cercare informazioni più specifiche su mercati finanziari, news economiche o dati settoriali."
                return fallback_result
                
        except requests.RequestException as e:
            logger.warning(f"⚠️ Errore API DuckDuckGo per '{query}': {e}")
            # Fallback response
            fallback_result = f"""
🔍 RICERCA WEB PER: {query}

⚠️ Servizio di ricerca temporaneamente non disponibile.

💡 SUGGERIMENTI ALTERNATIVI:
• Consultare siti finanziari: Yahoo Finance, Bloomberg, MarketWatch
• Verificare news recenti su Google Finance  
• Controllare comunicati stampa ufficiali dell'azienda
• Analizzare reports di analisti su Seeking Alpha

🎯 Per analisi {query}, raccomando di verificare:
• Performance recente del titolo
• News macro-economiche del settore
• Eventi corporate significativi
• Sentiment degli investitori
"""
            return fallback_result
            
        except Exception as e:
            error_msg = f"❌ Errore generale nella ricerca per '{query}': {str(e)}"
            logger.error(error_msg)
            return error_msg
