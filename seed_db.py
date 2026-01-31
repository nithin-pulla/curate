import sys
import os
import random
import uuid

# Add local path to sys.path to ensure imports work
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from backend.main import SessionLocal, engine, Base
from backend.models import User, Restaurant, Dish

def generate_embedding(dim=1536):
    return [random.uniform(-1.0, 1.0) for _ in range(dim)]

def seed_data():
    print("--- Seeding Database ---")
    
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
        print("Creating Menu...")
        dishes_data = [
            {"name": "Peanut Satay", "price": 12.00, "allergens": ["peanuts", "soy"], "tags": ["spicy"]},
            {"name": "Vegan Salad", "price": 10.00, "allergens": [], "tags": ["vegan"]},
            {"name": "Cheeseburger", "price": 15.00, "allergens": ["gluten", "dairy"], "tags": ["comfort_food"]},
            {"name": "Shrimp Scampi", "price": 22.00, "allergens": ["shellfish", "gluten"], "tags": ["seafood"]},
            {"name": "Mushroom Omelette", "price": 11.00, "allergens": ["eggs"], "tags": ["vegetarian"]},
            {"name": "Tofu Stir Fry", "price": 13.00, "allergens": ["soy"], "tags": ["vegan"]},
            {"name": "Walnut Brownie", "price": 8.00, "allergens": ["tree_nuts", "gluten", "eggs"], "tags": ["dessert"]},
            {"name": "Salmon Fillet", "price": 25.00, "allergens": ["fish"], "tags": ["healthy"]},
            {"name": "Chicken Noodle Soup", "price": 9.00, "allergens": ["gluten"], "tags": ["comfort_food"]},
            {"name": "Pasta Primavera", "price": 16.00, "allergens": ["gluten"], "tags": ["vegan", "vegetarian"]}
        ]
        
        for d in dishes_data:
            dish = Dish(
                id=str(uuid.uuid4()),
                restaurant_id=restaurant_id,
                name=d["name"],
                description=f"Delicious {d['name']}",
                price=d["price"],
                ingredients=["secret_ingredient"],
                allergens=d["allergens"],
                tags=d["tags"],
                calories=500,
                spice_level=1,
                is_available=True,
                # Generate random embedding
                embedding=generate_embedding(1536) 
                # Note: This might fail if using SQLite as it doesn't support Vector type natively 
                # without specific extensions or mocks.
                # Assuming this runs against a Postgres with pgvector, or the models.py definition allows it.
            )
            db.add(dish)
            
        # 4. Create User
        print("Creating User with Peanut Allergy...")
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email="safety_test@curate.com",
            hashed_password="hashed_secret",
            constraints=[],
            allergens_strict=["peanuts"],
            spice_tolerance=3,
            budget_setting=2,
            taste_embedding=generate_embedding(1536)
        )
        db.add(user)
        
        db.commit()
        print("✅ Seeding Complete!")
        print(f"User ID: {user_id}")
        print(f"Restaurant ID: {restaurant_id}")
        
    except Exception as e:
        print(f"❌ Formatting Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
