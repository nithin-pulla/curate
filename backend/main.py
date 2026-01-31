from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List

from backend.models import Base
from backend.schemas import MealBundle, RecommendationRequest
from backend.engine import RecommendationEngine

# Database Setup (Using SQLite for MVP simplicity if PG not available, 
# but TDD says Postgres. I'll stick to the engine pattern, assuming env vars or default)
# For this file generation, I'll use a placeholder connection string.
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5435/curate_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Extension if not exists (Fix for vector type error)
with engine.connect() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    connection.commit()

# Create Tables (Safe to run if they exist?)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Curate API", version="v1")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/recommendations", response_model=List[MealBundle])
def generate_recommendations(
    request: RecommendationRequest, 
    db: Session = Depends(get_db)
):
    """
    Generates personalized meal bundles for a given user and restaurant.
    Strictly filters unsafe dishes based on user allergies.
    """
    rec_engine = RecommendationEngine(db)
    
    try:
        bundles = rec_engine.generate_recommendations(
            user_id=request.user_id,
            restaurant_id=request.restaurant_id
        )
        
        if not bundles:
            # Option A: Return 404
            # raise HTTPException(status_code=404, detail="No safe options found.")
            
            # Option B: Return empty list (200 OK) with client handling
            return []
            
        return bundles
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
