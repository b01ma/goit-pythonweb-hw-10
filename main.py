import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

from src.api.auth import router as auth_router
from src.api.contacts import router as contacts_router
from src.api.users import limiter, router as users_router
from src.conf.config import setup_logging, settings

# Initialize logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def rate_limit_exception_handler(request: Request, exc: Exception) -> Response:
    """Bridge SlowAPI handler to FastAPI's ExceptionHandler type."""
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    raise exc


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_middleware(SlowAPIMiddleware)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup."""
    logger.info("Starting up application...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database URL: {settings.safe_database_url}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown."""
    logger.info("Shutting down application...")


# Health check endpoint
@app.get(
    "/health",
    tags=["system"],
    summary="Health check endpoint",
)
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
    }


# Include routers
app.include_router(auth_router)
app.include_router(contacts_router)
app.include_router(users_router)

logger.info(f"FastAPI application initialized: {settings.APP_TITLE} v{settings.APP_VERSION}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
