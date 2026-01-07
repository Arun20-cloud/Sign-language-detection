"""
Flask Hand Sign Detector - Local Development Server
====================================================
For local development: python app.py
For Vercel deployment: uses api/index.py

QUICK START:
1. pip install -r requirements.txt
2. python app.py
3. Open http://localhost:5000
4. Register/Login to access the app

FEATURES:
- User authentication with sessions
- Separate Train and Detect modes
- Real-time hand detection via webcam (browser)
- Record and label gesture samples
- KNN classifier (configurable K value)
- Export/import datasets as JSON
- localStorage for sample persistence per user

ARCHITECTURE:
- All hand detection runs client-side (MediaPipe CDN)
- Flask serves HTML with session management
- No backend processing needed (lightweight deployment)
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from datetime import datetime
import os
import secrets
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

MIN_API_INTERVAL = 15  # Minimum 15 seconds between API calls per user
LAST_API_CALL = {}  # Track last API call time per user session

AI_CACHE_DURATION = 10  # Cache results for 10 seconds
AI_CACHE = {}  # Cache AI detection results

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Print debug info on startup
print("=" * 50)
print("ENVIRONMENT VARIABLES CHECK:")
print(f"SUPABASE_URL: {'✓ Set' if SUPABASE_URL else '✗ NOT SET'}")
print(f"SUPABASE_SERVICE_KEY: {'✓ Set' if SUPABASE_SERVICE_KEY else '✗ NOT SET'}")
print(f"SECRET_KEY: {'✓ Set' if os.environ.get('SECRET_KEY') else '✗ Using default'}")
if SUPABASE_URL:
    print(f"Supabase URL: {SUPABASE_URL[:30]}...")
print("=" * 50)

def supabase_query(table, method='GET', filters=None, data=None):
    """Make direct HTTP request to Supabase REST API"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise Exception("Supabase credentials not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # ⭐ Apply filters ONLY when NOT inserting
    if filters and method != 'POST':
        params = []
        for key, value in filters.items():
            params.append(f"{key}=eq.{value}")
        url = f"{url}?{'&'.join(params)}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)

        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)

        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=10)

        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)

        response.raise_for_status()
        return response.json() if response.text else []

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Supabase HTTP request failed: {str(e)}")
        raise


# ===== AUTHENTICATION HELPERS =====
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        try:
            users = supabase_query('users', filters={'id': session['user_id']})
            if users and len(users) > 0:
                return users[0]
        except Exception as e:
            print(f"[ERROR] Failed to get current user: {str(e)}")
    return None


# ===== ROUTES =====
@app.route('/')
def index():
    """Root - show landing page or redirect to menu if logged in"""
    if 'user_id' in session:
        return redirect(url_for('menu'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        print(f"[DEBUG] Login attempt for username: {username}")

        if not username or not password:
            return render_template('login.html', error='Username and password required')

        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            return render_template('login.html', error='Database not configured. Please contact administrator.')

        try:
            users = supabase_query('users', filters={'username': username})
            
            if not users or len(users) == 0:
                print(f"[ERROR] User {username} not found in database")
                return render_template('login.html', error='User not found. Please register first.')
            
            user = users[0]
            
            # Verify password
            if user['password'] == password:
                session['user_id'] = str(user['id'])
                session['username'] = username
                print(f"[INFO] User {username} logged in successfully")
                return redirect(url_for('menu'))
            else:
                print(f"[ERROR] Invalid password for user {username}")
                return render_template('login.html', error='Invalid credentials')
        
        except Exception as e:
            print(f"[ERROR] Database error during login: {str(e)}")
            import traceback
            traceback.print_exc()
            return render_template('login.html', error='Login failed. Please try again.')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        print(f"[DEBUG] Registration attempt for username: {username}")

        if not username or not password:
            return render_template('register.html', error='Username and password required')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            return render_template('register.html', error='Server configuration error: Database not configured. Please contact administrator.')

        try:
            existing_users = supabase_query('users', filters={'username': username})
            
            if existing_users and len(existing_users) > 0:
                print(f"[ERROR] Username {username} already exists")
                return render_template('register.html', error='Username already exists')
            
            new_user_data = {
                'username': username,
                'password': password
            }
            new_users = supabase_query('users', method='POST', data=new_user_data)
            
            if not new_users or len(new_users) == 0:
                raise Exception("User creation returned no data")
            
            print(f"[SUCCESS] New user registered: {username} with ID: {new_users[0].get('id')}")
            return redirect(url_for('login'))
        
        except Exception as e:
            error_message = str(e)
            print(f"[ERROR] Registration failed: {error_message}")
            import traceback
            traceback.print_exc()
            return render_template('register.html', error=f'Registration failed: {error_message}')

    return render_template('register.html')


@app.route('/menu')
@login_required
def menu():
    """Main menu - choose detect or train"""
    username = session.get('username')
    return render_template('menu.html', username=username)


@app.route('/detect')
@login_required
def detect():
    """Hand sign detection page"""
    username = session.get('username')
    return render_template('detect.html', username=username)


@app.route('/train')
@login_required
def train():
    """Hand sign training/recording page"""
    username = session.get('username')
    return render_template('train.html', username=username)


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))


# ===== API ENDPOINTS =====
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "hand-sign-detector"})


@app.route('/api/stats', methods=['GET'])
def stats():
    """Return app statistics"""
    user = get_current_user()
    total_users = 0
    try:
        users = supabase_query('users')
        total_users = len(users) if users else 0
    except Exception as e:
        print(f"[ERROR] Failed to get user count: {str(e)}")
    
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "user": session.get('username'),
        "authenticated": 'user_id' in session,
        "total_users": total_users
    })


@app.route('/api/detect-vision', methods=['POST'])
@login_required
def detect_vision():
    """Use AI vision model to detect hand signs with rate limiting"""
    try:
        username = session.get('username')
        user_id = session.get('user_id')
        data = request.json
        image_data = data.get('image')
        
        current_time = time.time()
        if user_id in LAST_API_CALL:
            time_since_last_call = current_time - LAST_API_CALL[user_id]
            if time_since_last_call < MIN_API_INTERVAL:
                wait_time = int(MIN_API_INTERVAL - time_since_last_call)
                print(f"[AI-DETECT] RATE LIMITED: User {username} must wait {wait_time} more seconds")
                return jsonify({
                    "error": "rate_limit",
                    "message": f"Please wait {wait_time} seconds before detecting again",
                    "wait_seconds": wait_time,
                    "label": f"Rate limit: wait {wait_time}s",
                    "confidence": 0
                }), 429
        
        LAST_API_CALL[user_id] = current_time
        
        api_key = os.environ.get('AI_API_KEY')
        provider = os.environ.get('AI_PROVIDER', 'openai').lower()
        
        print(f"[AI-DETECT] ========== START ==========")
        print(f"[AI-DETECT] User: {username}")
        print(f"[AI-DETECT] Provider: {provider}")
        print(f"[AI-DETECT] API Key configured: {'YES' if api_key else 'NO'}")
        print(f"[AI-DETECT] Image received: {'YES' if image_data else 'NO'}")
        
        if not image_data:
            print("[AI-DETECT] ERROR: No image data in request")
            return jsonify({"label": "error: no image data", "confidence": 0}), 400
            
        if not api_key:
            print("[AI-DETECT] ERROR: API key not configured")
            return jsonify({"label": "error: api key missing", "confidence": 0}), 500
        
        # Strip data URL prefix if present
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
            print(f"[AI-DETECT] Stripped base64 prefix")
        
        print(f"[AI-DETECT] Image size: {len(image_data)} characters")
        print(f"[AI-DETECT] Calling AI provider: {provider}")
        
        # Call appropriate AI provider
        if provider == 'openai' or provider == 'gpt':
            result = call_openai_vision(image_data, api_key)
        elif provider == 'anthropic' or provider == 'claude':
            result = call_anthropic_vision(image_data, api_key)
        elif provider == 'groq':
            result = call_groq_vision(image_data, api_key)
        else:
            print(f"[AI-DETECT] ERROR: Unknown provider '{provider}'")
            return jsonify({"label": f"error: unknown provider {provider}", "confidence": 0}), 400
        
        print(f"[AI-DETECT] SUCCESS: {result}")
        print(f"[AI-DETECT] ========== END ==========")
        return jsonify(result)
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"[AI-DETECT] OpenAI rate limit hit for user {username}")
            return jsonify({
                "error": "rate_limit",
                "message": "Rate limit exceeded - too many requests",
                "provider": provider,
                "label": "Rate limit exceeded",
                "confidence": 0
            }), 429
        
        error_msg = str(e)
        print(f"[AI-DETECT] HTTP Error: {error_msg}")
        return jsonify({
            "label": f"API error: {error_msg[:50]}",
            "confidence": 0
        }), 500
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"[AI-DETECT] ========== EXCEPTION ==========")
        print(f"[AI-DETECT] Type: {error_type}")
        print(f"[AI-DETECT] Message: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Return user-friendly error
        return jsonify({
            "label": f"error: {error_msg[:100]}",
            "confidence": 0
        }), 500


@app.route('/api/test-ai', methods=['GET'])
@login_required
def test_ai():
    """Test AI API connection"""
    try:
        api_key = os.environ.get('AI_API_KEY')
        provider = os.environ.get('AI_PROVIDER', 'openai').lower()
        
        if not api_key:
            return jsonify({
                "success": False,
                "error": "AI_API_KEY environment variable not set",
                "provider": provider
            })
        
        # Test with a simple text prompt (no image)
        if provider == 'openai' or provider == 'gpt':
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say 'hello'"}],
                "max_tokens": 10
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 401:
                return jsonify({
                    "success": False,
                    "error": "Invalid API key - 401 Unauthorized",
                    "provider": provider,
                    "status_code": 401
                })
            
            if response.status_code == 429:
                return jsonify({
                    "success": False,
                    "error": "Rate limit exceeded - too many requests",
                    "provider": provider,
                    "status_code": 429
                })
            
            if not response.ok:
                return jsonify({
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "provider": provider,
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
            
            result = response.json()
            message = result['choices'][0]['message']['content']
            
            return jsonify({
                "success": True,
                "provider": provider,
                "message": "AI API is working!",
                "test_response": message
            })
        
        else:
            return jsonify({
                "success": False,
                "error": f"Provider '{provider}' test not implemented",
                "provider": provider
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "provider": provider if 'provider' in locals() else 'unknown'
        })


def call_openai_vision(image_base64, api_key):
    """Call OpenAI GPT-4 Vision with simplified prompt"""
    print("[AI-DETECT] >>> OpenAI API call starting...")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-mini",  # Using mini for faster/cheaper responses
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What hand gesture is shown in this image? Reply with ONE word only: thumbs-up, peace, okay, pointing, fist, open-palm, wave, or none."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "low"  # Using low detail for faster processing
                        }
                    }
                ]
            }
        ],
        "max_tokens": 20,
        "temperature": 0
    }
    
    try:
        print("[AI-DETECT] >>> Sending request to OpenAI...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"[AI-DETECT] >>> Response status: {response.status_code}")
        
        if not response.ok:
            error_text = response.text
            print(f"[AI-DETECT] >>> ERROR response: {error_text}")
            response.raise_for_status()
        
        result = response.json()
        label = result['choices'][0]['message']['content'].strip().lower()
        
        print(f"[AI-DETECT] >>> OpenAI detected: '{label}'")
        
        return {
            "label": label,
            "confidence": 0.90,
            "provider": "openai"
        }
    except Exception as e:
        print(f"[AI-DETECT] >>> OpenAI failed: {str(e)}")
        raise


def call_anthropic_vision(image_base64, api_key):
    """Call Anthropic Claude Vision API"""
    import requests
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 50,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "Identify the hand sign or gesture. Respond ONLY with the gesture name in lowercase (e.g., 'thumbs-up', 'peace'). If no hand sign is visible, say 'none'."
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    label = result['content'][0]['text'].strip().lower()
    
    return {
        "label": label,
        "confidence": 0.95,
        "provider": "anthropic"
    }


def call_groq_vision(image_base64, api_key):
    """Call Groq Vision API"""
    import requests
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "llama-3.2-90b-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Identify the hand sign. Respond ONLY with the gesture name in lowercase. If no hand is visible, say 'none'."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 50
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    label = result['choices'][0]['message']['content'].strip().lower()
    
    return {
        "label": label,
        "confidence": 0.95,
        "provider": "groq"
    }


@app.route('/api/training-data/save', methods=['POST'])
@login_required
def save_training_data():
    """Save training data to Supabase"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        data = request.json
        samples = data.get('samples', [])
        
        if not samples:
            return jsonify({"error": "No samples provided"}), 400
        
        print(f"[TRAINING-SAVE] Saving {len(samples)} samples for user {username}")
        
        # Delete existing training data for this user
        try:
            supabase_query('training_data', method='DELETE', filters={'user_id': user_id})
            print(f"[TRAINING-SAVE] Cleared existing data for user {username}")
        except Exception as e:
            print(f"[TRAINING-SAVE] Warning: Could not clear existing data: {str(e)}")
        
        # Insert new samples
        saved_count = 0
        for sample in samples:
            try:
                sample_data = {
                    'user_id': user_id,
                    'username': username,
                    'label': sample.get('label'),
                    'landmarks': sample.get('landmarks')
                }
                supabase_query('training_data', method='POST', data=sample_data)
                saved_count += 1
            except Exception as e:
                print(f"[TRAINING-SAVE] Error saving sample: {str(e)}")
                continue
        
        print(f"[TRAINING-SAVE] Successfully saved {saved_count}/{len(samples)} samples")
        return jsonify({
            "success": True,
            "saved": saved_count,
            "total": len(samples)
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"[TRAINING-SAVE] Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500


@app.route('/api/training-data/load', methods=['GET'])
@login_required
def load_training_data():
    """Load training data from Supabase"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        
        print(f"[TRAINING-LOAD] Loading data for user {username}")
        
        # Get all training data for this user
        rows = supabase_query('training_data', filters={'user_id': user_id})
        
        if not rows:
            print(f"[TRAINING-LOAD] No training data found for user {username}")
            return jsonify({"samples": []})
        
        # Convert to format expected by frontend
        samples = []
        for row in rows:
            samples.append({
                'label': row.get('label'),
                'landmarks': row.get('landmarks')
            })
        
        print(f"[TRAINING-LOAD] Loaded {len(samples)} samples for user {username}")
        return jsonify({"samples": samples})
    
    except Exception as e:
        error_msg = str(e)
        print(f"[TRAINING-LOAD] Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500


@app.route('/api/training-data/delete-label', methods=['POST'])
@login_required
def delete_training_label():
    """Delete all samples of a specific label from Supabase"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        data = request.json
        label = data.get('label')
        
        if not label:
            return jsonify({"error": "No label provided"}), 400
        
        print(f"[TRAINING-DELETE] Deleting label '{label}' for user {username}")
        
        # First, get count of samples to be deleted
        rows = supabase_query('training_data', filters={'user_id': user_id})
        count = len([r for r in rows if r.get('label') == label])
        
        # Delete using direct SQL through Supabase REST API with multiple filters
        url = f"{SUPABASE_URL}/rest/v1/training_data?user_id=eq.{user_id}&label=eq.{label}"
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.delete(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"[TRAINING-DELETE] Deleted {count} samples of label '{label}'")
        return jsonify({
            "success": True,
            "deleted": count,
            "label": label
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"[TRAINING-DELETE] Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500


@app.route('/api/training-data/clear', methods=['POST'])
@login_required
def clear_training_data():
    """Clear all training data for current user from Supabase"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        
        print(f"[TRAINING-CLEAR] Clearing all data for user {username}")
        
        # Get count before deletion
        rows = supabase_query('training_data', filters={'user_id': user_id})
        count = len(rows) if rows else 0
        
        # Delete all training data for this user
        supabase_query('training_data', method='DELETE', filters={'user_id': user_id})
        
        print(f"[TRAINING-CLEAR] Cleared {count} samples")
        return jsonify({
            "success": True,
            "deleted": count
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"[TRAINING-CLEAR] Error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║  Hand Sign Detector Server                                ║
║  Running on http://localhost:{port}                        ║
║                                                           ║
║  Features:                                                ║
║  - User Authentication                                    ║
║  - Train Mode (Record Gestures)                          ║
║  - Detect Mode (Recognize Gestures)                      ║
║                                                           ║
║  Press Ctrl+C to stop                                     ║
╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
