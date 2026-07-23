import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Import all module routers
from src.api.routers import (
    companies, screener, sectors, peers, 
    valuation, portfolio, documents, health
)

# Initialize FastAPI
app = FastAPI(
    title="Nifty 100 Corporate Analytics API",
    description="Backend API for financial data, clustering, and valuation metrics.",
    version="1.0.0"
)

# 1. CORS Middleware (Allow all origins for internal use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request Logging Middleware
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    
    logger.info(
        f"Method: {request.method} | Path: {request.url.path} | "
        f"Status: {response.status_code} | Response Time: {process_time:.4f}s"
    )
    return response

# 3. Router Registration (Prefix with /api/v1)
api_prefix = "/api/v1"

app.include_router(health.router, prefix=api_prefix, tags=["System Health"])
app.include_router(companies.router, prefix=api_prefix, tags=["Companies"])
app.include_router(screener.router, prefix=api_prefix, tags=["Screener"])
app.include_router(sectors.router, prefix=api_prefix, tags=["Sectors"])
app.include_router(peers.router, prefix=api_prefix, tags=["Peers"])
app.include_router(valuation.router, prefix=api_prefix, tags=["Valuation"])
app.include_router(portfolio.router, prefix=api_prefix, tags=["Portfolio"])
app.include_router(documents.router, prefix=api_prefix, tags=["Documents"])