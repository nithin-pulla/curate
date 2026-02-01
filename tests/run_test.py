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

    # 3. Create User
    print("\n[Step 2] Creating Test User Profile...")
    user_payload = {
        "name": "Hyderabadi Foodie",
        "email": f"test_{int(time.time())}@example.com",
        "preferences": "I love spicy South Indian tiffins like Dosa and Idly. I enjoy chutneys and podi.",
        "allergens": [] 
    }
    
    try:
        r = requests.post(f"{BASE_URL}/users", json=user_payload)
        r.raise_for_status()
        user_id = r.json()["user_id"]
        print(f"✅ User Created: {user_id}")
    except Exception as e:
        print(f"❌ FAIL: User creation error - {e}")
        return

    # 4. Get Restaurant ID
    # We need to query the DB to get the ID created by the seeder.
    # Quick hack: Use SQLAlchemy directly or fetch via API if we had a GetRestaurants endpoint.
    # Since we don't present that endpoint in README/Task, let's peek directly using models imports 
    # OR simpler: The seeder prints it? No, seeder doesn't return it easily to this process.
    # Let's add a quick query using the code imports.
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.models import Restaurant
    
    # Re-use connection string from main.py logic (env)
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_SERVER")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")
    
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
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
