"""
FastAPI backend for Personal Market Data Dashboard.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import alerts, health, journal, market, orders, pnl, websocket
from prometheus_fastapi_instrumentator import Instrumentator

# Create database tables
Base.metadata.create_all(bind=engine)

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
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(pnl.router, prefix="/api/pnl", tags=["pnl"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Market Data Dashboard API", "version": "0.1.0"}

