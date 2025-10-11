from crewai import Task
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

def create_strategy_task(
    ticker: str,
    agent,
    output_dir: str,
    context_tasks: List[Task],
    custom_instructions: Optional[str] = None
) -> Task:
    """
    Factory function to create investment strategy task.
    Depends on analysis task for context and decision-making.
    """
    
    base_description = f"""
    Basandoti esclusivamente sul report dettagliato del Senior Market Research Analyst, 
    sviluppa una strategia di investimento completa per {ticker}:
    
    1. **Investment Thesis Development**:
    - Sintetizza i key findings dell'analisi di mercato
    - Identifica i principali driver di valore
    - Valuta il posizionamento strategico dell'azienda
    
    2. **Risk-Return Analysis**:
    - Quantifica il profilo rischio-rendimento
    - Identifica scenari bull/bear/base case
    - Definisci probabilità per ogni scenario
    
    3. **Strategic Recommendation**:
    - Fornisci raccomandazione CHIARA: BUY/HOLD/SELL
    - Giustifica la decisione con evidenze specifiche dal report
    - Definisci target price e stop loss se applicabile
    
    4. **Implementation Strategy**:
    - Timing di ingresso ottimale
    - Dimensione posizione consigliata
    - Catalisti da monitorare
    """
    
    if custom_instructions:
        enhanced_description = f"{base_description}\n\n5. **Strategia Personalizzata**: {custom_instructions}"
    else:
        enhanced_description = base_description
    
    expected_output = f"""
    **INVESTMENT STRATEGY REPORT per {ticker}**
    
    **🎯 RACCOMANDAZIONE: [BUY/HOLD/SELL]**
    **📊 Target Price: [€X.XX]**
    **⚠️ Stop Loss: [€X.XX]**
    **📈 Upside Potential: [X%]**
    **📉 Downside Risk: [X%]**
    
    **INVESTMENT THESIS:**
    [Tesi di investimento in 2-3 paragrafi concentrati]
    
    **KEY RATIONALE:**
    1. [Primo motivo chiave con evidenze dal report]
    2. [Secondo motivo chiave con evidenze dal report]
    3. [Terzo motivo chiave con evidenze dal report]
    
    **RISK FACTORS:**
    - [Principale rischio identificato]
    - [Secondo rischio significativo]
    - [Rischio sistemico/di mercato]
    
    **IMPLEMENTATION:**
    - Timing: [Immediato/Graduale/Wait for...]
    - Position Size: [% di portafoglio raccomandato]
    - Catalysts to Watch: [Eventi chiave da monitorare]
    
    **MONITORING METRICS:**
    [3-5 KPI chiave da tracciare per validare la tesi]
    """
    
    try:
        task = Task(
            description=enhanced_description,
            expected_output=expected_output,
            agent=agent,
            context=context_tasks,  # Depends on analysis task output
            output_file=f"{output_dir}/investment_strategy_{ticker}.md"
        )
        
        logger.info(f"Strategy task created successfully for {ticker}")
        return task
        
    except Exception as e:
        logger.error(f"Failed to create strategy task for {ticker}: {e}")
        raise
