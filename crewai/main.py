import os
import logging
from datetime import datetime
import yfinance as yf
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
# from crewai_tools import DuckDuckGoSearchRun # Deprecated
from langchain.tools import DuckDuckGoSearchRun
from crewai.tools import BaseTool

# Configura logging dettagliato per debug
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'/app/storage/crewai_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration ---
# You can change the stock ticker and the research date range here
STOCK_TICKER = "TSLA"
RESEARCH_DATE_START = "2023-01-01"
RESEARCH_DATE_END = "2024-01-01"

# --- Output Directory Setup ---
# Use the OUTPUT_DIR environment variable if available, otherwise default to /app/outputs
output_dir = os.getenv("OUTPUT_DIR", "/app/outputs")
os.makedirs(output_dir, exist_ok=True)

# --- LLM and Tool Setup ---
try:
    # Use the OLLAMA_BASE_URL environment variable if available, otherwise default to localhost
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # CONFIGURAZIONE LLM OTTIMIZZATA - INSERIRE QUI
    # Per l'analista - temperatura più bassa per precisione
    analyst_llm = Ollama(
        #model="mistral", 
        model="mistral-nemo:12b-instruct-2407-q5_K_M",
        base_url=ollama_base_url,
        temperature=0.1,  # Maggiore consistenza nell'analisi
        max_tokens=4000,
        top_p=0.9
    )
    
    # Per lo stratega - leggera creatività per strategie innovative  
    strategist_llm = Ollama(
        #model="mistral", 
        model="mistral-nemo:12b-instruct-2407-q5_K_M",
        base_url=ollama_base_url,
        temperature=0.3,  # Bilanciamento tra precisione e creatività
        max_tokens=4000,
        top_p=0.9
    )

    print(f"Connessione riuscita a Ollama a {ollama_base_url}")
    
except Exception as e:
    print(f"Impossibile connettersi a Ollama. Assicurati che sia in esecuzione e accessibile. Errore: {e}")
    exit()

# --- Crea un tool wrapper personalizzato ---
class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Cerca sul web informazioni su un determinato argomento"
    
    def _run(self, query: str) -> str:
        search = DuckDuckGoSearchRun()
        return search.run(query)

# search_tool = DuckDuckGoSearchRun() # Deprecated
search_tool = DuckDuckGoSearchTool()

# --- Custom Tool for Financial Data ---
class FinancialDataTool:
    def get_stock_data(self, ticker, start_date, end_date):
        """
        Fetches historical stock data for a given ticker between two dates.
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            if data.empty:
                return f"Nessun dato trovato per {ticker} nell'intervallo di date specificato."
            return data.to_string()
        except Exception as e:
            return f"Errore durante il recupero dei dati azionari per {ticker}: {str(e)}"

    def get_company_info(self, ticker):
        """
        Fetches general information about a company.
        """
        try:
            company = yf.Ticker(ticker)
            return str(company.info)
        except Exception as e:
            return f"Errore durante il recupero delle informazioni aziendali per{ticker}: {str(e)}"

financial_tool = FinancialDataTool()

# --- Agent Definitions ---
# 1. Market Research Analyst
market_analyst = Agent(
    role='Senior Market Research Analyst',
    goal=f"""   Condurre un'analisi approfondita e multi-dimensionale di {STOCK_TICKER} 
                dal {RESEARCH_DATE_START} al {RESEARCH_DATE_END}, fornendo insights quantitativi 
                e qualitativi per supportare decisioni di investimento informate.""",
    backstory="""   Sei un analista finanziario senior con oltre 15 anni di esperienza 
                    nell'analisi di mercati azionari e nella valutazione di aziende. 
                    Hai una solida formazione in analisi tecnica e fondamentale, 
                    econometria e behavioral finance. Sei noto per la tua capacità di 
                    sintetizzare dati complessi in insights azionabili e per la tua 
                    precisione nell'identificare trend emergenti. Hai una particolare 
                    expertise nell'utilizzo di strumenti quantitativi e fonti di dati 
                    multiple (provenienti da ricerche web approfondite) per costruire 
                    una visione completa del contesto di mercato.""",
    verbose=True,
    allow_delegation=False,
    max_iter=15,
    max_rpm=None,
    memory=True,
    tools=[search_tool, financial_tool.get_stock_data, financial_tool.get_company_info],
    llm=analyst_llm
)

# 2. Financial Investment Strategist
investment_strategist = Agent(
    role='Senior Financial Investment Strategist',
    goal=f"""   Sviluppare una tesi di investimento strategica e raccomandazioni azionabili 
                per {STOCK_TICKER} basate sull'analisi del Market Research Analyst, considerando 
                fattori di rischio, potenziale di crescita e condizioni di mercato per fornire 
                una chiara strategia buy/hold/sell con razionale dettagliato.""",
    backstory="""Sei uno stratega degli investimenti di alto livello con 20+ anni di 
                 esperienza nella gestione di portafogli e nella formulazione di strategie 
                 di investimento. Hai gestito fondi per oltre €500M e hai un track record 
                 comprovato nell'identificazione di opportunità di investimento in mercati 
                 volatili. La tua expertise include valutazione del rischio, asset allocation, 
                 e timing di mercato. Sei riconosciuto per la tua capacità di tradurre 
                 analisi complesse in strategie di investimento chiare e implementabili, 
                 considerando sempre il profilo di rischio-rendimento ottimale.""",
    verbose=True,
    allow_delegation=False,
    max_iter=12,
    memory=True,
    llm=strategist_llm
)

# GESTIONE ERRORI E RETRY - INSERIRE QUI
# Configurazioni per robustezza
market_analyst.max_retry_limit = 3
investment_strategist.max_retry_limit = 3

# Aggiungi timeout per le operazioni
market_analyst.request_timeout = 300  # 5 minuti
investment_strategist.request_timeout = 200  # Meno tempo per strategia

# --- Task Definitions ---
# Task for the Market Analyst
analysis_task = Task(
    description=f"""
    Esegui un'analisi finanziaria completa e strutturata di {STOCK_TICKER}:
    
    1. **Analisi Tecnica**: Recupera dati storici dal {RESEARCH_DATE_START} al {RESEARCH_DATE_END}
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
    """,
    expected_output=f"""
    Report di Analisi di Mercato per {STOCK_TICKER} contenente:
    
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
    """,
    agent=market_analyst,
    context=[],
    output_file=f"{output_dir}/market_analysis_{STOCK_TICKER}.md"
)

# Task for the Investment Strategist
strategy_task = Task(
    description=f"""
    Basandoti esclusivamente sul report dettagliato del Senior Market Research Analyst, 
    sviluppa una strategia di investimento completa per {STOCK_TICKER}:
    
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
    """,
    expected_output=f"""
    **INVESTMENT STRATEGY REPORT per {STOCK_TICKER}**
    
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
    """,
    agent=investment_strategist,
    context=[analysis_task],  
    output_file=f"{output_dir}/investment_strategy_{STOCK_TICKER}.md"
)

# Configura storage personalizzato per Kubernetes
storage_path = os.getenv("CREWAI_STORAGE_DIR", "/app/storage")
os.makedirs(storage_path, exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = storage_path

# --- Crew Definition ---
financial_crew = Crew(
    agents=[market_analyst, investment_strategist],
    tasks=[analysis_task, strategy_task],
    process=Process.sequential,
    verbose=2,
    memory=True,      # Abilita memoria condivisa tra agenti
    cache=True,       # Cache per migliorare performance
    max_rpm=None,     # Nessun limite RPM per velocità massima
    output_log_file=f"{storage_path}/crew_log_{STOCK_TICKER}.txt"  # Log persistenti
)

# VALIDAZIONE OUTPUT - INSERIRE QUI
def validate_analysis_output(output):
    """Valida che il report dell'analista contenga le sezioni richieste"""
    required_sections = [
        'Executive Summary', 
        'Analisi Tecnica', 
        'Analisi Fondamentale',
        'Market Sentiment',
        'Risk Assessment'
    ]
    
    output_str = str(output)
    missing_sections = []
    
    for section in required_sections:
        if section.lower() not in output_str.lower():
            missing_sections.append(section)
    
    if missing_sections:
        logger.warning(f"Sezioni mancanti nel report: {missing_sections}")
        return False, missing_sections
    
    logger.info("Validazione output completata con successo")
    return True, []

def validate_strategy_output(output):
    """Valida che la strategia contenga raccomandazione chiara"""
    output_str = str(output).upper()
    
    has_recommendation = any(rec in output_str for rec in ['BUY', 'SELL', 'HOLD'])
    has_target_price = 'TARGET PRICE' in output_str
    has_rationale = 'RATIONALE' in output_str or 'KEY RATIONALE' in output_str
    
    if not (has_recommendation and has_target_price and has_rationale):
        logger.warning("Output della strategia manca di elementi essenziali")
        return False
    
    logger.info("Validazione strategia completata con successo")
    return True

# --- Execute the Crew ---
if __name__ == '__main__':
    logger.info(f"🚀 Starting Financial Analysis Crew for {STOCK_TICKER}")
    print("🚀 Starting Financial Analysis Crew per ", STOCK_TICKER)
    print("-" * 50)

    result = financial_crew.kickoff()

    try:
        # Esecuzione con gestione errori
        result = financial_crew.kickoff()
        
        # Validazione dei risultati
        if len(financial_crew.tasks) >= 2:
            # Valida output dell'analista
            analysis_valid, missing_sections = validate_analysis_output(
                financial_crew.tasks[0].output
            )
            if not analysis_valid:
                logger.warning(f"Report dell'analista incompleto: {missing_sections}")
            
            # Valida output dello stratega  
            strategy_valid = validate_strategy_output(
                financial_crew.tasks[1].output
            )
            if not strategy_valid:
                logger.warning("Strategia di investimento incompleta")
        
        # Output finale
        print("\n\n" + "="*50)
        print("✅ Financial Analysis Complete")
        print("="*50 + "\n")
        print("Final Report:")
        print(result)
        
        logger.info("Esecuzione completata con successo")
        
        # Salva anche in un file di riepilogo
        summary_path = f"{storage_path}/final_report_{STOCK_TICKER}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(str(result))
            logger.info(f"Report salvato in: {summary_path}")
        except Exception as save_error:
            logger.error(f"Errore nel salvataggio del report: {save_error}")
            
    except Exception as e:
        logger.error(f"Errore nell'esecuzione del crew: {e}")
        print(f"❌ Errore nell'esecuzione: {e}")
        
        # Strategia di fallback
        try:
            print("🔄 Tentativo di esecuzione semplificata...")
            # Versione semplificata senza memoria e cache
            fallback_crew = Crew(
                agents=[market_analyst, investment_strategist],
                tasks=[analysis_task, strategy_task],
                process=Process.sequential,
                verbose=1,
                memory=False,
                cache=False
            )
            result = fallback_crew.kickoff()
            print("✅ Esecuzione semplificata completata")
            print(result)
            
        except Exception as fallback_error:
            logger.critical(f"Anche l'esecuzione di fallback è fallita: {fallback_error}")
            print(f"❌ Errore critico: {fallback_error}")
            exit(1)