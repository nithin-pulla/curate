import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

from backend.models import Base, User, Dish
from backend.schemas import MealBundle, RecommendationRequest, DishResponse, UserOnboardingRequest

# Load env variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None
if not client:
    print("⚠️ WARNING: GOOGLE_API_KEY not set.")

# Database Setup
# Database Setup
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_SERVER")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    print("❌ CRITICAL: Missing Database/Env variables. Check .env file.")

print(f"🔌 CONNECTING TO DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Extension (Idempotent)
try:
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
        # Create Tables
        Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"DB Interface Error: {e}")

app = FastAPI(title="Curate API", version="v1")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

def get_gemini_embedding(text: str) -> List[float]:
    """Wrapper to get embedding from Gemini"""
    if not client: return [0.0] * 768
    try:
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Embedding Error: {e}")
        return [0.0] * 768

def generate_explanation(dish_name: str, dish_desc: str, user_profile: str) -> str:
    """Uses Gemini Flash to explain the match"""
    if not client: return f"We think you'll like the {dish_name} based on your profile."
    try:
        prompt = f"""
        Context: The user has these preferences: "{user_profile}".
        Task: Recommend the dish "{dish_name}" ({dish_desc}).
        Output: Write a single sentence explaining why this dish fits their specific taste. Speak directly to the user ("You'll love...").
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"GenAI Error: {e}")
        return f"We think you'll like the {dish_name} based on your profile."

@app.post("/api/v1/recommendations", response_model=List[MealBundle])
def generate_recommendations(
    request: RecommendationRequest, 
    db: Session = Depends(get_db)
):
    print(f"🚀 Processing Request for User: {request.user_id}")

    # 1. Fetch User
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        print("❌ User not found in DB")
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Determine Search Vector
    search_vector = None
    user_context_str = ""
    
    if request.mood:
        print(f"Generating embedding for mood: {request.mood}")
        search_vector = get_gemini_embedding(request.mood)
        user_context_str = request.mood
    elif user.taste_embedding is not None:
        search_vector = user.taste_embedding
        user_context_str = "Standard constraints and spicy tolerance."
    else:
        user_context_str = "No specific profile."
    
    # 3. Query Dishes (REMOVED is_available check to avoid NULL issues)
    query = db.query(Dish).filter(Dish.restaurant_id == request.restaurant_id)
    
    all_dishes = query.all()
    print(f"📊 Found {len(all_dishes)} dishes for restaurant {request.restaurant_id}")
    
    safe_candidates = []
    user_strict_allergens = set(user.allergens_strict) if user.allergens_strict else set()
    
    for dish in all_dishes:
        dish_allergens = set(dish.allergens) if dish.allergens else set()
        if not dish_allergens.isdisjoint(user_strict_allergens):
            continue
        safe_candidates.append(dish)

    print(f"✅ Safe candidates after allergy check: {len(safe_candidates)}")

    if not safe_candidates:
        print("⚠️ No safe dishes found.")
        return []

    # 4. Neural Ranking
    ranked_dishes = []
    
    if search_vector is not None:
        try:
            safe_ids = [d.id for d in safe_candidates]
            # Query DB again to let pgvector do the heavy lifting
            ranked_dishes = db.query(Dish).filter(
                Dish.id.in_(safe_ids)
            ).order_by(
                Dish.embedding.l2_distance(search_vector)
            ).limit(3).all()
        except Exception as e:
            print(f"⚠️ Vector Sort Error: {e}")
            ranked_dishes = safe_candidates[:3]
    else:
        ranked_dishes = safe_candidates[:3]

    print(f"🏆 Ranked top {len(ranked_dishes)} dishes")

    # 5. Generate Bundles with Explanation
    bundles = []
    if ranked_dishes:
        top_dish = ranked_dishes[0]
        
        explanation = generate_explanation(top_dish.name, top_dish.description or "", user_context_str)
        
        bundles.append(MealBundle(
            title="Top Match",
            dishes=[DishResponse.model_validate(top_dish)],
            total_price=top_dish.price,
            explanation=explanation
        ))
        
        if len(ranked_dishes) > 1:
            second = ranked_dishes[1]
            bundles.append(MealBundle(
                title="Alternative Choice",
                dishes=[DishResponse.model_validate(second)],
                total_price=second.price,
                explanation=f"A close second: {second.name}."
            ))

    return bundles

@app.post("/api/v1/users", response_model=dict)
def create_user(
    request: UserOnboardingRequest,
    db: Session = Depends(get_db)
):
    # 1. Generate Embedding from Preferences
    print(f"Generating profile for {request.name} based on: {request.preferences}")
    preference_embedding = get_gemini_embedding(request.preferences)
    
    # 2. Create User Record
    import uuid
    new_user_id = str(uuid.uuid4())
    
    new_user = User(
        id=new_user_id,
        name=request.name,
        email=request.email,
        hashed_password="mock_password_for_mvp", # Placeholder
        constraints=[], # Can be expanded later
        allergens_strict=request.allergens,
        spice_tolerance=3, # Default
        budget_setting=2, # Default
        taste_embedding=preference_embedding
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"user_id": new_user.id}
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.get("/health")
def health_check():
    return {"status": "ok"}
