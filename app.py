import os
import json
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from database import init_db, create_user, authenticate_user, get_user_by_email, get_user_by_id, add_bookmark, remove_bookmark, is_bookmarked, get_user_bookmarks, save_quiz_score, get_user_quiz_scores, save_chat_message, get_user_chat_history
from functools import wraps

load_dotenv()
client = InferenceClient(api_key=os.getenv('HF_TOKEN'))

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)
app.secret_key = 'vedaroots_secret_key_change_in_production'

# Initialize database
init_db()

# Load plant data
def load_plants():
    with open('plants.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Authentication middleware
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Get current user
def get_current_user():
    if 'user_id' in session:
        return get_user_by_id(session.get('user_id'))
    return None

# ✅ HOME ROUTE (THIS FIXES YOUR 404)
@app.route('/')
def home():
    return render_template('Vedaroot.html')

@app.route('/plants.html')
def plants_page():
    return render_template('plants.html')

@app.route('/chatbot.html')
def chatbot_page():
    return render_template('chatbot.html')

# ✅ AUTHENTICATION ROUTES
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        user_id = create_user(username, email, password, full_name)
        if user_id:
            session['user_id'] = user_id
            session['email'] = email
            session['username'] = username
            flash('Registration successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Username or email already exists', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    
    # Get user data
    bookmarks = get_user_bookmarks(user['id'])
    quiz_scores = get_user_quiz_scores(user['id'])
    chat_history = get_user_chat_history(user['id'], limit=10)
    
    return render_template('profile.html', 
                      user=user, 
                      bookmarks=bookmarks, 
                      quiz_scores=quiz_scores,
                      chat_history=chat_history)

@app.route('/3d-viewer.html')
def viewer_3d():
    return render_template('3d-viewer.html')

@app.route('/3d-gallery.html')
def gallery_3d():
    return render_template('3d-gallery.html')

# ✅ BOOKMARK API
@app.route('/api/bookmark/<int:plant_id>', methods=['POST', 'DELETE'])
@login_required
def bookmark_plant(plant_id):
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        success = add_bookmark(user_id, plant_id)
        return jsonify({'success': success})
    else:  # DELETE
        success = remove_bookmark(user_id, plant_id)
        return jsonify({'success': success})

# ✅ GET ALL PLANTS
@app.route('/api/plants', methods=['GET'])
def get_plants():
    try:
        plants = load_plants()
        # Transform data to match frontend expectations
        transformed_plants = []
        for plant in plants:
            transformed_plant = {
                'id': plant.get('id'),
                'emoji': plant.get('image', '🌿'),
                'name': plant.get('name'),
                'botanical_name': plant.get('botanical_name'),
                'family': plant.get('family'),
                'ayush_system': plant.get('ayush_system'),
                'category': plant.get('therapeutic_category'),
                'plant_type': plant.get('category'),
                'parts_used': plant.get('part_used'),
                'uses': plant.get('uses'),
                'preparation': plant.get('description'),
                'region': plant.get('region'),
                'disease_tags': plant.get('disease_tags', []),
                'common_names': plant.get('name'),
                'model': plant.get('model')
            }
            transformed_plants.append(transformed_plant)
        return jsonify(transformed_plants)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ GET PLANT BY ID
@app.route('/api/plants/<int:plant_id>', methods=['GET'])
def get_plant_by_id(plant_id):
    try:
        plants = load_plants()
        plant = next((p for p in plants if p['id'] == plant_id), None)
        if plant:
            # Transform data to match frontend expectations
            transformed_plant = {
                'id': plant.get('id'),
                'emoji': plant.get('image', '🌿'),
                'name': plant.get('name'),
                'botanical_name': plant.get('botanical_name'),
                'family': plant.get('family'),
                'ayush_system': plant.get('ayush_system'),
                'category': plant.get('therapeutic_category'),
                'plant_type': plant.get('category'),
                'parts_used': plant.get('part_used'),
                'uses': plant.get('uses'),
                'preparation': plant.get('description'),
                'region': plant.get('region'),
                'disease_tags': plant.get('disease_tags', []),
                'common_names': plant.get('name'),
                'model': plant.get('model')
            }
            return jsonify(transformed_plant)
        return jsonify({"error": "Plant not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ SEARCH
@app.route('/api/search', methods=['GET'])
def search_plants():
    query = request.args.get('q', '').lower()

    try:
        plants = load_plants()
        results = [
            p for p in plants
            if query in p.get('name', '').lower() or query in p.get('category', '').lower()
        ]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ CHATBOT
@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        query = request.args.get('q', '')
        if not query:
            return jsonify({"message": "Ask me about herbs 🌿"})
    else:
        data = request.get_json()
        query = data.get('message', '')
        history = data.get('history', [])
    
    if not query:
        return jsonify({"message": "Ask me about herbs 🌿"})

    try:
        # Context extraction: RAG system searching local data
        plants = load_plants()
        q_lower = query.lower()
        relevant_context = ""
        for p in plants:
            # If plant name or any disease tag or category is mentioned in query
            if p.get('name', '').lower() in q_lower or \
               any(tag.lower() in q_lower for tag in p.get('disease_tags', [])) or \
               p.get('therapeutic_category', '').lower() in q_lower:
                relevant_context += f"- {p['name']}: {p['uses']}. Prep: {p['description']}\n"
        
        system_prompt = """You are VedaBot, an expert Ayurvedic AI assistant for VedaRoots - a comprehensive digital encyclopedia of Ayurvedic and medicinal plants. 

Your role is to provide helpful, accurate information about:
- Medicinal plants and their properties
- Ayurvedic remedies and preparations
- Health benefits and uses of herbs
- Safety guidelines and dosage information
- Traditional Ayurvedic knowledge

Guidelines:
- Keep answers conversational but informative
- Use simple, clear language
- Include relevant plant names when applicable
- Mention preparation methods when helpful
- Always include safety disclaimers for medical advice
- Format responses with proper spacing and line breaks
- Use emojis occasionally to make conversations friendly
- Never give definitive medical diagnoses
- Always suggest consulting healthcare professionals for serious conditions

If you have relevant plant data from the database, prioritize that information in your responses."""
        
        if relevant_context:
            system_prompt += f"\n\nRELEVANT PLANT DATA FROM DATABASE:\n{relevant_context}"
        
        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if request.method == 'POST' and history:
            for msg in history[-6:]:  # Last 6 messages for context
                messages.append({"role": msg['role'], "content": msg['content']})
        
        messages.append({"role": "user", "content": query})
            
        response = client.chat_completion(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        return jsonify({"message": reply})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"message": "I'm having trouble connecting to my AI brain right now. Please try again in a moment. 🌿"}), 500

# RUN SERVER
if __name__ == '__main__':
    app.run(debug=True, port=5000)