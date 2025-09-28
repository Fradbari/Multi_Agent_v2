import os
import yfinance as yf
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
# from crewai_tools import DuckDuckGoSearchRun # Deprecated
from langchain.tools import DuckDuckGoSearchRun
from crewai.tools import BaseTool

# --- Configuration ---
# You can change the stock ticker and the research date range here
STOCK_TICKER = "TSLA"
RESEARCH_DATE_START = "2023-01-01"
RESEARCH_DATE_END = "2024-01-01"

# --- LLM and Tool Setup ---
try:
    # Use the OLLAMA_BASE_URL environment variable if available, otherwise default to localhost
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_llm = Ollama(model="mistral", base_url=ollama_base_url)
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
    llm=ollama_llm
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
    llm=ollama_llm
)

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
    output_file=f"market_analysis_{STOCK_TICKER}.md"
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
    output_file=f"investment_strategy_{STOCK_TICKER}.md"
)

# --- Crew Definition ---
financial_crew = Crew(
    agents=[market_analyst, investment_strategist],
    tasks=[analysis_task, strategy_task],
    process=Process.sequential,
    verbose=2
)

# --- Execute the Crew ---
if __name__ == '__main__':
    print("🚀 Starting Financial Analysis Crew for", STOCK_TICKER)
    print("-" * 50)

    result = financial_crew.kickoff()

    print("\n\n" + "="*50)
    print("✅ Financial Analysis Complete")
    print("="*50 + "\n")
    print("Final Report:")
    print(result)