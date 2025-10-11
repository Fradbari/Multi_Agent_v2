from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol", example="TSLA")
    start_date: str = Field(..., description="Start date YYYY-MM-DD", example="2024-01-01")
    end_date: str = Field(..., description="End date YYYY-MM-DD", example="2024-12-31")
    output_format: Optional[str] = Field("markdown", description="Output format")
    priority: Optional[str] = Field("normal", description="Analysis priority")
    custom_instructions: Optional[str] = Field(None, description="Custom analysis instructions")

class AnalysisResponse(BaseModel):
    job_id: str
    status: AnalysisStatus
    ticker: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: Optional[int] = Field(0, ge=0, le=100)

class BulkAnalysisRequest(BaseModel):
    tickers: List[str] = Field(..., description="List of stock tickers")
    start_date: str 
    end_date: str
    priority: Optional[str] = "normal"

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, bool]
    version: str = "1.0.0"
