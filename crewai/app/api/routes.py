from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from datetime import datetime
import uuid
import logging
import asyncio
import os
from typing import Dict, Any

from .models import (
    AnalysisRequest, 
    AnalysisResponse, 
    BulkAnalysisRequest, 
    HealthCheckResponse,
    AnalysisStatus
)

from ..agents import create_market_analyst, create_investment_strategist
from ..tasks import create_analysis_task, create_strategy_task
from ..tools.financial_data import FinancialDataTool
from ..tools.web_search import DuckDuckGoSearchTool
from crewai import Crew, Process

# Setup logging
logger = logging.getLogger(__name__)

# Router instance
router = APIRouter()

# In-memory storage for job tracking (in production use Redis/Database)
active_jobs: Dict[str, Dict[str, Any]] = {}
completed_jobs: Dict[str, AnalysisResponse] = {}

# Tools initialization
financial_tool = FinancialDataTool()
search_tool = DuckDuckGoSearchTool()
tools = [financial_tool.get_stock_data, financial_tool.get_company_info, search_tool]

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint to verify service status"""
    
    # Check service dependencies
    services_status = {
        "ollama": await check_ollama_connection(),
        "storage": check_storage_access(),
        "memory": True  # Always true for in-memory storage
    }
    
    overall_status = "healthy" if all(services_status.values()) else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(),
        services=services_status
    )

@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(
    request: AnalysisRequest, 
    background_tasks: BackgroundTasks
):
    """
    Create a new financial analysis job.
    Returns immediately with job_id for tracking.
    """
    
    job_id = f"analysis_{request.ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    try:
        # Validate ticker format
        if not request.ticker or len(request.ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker format")
        
        # Initialize job tracking
        job_data = {
            "job_id": job_id,
            "status": AnalysisStatus.PENDING,
            "ticker": request.ticker.upper(),
            "created_at": datetime.now(),
            "request": request
        }
        
        active_jobs[job_id] = job_data
        
        # Schedule background execution
        background_tasks.add_task(
            execute_financial_analysis,
            job_id=job_id,
            request=request
        )
        
        logger.info(f"Analysis job {job_id} created for ticker {request.ticker}")
        
        return AnalysisResponse(
            job_id=job_id,
            status=AnalysisStatus.PENDING,
            ticker=request.ticker.upper(),
            created_at=datetime.now(),
            progress=0
        )
        
    except Exception as e:
        logger.error(f"Failed to create analysis for {request.ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{job_id}", response_model=AnalysisResponse)
async def get_analysis_status(job_id: str):
    """Get the status and results of a specific analysis job"""
    
    # Check completed jobs first
    if job_id in completed_jobs:
        return completed_jobs[job_id]
    
    # Check active jobs
    if job_id in active_jobs:
        job_data = active_jobs[job_id]
        return AnalysisResponse(
            job_id=job_data["job_id"],
            status=job_data["status"],
            ticker=job_data["ticker"],
            created_at=job_data["created_at"],
            progress=job_data.get("progress", 0)
        )
    
    # Job not found
    raise HTTPException(status_code=404, detail="Analysis job not found")

@router.post("/analyze/bulk")
async def create_bulk_analysis(
    request: BulkAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Create multiple analysis jobs for different tickers"""
    
    if len(request.tickers) > 10:  # Limit concurrent analyses
        raise HTTPException(status_code=400, detail="Maximum 10 tickers per bulk request")
    
    job_ids = []
    
    for ticker in request.tickers:
        analysis_request = AnalysisRequest(
            ticker=ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            priority=request.priority
        )
        
        # Create individual analysis
        response = await create_analysis(analysis_request, background_tasks)
        job_ids.append(response.job_id)
    
    return {
        "message": f"Created {len(job_ids)} analysis jobs",
        "job_ids": job_ids,
        "status": "bulk_created"
    }

@router.delete("/analyze/{job_id}")
async def cancel_analysis(job_id: str):
    """Cancel a running analysis job"""
    
    if job_id in active_jobs:
        job_data = active_jobs[job_id]
        if job_data["status"] == AnalysisStatus.RUNNING:
            # Mark for cancellation (implementation depends on execution model)
            job_data["status"] = AnalysisStatus.FAILED
            job_data["error_message"] = "Job cancelled by user"
            
            # Move to completed
            completed_jobs[job_id] = AnalysisResponse(
                job_id=job_id,
                status=AnalysisStatus.FAILED,
                ticker=job_data["ticker"],
                created_at=job_data["created_at"],
                error_message="Job cancelled by user"
            )
            
            del active_jobs[job_id]
            return {"message": f"Analysis {job_id} cancelled"}
        else:
            raise HTTPException(status_code=400, detail="Job cannot be cancelled in current state")
    
    raise HTTPException(status_code=404, detail="Job not found")

@router.get("/jobs")
async def list_jobs(limit: int = 50, status: str = None):
    """List recent analysis jobs with optional status filter"""
    
    all_jobs = []
    
    # Add active jobs
    for job_data in active_jobs.values():
        if not status or job_data["status"] == status:
            all_jobs.append({
                "job_id": job_data["job_id"],
                "ticker": job_data["ticker"],
                "status": job_data["status"],
                "created_at": job_data["created_at"],
                "progress": job_data.get("progress", 0)
            })
    
    # Add completed jobs
    for response in completed_jobs.values():
        if not status or response.status == status:
            all_jobs.append({
                "job_id": response.job_id,
                "ticker": response.ticker,
                "status": response.status,
                "created_at": response.created_at,
                "completed_at": response.completed_at
            })
    
    # Sort by creation time (most recent first) and limit
    all_jobs.sort(key=lambda x: x["created_at"], reverse=True)
    return {"jobs": all_jobs[:limit]}

# Background execution function
async def execute_financial_analysis(job_id: str, request: AnalysisRequest):
    """
    Execute the financial analysis in background.
    This function orchestrates the CrewAI agents and tasks.
    """
    
    try:
        # Update job status to running
        if job_id in active_jobs:
            active_jobs[job_id]["status"] = AnalysisStatus.RUNNING
            active_jobs[job_id]["progress"] = 10
        
        logger.info(f"Starting analysis execution for job {job_id}")
        
        # Setup output directory
        output_dir = os.getenv("OUTPUT_DIR", "/app/outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create agents with dynamic configuration
        market_analyst = create_market_analyst(
            ticker=request.ticker,
            tools=tools,
            custom_instructions=request.custom_instructions
        )
        
        investment_strategist = create_investment_strategist(
            ticker=request.ticker,
            custom_instructions=request.custom_instructions
        )
        
        # Update progress
        if job_id in active_jobs:
            active_jobs[job_id]["progress"] = 30
        
        # Create tasks
        analysis_task = create_analysis_task(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            agent=market_analyst,
            output_dir=output_dir,
            custom_instructions=request.custom_instructions
        )
        
        strategy_task = create_strategy_task(
            ticker=request.ticker,
            agent=investment_strategist,
            output_dir=output_dir,
            context_tasks=[analysis_task],
            custom_instructions=request.custom_instructions
        )
        
        # Update progress
        if job_id in active_jobs:
            active_jobs[job_id]["progress"] = 50
        
        # Create crew and execute
        crew = Crew(
            agents=[market_analyst, investment_strategist],
            tasks=[analysis_task, strategy_task],
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
        )
        
        # Execute analysis
        logger.info(f"Executing crew for job {job_id}")
        result = crew.kickoff()
        
        # Update progress
        if job_id in active_jobs:
            active_jobs[job_id]["progress"] = 90
        
        # Process results
        analysis_result = {
            "analysis": str(result),
            "market_analysis_file": f"{output_dir}/market_analysis_{request.ticker}.md",
            "strategy_file": f"{output_dir}/investment_strategy_{request.ticker}.md",
            "completed_at": datetime.now().isoformat(),
            "ticker": request.ticker,
            "date_range": f"{request.start_date} to {request.end_date}"
        }
        
        # Move to completed jobs
        completed_job = AnalysisResponse(
            job_id=job_id,
            status=AnalysisStatus.COMPLETED,
            ticker=request.ticker,
            created_at=active_jobs[job_id]["created_at"],
            completed_at=datetime.now(),
            result=analysis_result,
            progress=100
        )
        
        completed_jobs[job_id] = completed_job
        
        # Remove from active jobs
        if job_id in active_jobs:
            del active_jobs[job_id]
        
        logger.info(f"Analysis completed successfully for job {job_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed for job {job_id}: {e}")
        
        # Mark as failed
        failed_job = AnalysisResponse(
            job_id=job_id,
            status=AnalysisStatus.FAILED,
            ticker=request.ticker,
            created_at=active_jobs[job_id]["created_at"] if job_id in active_jobs else datetime.now(),
            error_message=str(e)
        )
        
        completed_jobs[job_id] = failed_job
        
        if job_id in active_jobs:
            del active_jobs[job_id]

# Helper functions
async def check_ollama_connection() -> bool:
    """Check if Ollama service is accessible"""
    try:
        import httpx
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ollama_url}/api/tags", timeout=5.0)
            return response.status_code == 200
    except:
        return False

def check_storage_access() -> bool:
    """Check if storage directory is accessible"""
    try:
        output_dir = os.getenv("OUTPUT_DIR", "/app/outputs")
        os.makedirs(output_dir, exist_ok=True)
        return os.access(output_dir, os.W_OK)
    except:
        return False
