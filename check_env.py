import sys
import os

def check_imports():
    print("--- Checking Imports ---")
    required_libs = [
        ("fastapi", "fastapi"),
        ("sqlalchemy", "sqlalchemy"),
        ("psycopg2", "psycopg2"),
        ("pgvector", "pgvector")
    ]
    
    missing = []
    for pip_name, import_name in required_libs:
        try:
            __import__(import_name)
            # visual cue for success could be added here if desired, but request asked for specific failures
        except ImportError:
            # Try to handle the case where pip name != import name if needed, 
            # but for these they are mostly same or standard.
            # pgvector is 'pgvector' in pip and 'pgvector' module? 
            # actually pgvector python client is `pgvector`.
            missing.append(pip_name)
    
    if missing:
        for lib in missing:
             print(f"❌ Missing Library: {lib}")
        return False
    return True

def check_db_connection():
    print("\n--- Checking Database Connection ---")
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # URL from env
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_SERVER")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")
    
    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Successfully connected to database at {DB_HOST}:{DB_PORT}.")
        return True
    except Exception as e:
        print(f"❌ Database Connection Failed. Check Docker. Error: {e}")
        return False

def main():
    imports_ok = check_imports()
    # If imports fail, likely can't test DB properly if sqlalchemy/psycopg2 missing
    if not imports_ok:
        print("\nPlease install missing libraries using pip install ...")
        sys.exit(1)
        
    db_ok = check_db_connection()
    
    if imports_ok and db_ok:
        print("\n✅ Environment Healthy & Database Connected!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
