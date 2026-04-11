#!/usr/bin/env python3

print("=== VedaRoots Application Diagnostic ===")
print()

# Test 1: Check Python imports
print("1. Testing Python imports...")
try:
    import flask
    print("   Flask: OK")
except ImportError as e:
    print(f"   Flask: ERROR - {e}")

try:
    import sqlite3
    print("   SQLite: OK")
except ImportError as e:
    print(f"   SQLite: ERROR - {e}")

try:
    from flask_cors import CORS
    print("   Flask-CORS: OK")
except ImportError as e:
    print(f"   Flask-CORS: ERROR - {e}")

try:
    from dotenv import load_dotenv
    print("   python-dotenv: OK")
except ImportError as e:
    print(f"   python-dotenv: ERROR - {e}")

try:
    from huggingface_hub import InferenceClient
    print("   huggingface_hub: OK")
except ImportError as e:
    print(f"   huggingface_hub: ERROR - {e}")

print()

# Test 2: Check database
print("2. Testing database...")
try:
    from database import init_db, get_user_by_id
    print("   Database module: OK")
    init_db()
    print("   Database initialization: OK")
except Exception as e:
    print(f"   Database: ERROR - {e}")

print()

# Test 3: Check app import
print("3. Testing Flask app...")
try:
    from app import app
    print("   App import: OK")
    print(f"   App name: {app.name}")
    print(f"   Debug mode: {app.debug}")
except Exception as e:
    print(f"   App import: ERROR - {e}")

print()

# Test 4: Check files
print("4. Checking required files...")
import os

files_to_check = [
    'app.py',
    'database.py', 
    'plants.json',
    'templates/Vedaroot.html',
    'templates/plants.html',
    'templates/login.html',
    'templates/register.html',
    'templates/profile.html'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"   {file_path}: OK")
    else:
        print(f"   {file_path}: MISSING")

print()

# Test 5: Check environment
print("5. Testing environment...")
try:
    load_dotenv()
    hf_token = os.getenv('HF_TOKEN')
    if hf_token:
        print("   HuggingFace token: OK")
    else:
        print("   HuggingFace token: MISSING")
except Exception as e:
    print(f"   Environment: ERROR - {e}")

print()
print("=== Diagnostic Complete ===")
print("If all tests show OK, try running: python app.py")
print("If there are errors, install missing dependencies with:")
print("pip install -r requirements.txt")
