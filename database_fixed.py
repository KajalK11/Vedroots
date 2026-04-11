import sqlite3
import hashlib
import os
from contextlib import contextmanager

# Database file path
DATABASE_PATH = 'vedaroots.db'

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            profile_picture TEXT DEFAULT 'default.png'
        )
    ''')
    
    # User bookmarks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plant_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, plant_id)
        )
    ''')
    
    # User quiz scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

# User management functions
def create_user(username, email, password, full_name=None):
    """Create a new user"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, hash_password(password), full_name))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def get_user_by_email(email):
    """Get user by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()

def get_user_by_username(username):
    """Get user by username"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def authenticate_user(email, password):
    """Authenticate user credentials"""
    user = get_user_by_email(email)
    if user and verify_password(password, user['password_hash']):
        # Update last login
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
            conn.commit()
        return dict(user)
    return None

# Bookmark functions
def add_bookmark(user_id, plant_id):
    """Add plant to user bookmarks"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user_bookmarks (user_id, plant_id)
                VALUES (?, ?)
            ''', (user_id, plant_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def remove_bookmark(user_id, plant_id):
    """Remove plant from user bookmarks"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM user_bookmarks WHERE user_id = ? AND plant_id = ?
        ''', (user_id, plant_id))
        conn.commit()
        return cursor.rowcount > 0

def get_user_bookmarks(user_id):
    """Get all bookmarks for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.* FROM plants p
            JOIN user_bookmarks ub ON p.id = ub.plant_id
            WHERE ub.user_id = ?
            ORDER BY ub.created_at DESC
        ''', (user_id,))
        return cursor.fetchall()

def is_bookmarked(user_id, plant_id):
    """Check if plant is bookmarked by user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM user_bookmarks 
            WHERE user_id = ? AND plant_id = ?
        ''', (user_id, plant_id))
        return cursor.fetchone() is not None

# Quiz score functions
def save_quiz_score(user_id, score, total_questions):
    """Save quiz score for user"""
    percentage = (score / total_questions) * 100
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_quiz_scores (user_id, score, total_questions, percentage)
            VALUES (?, ?, ?, ?)
        ''', (user_id, score, total_questions, percentage))
        conn.commit()
        return cursor.lastrowid

def get_user_quiz_scores(user_id):
    """Get quiz scores for user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM user_quiz_scores 
            WHERE user_id = ?
            ORDER BY quiz_date DESC
            LIMIT 10
        ''', (user_id,))
        return cursor.fetchall()

# Chat history functions
def save_chat_message(user_id, message, response):
    """Save chat message and response"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_chat_history (user_id, message, response)
            VALUES (?, ?, ?)
        ''', (user_id, message, response))
        conn.commit()
        return cursor.lastrowid

def get_user_chat_history(user_id, limit=50):
    """Get chat history for user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM user_chat_history 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        return cursor.fetchall()

# Initialize database on import
if not os.path.exists(DATABASE_PATH):
    init_db()
