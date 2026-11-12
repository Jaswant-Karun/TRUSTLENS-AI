"""
TRUSTLENS AI - Complete Production FastAPI Backend Application
"Detect the deception before people lose their money."

Advanced Multilingual Digital Fraud Intelligence & Prevention Platform API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi

from backend.app.config.settings import settings
from backend.app.core.logging import logger
from backend.app.database.manager import db_manager
from backend.app.database.indexes import init_database_indexes
from backend.app.services.auth_service import auth_service
from backend.app.api.v1.api import api_router
from backend.app.middleware.logging_middleware import RequestLoggingMiddleware
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.middleware.rate_limit import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: initialize database, indexes, and initial admin on startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]...")
    # 1. Connect to MongoDB Atlas (or in-memory resilient fallback)
    await db_manager.connect()
    # 2. Build collection indexes
    await init_database_indexes()
    # 3. Seed initial admin user if not present
    await auth_service.seed_initial_admin()
    yield
    # 4. Graceful shutdown
    logger.info("Shutting down TRUSTLENS AI application...")
    await db_manager.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "**TRUSTLENS AI API** — Advanced Multilingual Digital Fraud Intelligence & Prevention Platform.\n\n"
        "Detects scam communications, phishing URLs, and psychological coercion across SMS, WhatsApp, and emails. "
        "Provides transparent risk aggregation, forensic explainability, and campaign intelligence."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Security Headers Middleware (OWASP hardening)
app.add_middleware(SecurityHeadersMiddleware)

# 3. Request Logging & Process Timing Middleware
app.add_middleware(RequestLoggingMiddleware)

# 4. Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# Mount API v1 Routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    """Root platform metadata."""
    return {
        "platform": "TRUSTLENS AI",
        "tagline": "Detect the deception before people lose their money.",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "documentation": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "analyze": f"{settings.API_V1_STR}/analyze",
            "analyses": f"{settings.API_V1_STR}/analyses",
            "campaigns": f"{settings.API_V1_STR}/campaigns",
            "models": f"{settings.API_V1_STR}/models",
            "reports": f"{settings.API_V1_STR}/reports",
        },
    }


# Custom Exception Handlers ensuring structured JSON errors

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic validation errors with structured JSON output."""
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append({"location": loc, "message": err.get("msg")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request payload format.",
            "details": errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global fallback exception handler ensuring JSON error response format without credentials leaks."""
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred during threat processing.",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


def custom_openapi():
    """Enhances Swagger UI with JWT Bearer Security Scheme."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT Bearer Token (obtain via /api/v1/auth/login)",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
