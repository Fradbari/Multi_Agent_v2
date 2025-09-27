import os
import yfinance as yf
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from crewai_tools import DuckDuckGoSearchRun

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
    print(f"Successfully connected to Ollama at {ollama_base_url}")
except Exception as e:
    print(f"Failed to connect to Ollama. Please ensure it is running and accessible. Error: {e}")
    exit()

search_tool = DuckDuckGoSearchRun()

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
                return f"No data found for {ticker} in the specified date range."
            return data.to_string()
        except Exception as e:
            return f"Error fetching stock data for {ticker}: {str(e)}"

    def get_company_info(self, ticker):
        """
        Fetches general information about a company.
        """
        try:
            company = yf.Ticker(ticker)
            return str(company.info)
        except Exception as e:
            return f"Error fetching company info for {ticker}: {str(e)}"

financial_tool = FinancialDataTool()

# --- Agent Definitions ---
# 1. Market Research Analyst
market_analyst = Agent(
    role='Market Research Analyst',
    goal=f'Analyze the financial performance and market sentiment of {STOCK_TICKER} from {RESEARCH_DATE_START} to {RESEARCH_DATE_END}.',
    backstory="""An experienced analyst with a keen eye for market trends and financial data.
    You are skilled at using financial tools to gather and interpret data, and you can
    also perform web searches to understand the broader market context.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool, financial_tool.get_stock_data, financial_tool.get_company_info],
    llm=ollama_llm
)

# 2. Financial Investment Strategist
investment_strategist = Agent(
    role='Financial Investment Strategist',
    goal=f'Develop a detailed investment thesis and recommendation for {STOCK_TICKER} based on the analyst\'s report.',
    backstory="""A seasoned investment strategist known for your ability to synthesize complex information
    into a clear, actionable investment plan. You consider market conditions, risk tolerance,
    and long-term potential to advise on whether to buy, hold, or sell.""",
    verbose=True,
    allow_delegation=True,
    llm=ollama_llm
)

# --- Task Definitions ---
# Task for the Market Analyst
analysis_task = Task(
    description=f"""
    1.  Fetch the historical stock data for {STOCK_TICKER} from {RESEARCH_DATE_START} to {RESEARCH_DATE_END}.
    2.  Fetch the general company information for {STOCK_TICKER}.
    3.  Conduct a web search for news and market sentiment regarding {STOCK_TICKER} during this period.
    4.  Summarize the key financial metrics, news highlights, and overall market sentiment.
    5.  Compile a comprehensive report of your findings.
    """,
    expected_output=f"A detailed report containing the historical stock data analysis, company overview, and market sentiment summary for {STOCK_TICKER}.",
    agent=market_analyst
)

# Task for the Investment Strategist
strategy_task = Task(
    description=f"""
    1.  Review the comprehensive report provided by the Market Research Analyst.
    2.  Based on the data and sentiment, formulate a long-term investment thesis for {STOCK_TICKER}.
    3.  Provide a clear recommendation: Is {STOCK_TICKER} a 'Buy', 'Hold', or 'Sell' at this time?
    4.  Justify your recommendation with key reasons derived from the analysis.
    """,
    expected_output=f"A final investment recommendation report for {STOCK_TICKER}, including the investment thesis and a clear 'Buy/Hold/Sell' rating with justification.",
    agent=investment_strategist
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