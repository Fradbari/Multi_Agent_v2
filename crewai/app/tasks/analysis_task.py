from crewai import Task
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def create_analysis_task(
    ticker: str,
    start_date: str,
    end_date: str,
    agent,
    output_dir: str,
    custom_instructions: Optional[str] = None
) -> Task:
    """
    Factory function to create market analysis task with dynamic parameters.
    Follows CrewAI best practices for configurable task creation.
    """
    
    # Base task description with dynamic parameters
    base_description = f"""
    Esegui un'analisi finanziaria completa e strutturata di {ticker}:
    
    1. **Analisi Tecnica**: Recupera dati storici dal {start_date} al {end_date}
    - Calcola indicatori tecnici chiave (RSI, MACD, Bollinger Bands)
    - Identifica pattern grafici significativi
    - Analizza volumi di trading e volatilità
    
    2. **Analisi Fondamentale**: Recupera informazioni aziendali dettagliate
    - Metriche finanziarie chiave (P/E, P/B, ROE, debt-to-equity)
    - Performance finanziaria storica e trend
    - Posizione competitiva e settore di appartenenza
    
    3. **Sentiment Analysis**: Ricerca notizie e sentiment di mercato
    - Eventi significativi nel periodo analizzato
    - Sentiment degli analisti e rating
    - Impatto di news macro-economiche
    
    4. **Sintesi Quantitativa**: Integra tutti i dati in un framework coerente
    """
    
    # Add custom instructions if provided
    if custom_instructions:
        enhanced_description = f"{base_description}\n\n5. **Analisi Personalizzata**: {custom_instructions}"
    else:
        enhanced_description = base_description
    
    # Expected output template
    expected_output = f"""
    Report di Analisi di Mercato per {ticker} contenente:
    
    **SEZIONE 1: Executive Summary**
    - Riassunto in 3 punti chiave della posizione attuale del titolo
    
    **SEZIONE 2: Analisi Tecnica**
    - Trend principale e livelli di supporto/resistenza
    - Indicatori tecnici con interpretazione
    - Volume analysis e momentum
    
    **SEZIONE 3: Analisi Fondamentale**
    - Metriche di valutazione vs settore e mercato
    - Performance finanziaria e trend di crescita
    - Strengths, Weaknesses, Opportunities, Threats (SWOT)
    
    **SEZIONE 4: Market Sentiment**
    - Sentiment score generale (1-10)
    - News impact analysis
    - Analisti consensus e rating changes
    
    **SEZIONE 5: Risk Assessment**
    - Principali fattori di rischio identificati
    - Volatilità storica e beta
    - Correlazioni con mercato e settore
    """
    
    try:
        task = Task(
            description=enhanced_description,
            expected_output=expected_output,
            agent=agent,
            context=[],  # Will be populated by crew execution flow
            output_file=f"{output_dir}/market_analysis_{ticker}.md"
        )
        
        logger.info(f"Analysis task created successfully for {ticker}")
        return task
        
    except Exception as e:
        logger.error(f"Failed to create analysis task for {ticker}: {e}")
        raise
