from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
import sqlalchemy
from app.api.routes import router as api_router
from app.core.config import settings

app = FastAPI(
    title="Planner.AI",
    description="AI-Powered Media Planning Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.railway.app",  # Railway domains
        "https://*.up.railway.app"  # Railway deployment domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Planner.AI API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        db.execute(sqlalchemy.text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": str(e)
        } 