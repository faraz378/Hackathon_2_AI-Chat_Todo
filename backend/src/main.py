"""FastAPI application initialization."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import tasks, auth, chat
from .core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Startup: Initialize database tables
        logger.info("Initializing database tables...")
        await init_db()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown: cleanup if needed


# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="Backend Core & Data Layer for task management with user-scoped data handling",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://frontend-9z4asc243-faraz378s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Task Management API is running",
        "version": "1.0.0"
    }


# Router registration
app.include_router(auth.router)
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(chat.router, tags=["Chat"])
