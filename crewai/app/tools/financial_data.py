import yfinance as yf
from crewai.tools import BaseTool
from typing import Type, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class FinancialDataInput(BaseModel):
    """Input schema for financial data tool"""
    query: str = Field(..., description="Query in format: 'stock_data:TICKER:START_DATE:END_DATE' or 'company_info:TICKER'")

class FinancialDataTool(BaseTool):
    name: str = "Financial Data Tool"
    description: str = "Fornisce dati finanziari storici e informazioni aziendali per azioni specifiche"
    args_schema: Type[BaseModel] = FinancialDataInput
    
    def _run(self, query: str) -> str:
        """Execute the financial data query"""
        try:
            parts = query.split(":")
            if len(parts) < 2:
                return "Formato query non valido. Usa: 'stock_data:TICKER:START:END' o 'company_info:TICKER'"
            
            action = parts[0].lower()
            ticker = parts[1].upper()
            
            if action == "stock_data" and len(parts) >= 4:
                start_date = parts[2]
                end_date = parts[3]
                return self._get_stock_data(ticker, start_date, end_date)
            elif action == "company_info":
                return self._get_company_info(ticker)
            else:
                return f"Azione '{action}' non riconosciuta. Usa 'stock_data' o 'company_info'"
                
        except Exception as e:
            error_msg = f"Errore nell'esecuzione query finanziaria: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _get_stock_data(self, ticker: str, start_date: str, end_date: str) -> str:
        """Fetch historical stock data"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                return f"❌ Nessun dato trovato per {ticker} nell'intervallo {start_date} - {end_date}"
            
            # Calculate key metrics
            latest = data.iloc[-1]
            first = data.iloc[0]
            
            # Performance calculation
            total_return = ((latest['Close'] - first['Open']) / first['Open']) * 100
            avg_volume = data['Volume'].mean()
            volatility = data['Close'].pct_change().std() * (252**0.5) * 100  # Annualized
            
            result = f"""
📊 DATI STORICI {ticker} ({start_date} → {end_date}):

💰 PERFORMANCE:
• Prezzo Apertura: ${first['Open']:.2f}
• Prezzo Chiusura: ${latest['Close']:.2f}  
• Rendimento Totale: {total_return:.2f}%
• Massimo Periodo: ${data['High'].max():.2f}
• Minimo Periodo: ${data['Low'].min():.2f}

📈 STATISTICHE:
• Volume Medio: {avg_volume:,.0f}
• Volatilità Annualizzata: {volatility:.2f}%
• Giorni di Trading: {len(data)}

📊 ULTIMI 5 GIORNI:
{data[['Open', 'High', 'Low', 'Close', 'Volume']].tail().to_string()}
"""
            logger.info(f"✅ Dati recuperati per {ticker}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Errore recupero dati {ticker}: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _get_company_info(self, ticker: str) -> str:
        """Fetch company information"""
        try:
            company = yf.Ticker(ticker)
            info = company.info
            
            if not info:
                return f"❌ Informazioni non disponibili per {ticker}"
            
            # Format key information
            result = f"""
🏢 INFORMAZIONI AZIENDALI {ticker}:

📋 DETTAGLI BASE:
• Nome: {info.get('longName', 'N/A')}
• Settore: {info.get('sector', 'N/A')}
• Industria: {info.get('industry', 'N/A')}
• Paese: {info.get('country', 'N/A')}

💼 METRICHE AZIENDALI:  
• Market Cap: ${info.get('marketCap', 0):,}
• Dipendenti: {info.get('fullTimeEmployees', 'N/A'):,}
• Revenue: ${info.get('totalRevenue', 0):,}

📊 RATIOS FINANZIARI:
• P/E Ratio: {info.get('trailingPE', 'N/A')}
• P/B Ratio: {info.get('priceToBook', 'N/A')}
• Debt/Equity: {info.get('debtToEquity', 'N/A')}
• ROE: {info.get('returnOnEquity', 'N/A')}

🎯 VALUTAZIONE:
• 52W High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
• 52W Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
• Target Price: ${info.get('targetMeanPrice', 'N/A')}

📝 DESCRIZIONE:
{info.get('longBusinessSummary', 'Non disponibile')[:500]}...
"""
            logger.info(f"✅ Informazioni recuperate per {ticker}")
            return result
            
        except Exception as e:
            error_msg = f"❌ Errore recupero informazioni {ticker}: {str(e)}"
            logger.error(error_msg)
            return error_msg
