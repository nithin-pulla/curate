import sys
import os
import time
import uuid
import google.generativeai as genai
from dotenv import load_dotenv

# Add local path to sys.path to ensure imports work
sys.path.append(os.getcwd())

# Load environment variables
load_dotenv()

from sqlalchemy.orm import Session
from backend.main import SessionLocal, engine, Base
from backend.models import User, Restaurant, Dish

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
    print("Please create a .env file with GOOGLE_API_KEY=your_key")
    sys.exit(1)

genai.configure(api_key=api_key)

def get_embedding(text: str):
    """Generates an embedding using Google Gemini models/text-embedding-004"""
    try:
        # Retry logic could be added here for production
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding for '{text}': {e}")
        # Fallback for dev if API fails? Better to fail hard so we know.
        raise e

def seed_data():
    print("--- Seeding Database with Gemini Embeddings ---")
    
    # 1. Reset Database
    print("Dropping and creating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 2. Create Restaurant
        print("Creating Restaurant 'Bistro 42'...")
        restaurant_id = str(uuid.uuid4())
        bistro = Restaurant(
            id=restaurant_id,
            name="Bistro 42",
            address="42 Food Lane",
            owner_id="admin_chef"
        )
        db.add(bistro)
        
        # 3. Create Menu (10 Dishes)
        print("Creating Menu & Generating Embeddings (this may take a moment)...")
        dishes_data = [
            {"name": "Peanut Satay", "price": 12.00, "allergens": ["peanuts", "soy"], "tags": ["spicy", "asian"], "desc": "Grilled chicken skewers with rich peanut sauce"},
            {"name": "Vegan Salad", "price": 10.00, "allergens": [], "tags": ["vegan", "healthy"], "desc": "Fresh greens with balsamic vinaigrette"},
            {"name": "Cheeseburger", "price": 15.00, "allergens": ["gluten", "dairy"], "tags": ["comfort_food", "american"], "desc": "Juicy beef patty with cheddar cheese"},
            {"name": "Shrimp Scampi", "price": 22.00, "allergens": ["shellfish", "gluten"], "tags": ["seafood", "italian"], "desc": "Shrimp sautéed in garlic butter sauce"},
            {"name": "Mushroom Omelette", "price": 11.00, "allergens": ["eggs"], "tags": ["vegetarian", "breakfast"], "desc": "Fluffy omelette with sautéed mushrooms"},
            {"name": "Tofu Stir Fry", "price": 13.00, "allergens": ["soy"], "tags": ["vegan", "asian"], "desc": "Crispy tofu with mixed vegetables"},
            {"name": "Walnut Brownie", "price": 8.00, "allergens": ["tree_nuts", "gluten", "eggs"], "tags": ["dessert", "sweet"], "desc": "Rich chocolate brownie with walnuts"},
            {"name": "Salmon Fillet", "price": 25.00, "allergens": ["fish"], "tags": ["healthy", "seafood"], "desc": "Pan-seared salmon with lemon herbs"},
            {"name": "Chicken Noodle Soup", "price": 9.00, "allergens": ["gluten"], "tags": ["comfort_food", "soup"], "desc": "Warm soup with chicken and egg noodles"},
            {"name": "Pasta Primavera", "price": 16.00, "allergens": ["gluten"], "tags": ["vegan", "vegetarian", "italian"], "desc": "Pasta with fresh seasonal vegetables"}
        ]
        
        for d in dishes_data:
            # Create a rich text representation for the embedding
            # Combining Name, Tags, and Description for better semantic matching
            embedding_text = f"{d['name']}: {d['desc']}. Tags: {', '.join(d['tags'])}"
            print(f"  Embedding: {d['name']}...")
            
            dish = Dish(
                id=str(uuid.uuid4()),
                restaurant_id=restaurant_id,
                name=d["name"],
                description=d["desc"],
                price=d["price"],
                ingredients=["secret_ingredient"], # Placeholder
                allergens=d["allergens"],
                tags=d["tags"],
                calories=500,
                spice_level=1,
                is_available=True,
                # CALL GEMINI API
                embedding=get_embedding(embedding_text) 
            )
            db.add(dish)
            time.sleep(0.5) # Rate limiting politeness
            
        # 4. Create User
        print("Creating User 'Safety Test' with Semantic Preferences...")
        user_id = str(uuid.uuid4())
        
        # User preference text: "I love spicy food and asian flavors"
        user_pref_text = "I love spicy food, asian flavors, and comfort meals."
        
        user = User(
            id=user_id,
            email="safety_test@curate.com",
            hashed_password="hashed_secret",
            constraints=[],
            allergens_strict=["peanuts"],
            spice_tolerance=3,
            budget_setting=2,
            # CALL GEMINI API
            taste_embedding=get_embedding(user_pref_text)
        )
        db.add(user)
        
        db.commit()
        print("✅ Seeding Complete with Real Embeddings!")
        print(f"User ID: {user_id}")
        print(f"Restaurant ID: {restaurant_id}")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
