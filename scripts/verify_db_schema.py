import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import db_session
from app.models.session import UserSession

def verify_schema():
    """Verify that UserSession can be queried with new columns"""
    print("Verifying database schema...")
    try:
        # Try to query the first session object
        session = db_session.query(UserSession).first()
        if session:
            print(f"✅ Found session for user: {session.user_id}")
            print(f"   Status: {session.status}")
            # Access new columns to ensure they exist
            print(f"   Weight Stage: {session.weight_stage}")
            print(f"   Weight Answers: {session.weight_answers}")
            print(f"   Weights: {session.weights}")
        else:
            print("✅ Query successful (no sessions found yet)")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        db_session.remove()

if __name__ == "__main__":
    verify_schema()
