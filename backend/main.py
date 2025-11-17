"""
MedSummarize Backend API
FastAPI application for medical report processing with OCR, NLP, and AI summarization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from core.config import settings
from api.routes import upload, process, summarize, health
from core.logging import setup_logging
from database.database import init_db

# Setup logging
setup_logging()

# Initialize database tables
init_db()

app = FastAPI(
    title="MedSummarize API",
    description="AI-powered medical report summarization system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(process.router, prefix="/api/process", tags=["process"])
app.include_router(summarize.router, prefix="/api/summarize", tags=["summarize"])
app.include_router(health.router, prefix="/api/health", tags=["health"])

# Mount static files for processed reports
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MedSummarize API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )