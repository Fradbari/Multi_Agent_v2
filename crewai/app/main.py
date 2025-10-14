import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.routes import router as api_router

# ✅ CORRETTO - Configurazione logging sicura
def setup_logging():
    """Setup logging with proper directory creation"""
    # Ensure storage directory exists
    storage_dir = "/app/storage"
    os.makedirs(storage_dir, exist_ok=True)
    
    # Configure logging DOPO aver creato le directory
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'{storage_dir}/crewai_api.log')
        ],
        force=True  # Forza reconfigurazione se necessario
    )

# Setup logging at module level - MA con directory creation
try:
    setup_logging()
except PermissionError:
    # Fallback a solo console se permission problem
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

logger = logging.getLogger(__name__)

"""
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/storage/crewai_api.log')
    ]
)

logger = logging.getLogger(__name__)
"""

# Lifespan events for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 CrewAI Financial Analysis API starting up...")
    
    # Verify environment
    required_dirs = ["/app/storage", "/app/outputs"]
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"✅ Directory verified: {dir_path}")
    
    # Check Ollama connection
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    logger.info(f"🤖 Ollama configured at: {ollama_url}")
    
    logger.info("✅ CrewAI Financial Analysis API ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 CrewAI Financial Analysis API shutting down...")

# Create FastAPI application
app = FastAPI(
    title="CrewAI Financial Analysis API",
    description="""
    🚀 **Multi-Agent Financial Analysis Service**
    
    A scalable API service powered by CrewAI multi-agent system for comprehensive stock analysis.
    
    ## Features
    - 📊 **Dynamic Analysis**: Configure ticker, date ranges, and custom instructions
    - 🤖 **Multi-Agent**: Market Research Analyst + Investment Strategist collaboration
    - ⚡ **Async Processing**: Background job execution with progress tracking
    - 📈 **Bulk Operations**: Analyze multiple tickers simultaneously
    - 🔍 **Job Management**: Track, monitor, and cancel analysis jobs
    
    ## Usage
    1. **POST /api/analyze** - Create new analysis
    2. **GET /api/analyze/{job_id}** - Check status and get results
    3. **POST /api/analyze/bulk** - Bulk ticker analysis
    4. **GET /api/health** - Service health check
    
    Built with FastAPI + CrewAI + Ollama for enterprise-grade financial analysis.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Log request details
    process_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )

# Include API routes
app.include_router(api_router, prefix="/api", tags=["Financial Analysis"])

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API service information and status"""
    return {
        "service": "CrewAI Financial Analysis API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now(),
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "analyze": "/api/analyze",
            "jobs": "/api/jobs"
        },
        "description": "Multi-agent financial analysis powered by CrewAI"
    }

# Development server entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
