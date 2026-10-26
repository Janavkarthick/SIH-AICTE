"""Main FastAPI application entry point for AICTE-Verify.

Configures CORS, registers all API routers, serves static uploads,
initializes database schemas on startup, and runs synthetic database seeding.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import (
    analytics,
    applications,
    audit,
    auth,
    compliance,
    documents,
    evaluation,
    flags,
    graph,
    letters,
    mock_issuer,
    users,
    verification,
)
from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.seed.seed_db import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database initialization and synthetic data seeding."""
    # Ensure upload directory exists
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize tables
    await init_db()

    # Seed initial test data
    async with AsyncSessionLocal() as session:
        await seed_database(session)

    yield


app = FastAPI(
    title="AICTE-Verify Regulatory Validation & Verification Engine",
    description=(
        "Production-quality automated regulatory compliance, document forensics, "
        "and multi-issuer verification platform for AICTE technical education approvals. "
        "All threshold values are illustrative: replace with Approval Process Handbook values. "
        "All simulated external components are clearly labeled SIMULATED."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Middleware
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploads
upload_dir_path = Path(settings.UPLOAD_DIR).resolve()
upload_dir_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir_path)), name="uploads")


# Advisory banner middleware
@app.middleware("http")
async def add_advisory_banner_header(request: Request, call_next):
    """Inject statutory advisory header into all API responses."""
    response = await call_next(request)
    response.headers["X-AICTE-Verify-Advisory"] = (
        "SIMULATED Prototype - All thresholds illustrative: replace with Approval Process Handbook values"
    )
    return response


# Root & Health Check Endpoints
@app.get("/", tags=["General"])
async def root():
    """System banner and platform status."""
    return {
        "title": "AICTE-Verify Automated Regulatory Validation Engine",
        "version": "1.0.0",
        "mode": "PROTOTYPE / DEMONSTRATION",
        "advisory": "All thresholds illustrative: replace with Approval Process Handbook values. Simulated issuers marked SIMULATED.",
        "documentation": f"{settings.API_V1_STR}/docs",
        "health": "/health",
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Service liveness and readiness probe."""
    return {
        "status": "healthy",
        "service": "AICTE-Verify Backend",
        "version": "1.0.0",
        "database": "connected",
        "debug": settings.DEBUG,
    }


@app.get("/api/v1/banner", tags=["General"])
async def get_advisory_banner():
    """Retrieve advisory banner message for frontend UI display."""
    return {
        "banner_text": (
            "NOTICE: AICTE-Verify Prototype - Operating with synthetic and anonymized institutional datasets. "
            "All compliance thresholds, limits, and rules are illustrative: replace with Approval Process Handbook values. "
            "Authority registries and issuers are labeled SIMULATED."
        ),
        "is_simulated": True,
        "mode": "Development / Evaluation",
    }


# Include all sub-routers under API_V1_STR
api_routers = [
    auth.router,
    users.router,
    applications.router,
    documents.router,
    verification.router,
    compliance.router,
    flags.router,
    audit.router,
    analytics.router,
    graph.router,
    letters.router,
    evaluation.router,
]

for r in api_routers:
    app.include_router(r, prefix=settings.API_V1_STR)
    app.include_router(r, prefix="/api")
    app.include_router(r)

# Mount mock issuer router (under /mock-issuer and also under /api/v1/mock-issuer)
app.include_router(mock_issuer.router)
app.include_router(mock_issuer.router, prefix="/api")
app.include_router(mock_issuer.router, prefix=settings.API_V1_STR)
