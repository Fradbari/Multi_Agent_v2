import yfinance as yf
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FinancialDataTool:
    """Enhanced Financial Data Tool with error handling and validation"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_data(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        Fetches historical stock data for a given ticker between two dates.
        Enhanced with caching and better error handling.
        """
        cache_key = f"{ticker}_{start_date}_{end_date}"
        
        if cache_key in self.cache:
            logger.info(f"Cache hit for {cache_key}")
            return self.cache[cache_key]
        
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                error_msg = f"Nessun dato trovato per {ticker} nell'intervallo {start_date} - {end_date}"
                logger.warning(error_msg)
                return error_msg
            
            # Calcola metriche aggiuntive
            data['Daily_Return'] = data['Close'].pct_change()
            data['Volatility'] = data['Daily_Return'].rolling(window=20).std()
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            
            result = data.to_string()
            self.cache[cache_key] = result  # Cache result
            
            logger.info(f"Successfully fetched data for {ticker}")
            return result
            
        except Exception as e:
            error_msg = f"Errore durante il recupero dei dati per {ticker}: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def get_company_info(self, ticker: str) -> str:
        """
        Fetches comprehensive company information.
        Enhanced with better data structuring.
        """
        cache_key = f"info_{ticker}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            company = yf.Ticker(ticker)
            info = company.info
            
            if not info:
                return f"Informazioni non disponibili per {ticker}"
            
            # Struttura informazioni chiave
            formatted_info = f"""
            INFORMAZIONI AZIENDALI PER {ticker}:
            
            Nome: {info.get('longName', 'N/A')}
            Settore: {info.get('sector', 'N/A')}
            Industria: {info.get('industry', 'N/A')}
            Market Cap: ${info.get('marketCap', 0):,}
            Dipendenti: {info.get('fullTimeEmployees', 'N/A')}
            
            METRICHE FINANZIARIE:
            P/E Ratio: {info.get('trailingPE', 'N/A')}
            P/B Ratio: {info.get('priceToBook', 'N/A')}
            Debt/Equity: {info.get('debtToEquity', 'N/A')}
            ROE: {info.get('returnOnEquity', 'N/A')}
            
            VALUTAZIONE:
            52W High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
            52W Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
            Target Price: ${info.get('targetMeanPrice', 'N/A')}
            """
            
            self.cache[cache_key] = formatted_info
            return formatted_info
            
        except Exception as e:
            error_msg = f"Errore recupero informazioni per {ticker}: {str(e)}"
            logger.error(error_msg)
            return error_msg
