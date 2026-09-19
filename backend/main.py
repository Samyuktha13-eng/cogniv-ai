"""
FastAPI Main Application
Cognitive AI Game Backend Server

Usage:
    python -m backend.main
    or
    uvicorn backend.main:app --reload
"""

from pathlib import Path
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Load local environment variables (for GEMINI_API_KEY, etc.)
load_dotenv()

# Import routes
from backend.api import game_routes, outcome_routes, video_routes

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Cognitive AI Game Backend",
    description="Backend for dementia memory care game platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS - Allow requests from Unity and any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Cognitive AI Game Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "game": "/game",
            "outcomes": "/outcome",
            "health": "/"
        }
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

app.include_router(game_routes.router)
app.include_router(outcome_routes.router)
app.include_router(video_routes.router)

# Make generated MP4s accessible to the frontend.
backend_root = Path(__file__).resolve().parent
generated_videos_dir = backend_root / "generated_videos"
generated_videos_dir.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(generated_videos_dir)), name="videos")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global error handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Called when server starts."""
    logger.info("Cognitive AI Game Backend starting...")
    logger.info("Loading semantic action library...")
    from backend.blueprint.semantic_actions import SemanticActionLibrary
    library = SemanticActionLibrary()
    logger.info(f"Loaded {len(library.list_all_actions())} semantic actions")
    logger.info("Backend ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Called when server shuts down."""
    logger.info("Cognitive AI Game Backend shutting down...")


# ============================================================================
# EXAMPLE: How to start the server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run with: python -m backend.main
    # Or: uvicorn backend.main:app --reload
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║   Cognitive AI Game Backend                                    ║
    ║                                                                ║
    ║   Starting server...                                          ║
    ║   API Documentation: http://localhost:8000/docs               ║
    ║   Health: http://localhost:8000/health                        ║
    ║                                                                ║
    ║   Endpoints:                                                  ║
    ║   - POST   /game/create         (Create new game)             ║
    ║   - GET    /game/scene/{id}/{id} (Get scene)                  ║
    ║   - POST   /game/action         (Execute patient action)      ║
    ║   - GET    /game/blueprint/{id} (Get full blueprint)          ║
    ║   - POST   /outcome/record      (Record outcome)              ║
    ║   - GET    /outcome/patient/{id}/profile (Cognitive profile)  ║
    ║   - GET    /outcome/patient/{id}/games   (Patient games)      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
