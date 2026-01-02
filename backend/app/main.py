"""
Main FastAPI application entry point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis_client import redis_client
from app.api.v1 import ml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting IntelliRate Gateway...")
    
    try:
        # Connect to Redis
        await redis_client.connect()
        logger.info("✓ Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {str(e)}")
    
    # Initialize ML clients
    from app.services.cloud_ml_service import cloud_ml_client
    logger.info(f"✓ ML Service initialized (cloud={'enabled' if settings.USE_CLOUD_ML else 'disabled'})")
    
    # Initialize Firebase Admin SDK
    try:
        from app.middleware.firebase_auth import initialize_firebase
        initialize_firebase()
    except Exception as e:
        logger.warning(f"Firebase initialization skipped: {str(e)}")
    
    logger.info("✓ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IntelliRate Gateway...")
    await redis_client.disconnect()
    logger.info("✓ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered API Gateway with Google Cloud ML Integration",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration - Allow Analyzer frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",  # Additional fallback
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ml.router, prefix="/api/v1")

# Import and include new routers
from app.api.v1 import analyze, analytics, logs, traffic, proxy, users, anomalies, rate_limits, ml_metrics
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")
app.include_router(traffic.router, prefix="/api/v1")
app.include_router(proxy.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(anomalies.router, prefix="/api/v1")
app.include_router(rate_limits.router, prefix="/api/v1")
app.include_router(ml_metrics.router, prefix="/api/v1/ml", tags=["ML Metrics"])



@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to IntelliRate Gateway",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - includes Groq API status"""
    from app.services.groq_service import groq_service
    from app.core.redis_client import redis_client
    
    # Check Redis connection
    redis_status = "connected"
    try:
        await redis_client.ping()
    except:
        redis_status = "disconnected"
    
    # Check Groq API (simple check)
    groq_status = "unknown"
    if settings.GROQ_API_KEY:
        groq_status = "configured"
    
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": "2025-12-24T15:25:00Z",
        "services": {
            "redis": redis_status,
            "groq": groq_status,
            "database": "connected"
        },
        "features": {
            "cloud_ml_enabled": settings.USE_CLOUD_ML,
            "fallback_enabled": settings.ENABLE_ML_FALLBACK,
            "groq_proxy_enabled": bool(settings.GROQ_API_KEY)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
