import sys
from pathlib import Path

# Automatically ensure 'Backend/src' is in sys.path when running via IDE debugger
_src_dir = str(Path(__file__).resolve().parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_knowledge_inbox.config import CORS_ORIGINS, CORS_ORIGIN_REGEX, PORT, logger
from ai_knowledge_inbox.routes import health, items, ingest, query
from ai_knowledge_inbox.error_handlers import register_error_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown banner"""
    logger.info("============================================================")
    logger.info("🚀 Backend Server Ready!")
    logger.info("📡 Base API:      http://127.0.0.1:%s", PORT)
    logger.info("📖 Swagger Docs:  http://127.0.0.1:%s/docs", PORT)
    logger.info("============================================================")
    yield
    logger.info("Backend Server shutting down gracefully...")

def create_app() -> FastAPI:
    """Application factory for AI Knowledge Inbox"""
    app = FastAPI(
        title="AI Knowledge Inbox API",
        description="Production-style minimal RAG pipeline for notes and URL content",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    # Bulletproof CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_origin_regex=CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register modular route handlers
    app.include_router(health.router)
    app.include_router(items.router)
    app.include_router(ingest.router)
    app.include_router(query.router)

    # Register centralized global error handlers
    register_error_handlers(app)

    return app

app = create_app()

def dev():
    """CLI shortcut for `uv run dev`"""
    uvicorn.run("ai_knowledge_inbox.main:app", host="127.0.0.1", port=PORT, reload=True)

if __name__ == "__main__":
    dev()
