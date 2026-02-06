import sys
import os
import time
import requests
import subprocess
import json
from dotenv import load_dotenv

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(repo_root)

# Load env
load_dotenv()

# Require API_URL from env
BASE_URL = os.getenv("API_URL")
if not BASE_URL:
    raise ValueError("API_URL not set in .env")

API_HOST = BASE_URL.replace("/api/v1", "")

def wait_for_server():
    """Waits for the backend to be healthy"""
    print("Waiting for server to start...")
    for _ in range(10):
        try:
            r = requests.get(f"{API_HOST}/health")
            if r.status_code == 200:
                print("Server is UP!")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    return False

def run_tests():
    print("--- Starting Integration Test Suite ---")

    # 1. Run Seeder
    print("\n[Step 1] Running Dynamic Seeder...")
    subprocess.run(["python", "tests/test_seed.py"], check=True)

    # 2. Start Backend (if not running, but usually for tests we might assume it involves docker or we start it)
    # For this script we assume Docker is UP. If not, the health check will fail.
    if not wait_for_server():
        print("❌ FAIL: Server not running. Please start 'docker-compose up'")
        return

    # Setup DB Connection for direct checks
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.models import Restaurant, User
    
    # Re-use connection string from main.py logic (env)
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_SERVER")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")
    
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    # 3. User Setup (Static or Dynamic)
    print("\n[Step 2] Setting up Test User...")
    user_id = os.getenv("TEST_USER_ID")
    test_password = os.getenv("TEST_USER_PASSWORD", "TestPassword123!")
    test_prefs = os.getenv("TEST_USER_PREFERENCES", "I love spicy South Indian tiffins.")

    if user_id:
        print(f"⏩ Using Static Test User ID from .env: {user_id}")
        # Ensure user exists in DB (since seeder wiped it)
        db = SessionLocal()
        existing_user = db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            print(f"⚠️ User {user_id} missing in DB (wiped). Re-creating profile...")
            
            # Generate dummy embedding
            from backend.main import get_gemini_embedding
            pref_text = test_prefs
            
            # Create User directly
            static_user = User(
                id=user_id,
                name="Static Test User",
                email=f"test_static_{int(time.time())}@example.com", # Email doesn't matter for DB logic
                hashed_password="managed_by_supabase",
                constraints=[],
                allergens_strict=[],
                spice_tolerance=3,
                budget_setting=2,
                taste_embedding=get_gemini_embedding(pref_text)
            )
            db.add(static_user)
            db.commit()
            print("✅ Static User Re-seeded into DB.")
        db.close()
    else:
        print("Creating New Test User...")
        user_payload = {
            "name": "Hyderabadi Foodie",
            "email": f"test_{int(time.time())}@example.com",
            "password": test_password, # Required for Supabase Auth
            "preferences": test_prefs,
            "allergens": [] 
        }
        
        try:
            r = requests.post(f"{BASE_URL}/users", json=user_payload)
            r.raise_for_status()
            user_id = r.json()["user_id"]
            print(f"✅ User Created: {user_id}")
        except Exception as e:
            print(f"❌ FAIL: User creation error - {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return

    # 4. Get Restaurant ID
    db = SessionLocal()
    restaurant = db.query(Restaurant).filter(Restaurant.name == "Ulavacharu Tiffins").first()
    
    if not restaurant:
        print("❌ FAIL: Restaurant 'Ulavacharu Tiffins' not found in DB.")
        return
        
    restaurant_id = restaurant.id
    print(f"✅ Found Restaurant ID: {restaurant_id}")
    db.close()

    # 5. Get Recommendations
    print("\n[Step 3] Fetching Smart Recommendations...")
    rec_payload = {
        "user_id": user_id,
        "restaurant_id": restaurant_id,
        "mood": "Something crispy and spicy for breakfast"
    }
    
    r = requests.post(f"{BASE_URL}/recommendations", json=rec_payload)
    if r.status_code != 200:
        print(f"❌ FAIL: Recommendation API error {r.status_code} - {r.text}")
        return
        
    bundles = r.json()
    print(f"Received {len(bundles)} bundles.")
    
    if not bundles:
        print("❌ FAIL: No bundles returned.")
        return

    # 6. Analysis (The Grader)
    top_pick = bundles[0]
    dish_name = top_pick["dishes"][0]["name"]
    explanation = top_pick["explanation"]
    
    print(f"\n🏆 Top Recommendation: {dish_name}")
    print(f"📝 AI Explanation: \"{explanation}\"")
    
    # Grader Logic
    # 1. Relevance: Did it pick a Dosa or Idly?
    relevant_keywords = ["Dosa", "Idly", "Vada", "Pesarattu"]
    is_relevant = any(k in dish_name for k in relevant_keywords)
    
    if is_relevant:
        print("✅ PASS: Relevance Check (Matched Tiffin items)")
    else:
        print(f"⚠️ WARN: Relevance Check (Did it pick {dish_name} correctly for 'crispy/spicy'?)")

    # 2. Explanation Quality
    fallback_phrase = "We think you'll like"
    if fallback_phrase in explanation:
         print("❌ FAIL: AI Explanation failed (Fallback detected).")
    else:
         print("✅ PASS: AI Logic active (Dynamic explanation generated).")

if __name__ == "__main__":
    run_tests()
