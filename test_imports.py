#!/usr/bin/env python3

print("Testing database imports...")

try:
    from database import get_user_by_id, get_user_by_email, init_db
    print("SUCCESS: All database functions imported correctly")
    
    # Test database initialization
    init_db()
    print("SUCCESS: Database initialized")
    
    # Test app import
    from app import app
    print("SUCCESS: Flask app imported")
    
    print("\n=== All tests passed! ===")
    print("You can now run: python app.py")
    print("Then open: http://127.0.0.1:5000")
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")
    import traceback
    traceback.print_exc()
