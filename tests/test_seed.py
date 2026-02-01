import os
import json
import time
import uuid
import psycopg2
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load the .env file automatically
load_dotenv() 

# Load API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in .env file")

# Initialize the Client
client = genai.Client(api_key=GOOGLE_API_KEY)

# 2. DB Config
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_SERVER")
DB_PORT = os.getenv("POSTGRES_PORT")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def get_embedding(text):
    """Generates a 768-dim vector using the new SDK."""
    try:
        response = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Error embedding text: {e}")
        return [0.0] * 768

def enrich_dish(item_name, grouping):
    """Uses Gemini to generate description and allergens."""
    prompt = f"""
    Describe the dish '{item_name}' (Category: {grouping}). 
    Provide a 1-sentence description and a list of common allergens.
    Return ONLY valid JSON with this format:
    {{
        "description": "...",
        "allergens": ["..."]
    }}
    """
    try:
        # Using the latest available flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error enriching dish {item_name}: {e}")
        return {"description": f"A delicious {item_name}", "allergens": []}

def seed_test_data():
    conn = get_db_connection()
    cur = conn.cursor()

    print("--- Dynamic Test Seeding ---")
    
    # 1. Wipe Tables
    print("Resetting Tables...")
    cur.execute("TRUNCATE TABLE dishes, restaurants, users CASCADE;")
    
    # 2. CREATE DUMMY OWNER
    owner_id = str(uuid.uuid4())
    print(f"Creating Test Owner ({owner_id})...")
    cur.execute(
        "INSERT INTO users (id, email, hashed_password) VALUES (%s, %s, %s)",
        (owner_id, "restaurant_owner@test.com", "dummy_hash")
    )

    # 3. Find JSON Files
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            name_part = filename.replace(".json", "")
            if "-" in name_part:
                r_name = name_part.rsplit("-", 1)[0].replace("_", " ").title()
                r_id = name_part.rsplit("-", 1)[1]
            else:
                continue

            print(f"Processing: {r_name} (from {filename})")

            # 4. Create Restaurant
            cur.execute(
                "INSERT INTO restaurants (id, name, address, owner_id) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (r_id, r_name, "123 Test St", owner_id)
            )

            # 5. Load Dishes
            with open(os.path.join(data_dir, filename), 'r') as f:
                data = json.load(f)
                
            menu_items = data.get("menu", [])
            for group in menu_items:
                group_name = group.get("grouping")
                print(f"  Group: {group_name}")
                
                for item in group.get("items", []):
                    d_name = item["item"]
                    d_price = item["price"]
                    dish_id = str(uuid.uuid4()) 
                    
                    print(f"    Enriching: {d_name}...", end="", flush=True)
                    
                    enriched = enrich_dish(d_name, group_name)
                    vector_text = f"{d_name} {enriched['description']} {group_name}"
                    vector = get_embedding(vector_text)
                    
                    cur.execute(
                        """
                        INSERT INTO dishes 
                        (id, name, description, price, restaurant_id, spice_level, allergens, embedding, ingredients, tags, is_available)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            dish_id, 
                            d_name, 
                            enriched['description'], 
                            d_price, 
                            r_id, 
                            2,
                            enriched['allergens'],
                            vector,
                            [], # ingredients default
                            [], # tags default
                            True # is_available default
                        )
                    )
                    print("Done.")
                    time.sleep(0.5)

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    seed_test_data()