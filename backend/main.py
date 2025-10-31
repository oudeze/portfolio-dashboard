"""
FastAPI backend for Personal Market Data Dashboard.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, market, websocket

app = FastAPI(
    title="Market Data Dashboard API",
    description="Backend API for personal trading dashboard",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(market.router, prefix="/api", tags=["market"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Market Data Dashboard API", "version": "0.1.0"}

