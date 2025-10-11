# Multi-Agent CrewAI API Service
# Modular architecture for scalable financial analysis

__version__ = "1.0.0"
__author__ = "Francesco Di Lecce"

from .api.models import (
    AnalysisRequest,
    AnalysisResponse, 
    BulkAnalysisRequest,
    HealthCheckResponse,
    AnalysisStatus
)

from .agents import (
    create_market_analyst,
    create_investment_strategist
)

from .tasks import (
    create_analysis_task,
    create_strategy_task
)

from .tools.financial_data import FinancialDataTool
from .tools.web_search import DuckDuckGoSearchTool

__all__ = [
    # Models
    'AnalysisRequest',
    'AnalysisResponse',
    'BulkAnalysisRequest', 
    'HealthCheckResponse',
    'AnalysisStatus',
    
    # Agent Factories
    'create_market_analyst',
    'create_investment_strategist',
    
    # Task Factories
    'create_analysis_task',
    'create_strategy_task',
    
    # Tools
    'FinancialDataTool',
    'DuckDuckGoSearchTool'
]
