"""AutoResumeFiller Backend API - Entry Point.

This module initializes the FastAPI application with CORS middleware,
startup/shutdown handlers, and health check endpoint. The backend serves
as the orchestration layer for AI providers, data management, and form
processing.

Endpoints:
    GET /              - Root endpoint with API information
    GET /api/status    - Health check endpoint
    GET /docs          - Interactive API documentation (Swagger UI)
    GET /redoc         - API documentation (ReDoc)
"""

import logging
from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for AutoResumeFiller - Intelligent job application "
        "form auto-filling with AI assistance. Provides endpoints for form "
        "analysis, AI-powered response generation, and user data management."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {settings.CORS_ORIGINS}")


@app.on_event("startup")
async def startup_event() -> None:
    """Application startup event handler.

    Logs backend initialization and configuration details.
    Future epics will add database connections, AI provider initialization, etc.
    """
    logger.info("=" * 70)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Server: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Application shutdown event handler.

    Logs backend shutdown. Future epics will add cleanup tasks
    (close database connections, flush logs, etc.).
    """
    logger.info("Shutting down Backend API")
    logger.info("Cleanup complete")


@app.get("/", response_model=Dict[str, str], tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint providing API information and navigation links.

    Returns:
        Dictionary with API name, version, and links to documentation endpoints.
    """
    return {
        "message": f"{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/status",
    }


@app.get("/api/status", response_model=Dict[str, str], tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for system verification.

    Used by the GUI dashboard and Chrome Extension to verify backend
    availability. Returns 200 OK if the server is operational.

    Returns:
        Dictionary with status ("healthy"), version, and UTC timestamp.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# Entry point for running with Python directly (development only)
if __name__ == "__main__":
    import uvicorn

    logger.warning(
        "Running with 'python backend/main.py' is for quick testing only. "
        "Use 'uvicorn backend.main:app --reload' for development."
    )

    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
