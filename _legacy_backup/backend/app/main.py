"""
AI Interview Evaluator — FastAPI entrypoint.

Phase 1 scope: app bootstrap, middleware, health check, and error handling
skeleton only. Routers for auth/interviews/questions/evaluation/reports are
wired in during their respective phases (2-11).
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger import jsonlogger

from app.core.config import settings

# ---------------------------------------------------------------------------
# Logging setup (structured JSON logs; never log secrets or raw answers)
# ---------------------------------------------------------------------------
logger = logging.getLogger("ai_interview_evaluator")
logger.setLevel(settings.LOG_LEVEL)
_handler = logging.StreamHandler()
if settings.LOG_FORMAT == "json":
    _handler.setFormatter(
        jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
logger.addHandler(_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Interview Evaluator API", extra={"env": settings.ENVIRONMENT})
    yield
    logger.info("Shutting down AI Interview Evaluator API")


app = FastAPI(
    title="AI Interview Evaluator API",
    description="AI/NLP-powered technical interview simulation and evaluation platform.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request timing / access log middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return response


# ---------------------------------------------------------------------------
# Global error handling — never leak raw exceptions to the client
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", extra={"path": request.url.path, "error": str(exc)})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred. Please try again later.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["system"])
async def health_check():
    return {"success": True, "status": "ok", "environment": settings.ENVIRONMENT}


# ---------------------------------------------------------------------------
# Routers (uncommented progressively in later phases)
# ---------------------------------------------------------------------------
# from app.api import auth, interviews, questions, evaluation, reports, dashboard, admin
# app.include_router(auth.router, prefix=settings.API_V1_PREFIX + "/auth", tags=["auth"])
# app.include_router(interviews.router, prefix=settings.API_V1_PREFIX + "/interviews", tags=["interviews"])
# app.include_router(questions.router, prefix=settings.API_V1_PREFIX + "/questions", tags=["questions"])
# app.include_router(evaluation.router, prefix=settings.API_V1_PREFIX + "/evaluate", tags=["evaluation"])
# app.include_router(reports.router, prefix=settings.API_V1_PREFIX + "/reports", tags=["reports"])
# app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX + "/dashboard", tags=["dashboard"])
# app.include_router(admin.router, prefix=settings.API_V1_PREFIX + "/admin", tags=["admin"])
