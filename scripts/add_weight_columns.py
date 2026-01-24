import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.models import engine

def add_columns():
    """Manually add missing columns to user_sessions table"""
    print("Connecting to database...")
    
    with engine.connect() as conn:
        try:
            # 1. Add weight_stage (Integer)
            print("Adding column: weight_stage")
            conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS weight_stage INTEGER DEFAULT 0"))
            
            # 2. Add weight_answers (JSON)
            print("Adding column: weight_answers")
            # Determine JSON type based on dialect (PostgreSQL uses JSON/JSONB, SQLite uses TEXT)
            # Assuming PostgreSQL based on psycopg2 error in user request
            conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS weight_answers JSONB DEFAULT '{}'::jsonb"))
            
            # 3. Add weights (JSON)
            print("Adding column: weights")
            conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS weights JSONB DEFAULT '{}'::jsonb"))
            
            conn.commit()
            print("✅ Successfully added columns!")
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            print("Attempting SQLite fallback just in case...")
            # Fallback for SQLite (if environment differs)
            try:
                conn.execute(text("ALTER TABLE user_sessions ADD COLUMN weight_stage INTEGER DEFAULT 0"))
                conn.execute(text("ALTER TABLE user_sessions ADD COLUMN weight_answers JSON DEFAULT '{}'"))
                conn.execute(text("ALTER TABLE user_sessions ADD COLUMN weights JSON DEFAULT '{}'"))
                conn.commit()
                print("✅ Successfully added columns (SQLite fallback)!")
            except Exception as e2:
                 print(f"❌ Fallback failed: {e2}")

if __name__ == "__main__":
    add_columns()
