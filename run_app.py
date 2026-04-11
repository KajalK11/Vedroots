import sys
import os

print("Python path:", sys.executable)
print("Current directory:", os.getcwd())
print("Python version:", sys.version)

try:
    sys.path.insert(0, os.getcwd())
    print("Testing basic imports...")
    
    import flask
    print("Flask imported successfully")
    
    from database import init_db
    print("Database module imported successfully")
    
    init_db()
    print("Database initialized successfully")
    
    from app import app
    print("App imported successfully")
    
    print("\nStarting Flask server...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
