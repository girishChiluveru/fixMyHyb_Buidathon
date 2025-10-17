import os
import json
import sqlite3
import time
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template, render_template_string, redirect, url_for, flash, session
from PIL import Image, ExifTags
from dotenv import load_dotenv
import google.generativeai as genai


# ==================== 1. INITIALIZATION & CONFIG ====================

load_dotenv()
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

COMPLAINT_CATEGORIES = [
    "Open Garbage Dump", "Sewage Leak/Overflow", "Pothole/Damaged Road",
    "Damaged Electrical Infrastructure", "Fallen Tree", "Water Logging",
    "Stray Animals", "Other"
]

def check_api_keys():
    """Check if API keys are properly configured"""
    print("\n" + "="*60)
    print("API KEY CONFIGURATION CHECK")
    print("="*60)
    
    keys = {
        'GOOGLE_API_KEY_IMAGE': os.getenv('GOOGLE_API_KEY_IMAGE'),
        'GOOGLE_API_KEY_AUDIO': os.getenv('GOOGLE_API_KEY_AUDIO'),
        'GOOGLE_API_KEY_TEXT': os.getenv('GOOGLE_API_KEY_TEXT'),
        'GOOGLE_API_KEY_REPORT': os.getenv('GOOGLE_API_KEY_REPORT')
    }
    
    all_set = True
    for key_name, key_value in keys.items():
        if key_value and len(key_value) > 10:
            print(f"✅ {key_name}: Set (length: {len(key_value)})")
        else:
            print(f"❌ {key_name}: NOT SET or INVALID")
            all_set = False
    
    print("="*60)
    if not all_set:
        print("⚠️  WARNING: Some API keys are missing!")
        print("AI features will return placeholder data.")
        print("Please set your Google API keys in .env file")
    else:
        print("✅ All API keys configured")
    print("="*60 + "\n")
    
    return all_set

check_api_keys()

# ==================== 2. DATABASE SETUP ====================

def get_db_connection():
    """Establishes SQLite connection and sets row_factory to sqlite3.Row for dictionary access."""
    conn = sqlite3.connect('fixmyhyd.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initializes all required SQLite tables and creates the default admin user."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ghmc_id TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT,
            zone TEXT,
            gps_lat REAL,
            gps_lng REAL,
            status TEXT DEFAULT 'Submitted',
            submitted_by TEXT DEFAULT 'Citizen',
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER,
            old_status TEXT,
            new_status TEXT,
            changed_by TEXT,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (complaint_id) REFERENCES complaints (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin if none exists (admin/admin123)
    c.execute('SELECT COUNT(*) FROM admins')
    if c.fetchone()[0] == 0:
        admin_password = hash_password('admin123')
        c.execute('''
            INSERT INTO admins (username, password_hash, name)
            VALUES (?, ?, ?)
        ''', ('admin', admin_password, 'System Administrator'))
    
    conn.commit()
    conn.close()

# ==================== 3. AI HELPER FUNCTIONS (PLACEHOLDERS) ====================
# NOTE: Actual Gemini API integration logic is complex and requires proper API keys.
# These functions are placeholders to ensure the app logic can proceed.
def analyze_image_with_gemini(image_stream, max_retries=3):
    try:
        api_key = os.getenv("GOOGLE_API_KEY_IMAGE")
        if not api_key: 
            print("❌ ERROR: GOOGLE_API_KEY_IMAGE is not set!")
            raise ValueError("GOOGLE_API_KEY_IMAGE is not set!")
        
        print(f"📸 Calling Gemini Image API (key length: {len(api_key)})")
        genai.configure(api_key=api_key)
        
        image_bytes = image_stream.read()
        print(f"📸 Image size: {len(image_bytes)} bytes")
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        prompt = f"""
        Analyze the image of a civic issue in Hyderabad, India. Provide a response in a valid JSON object with two keys:
        1. "summary": A brief, one-sentence summary of the scene.
        2. "category": Classify the issue into one of these exact categories: {', '.join(COMPLAINT_CATEGORIES)}.
        """
        
        # Use gemini-1.5-flash for better rate limits
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Retry logic for quota errors
        for attempt in range(max_retries):
            try:
                print(f"📸 Attempt {attempt + 1}/{max_retries}...")
                response = model.generate_content([prompt, image_part])
                response_text = response.text.strip().replace("```json", "").replace("```", "")
                print(f"📸 API Response: {response_text[:200]}...")
                result = json.loads(response_text)
                print(f"✅ Image analysis successful: {result}")
                return result
            except Exception as e:
                error_str = str(e)
                print(f"❌ Image API error (attempt {attempt + 1}): {error_str}")
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2 + 7
                        print(f"⏳ Quota exceeded, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                raise e
                
    except Exception as e:
        print(f"❌ FATAL ERROR in analyze_image_with_gemini: {e}")
        import traceback
        traceback.print_exc()
        return None


def transcribe_audio_with_gemini(audio_file, max_retries=3):
    try:
        api_key = os.getenv("GOOGLE_API_KEY_AUDIO")
        if not api_key: 
            print("❌ ERROR: GOOGLE_API_KEY_AUDIO is not set!")
            raise ValueError("GOOGLE_API_KEY_AUDIO is not set!")
        
        print(f"🎤 Calling Gemini Audio API")
        genai.configure(api_key=api_key)

        prompt = """
        You are an audio transcription service for GHMC. Transcribe the following audio complaint.
        Return ONLY the transcribed text.
        """
        
        for attempt in range(max_retries):
            try:
                print(f"🎤 Uploading audio file: {audio_file}")
                uploaded_file = genai.upload_file(path=audio_file, display_name="user_complaint_audio")
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                response = model.generate_content([prompt, uploaded_file])
                genai.delete_file(uploaded_file.name)
                print(f"✅ Audio transcription successful")
                return {"transcription": response.text}
            except Exception as e:
                error_str = str(e)
                print(f"❌ Audio API error (attempt {attempt + 1}): {error_str}")
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2 + 7
                        print(f"⏳ Quota exceeded, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                raise e
                
    except Exception as e:
        print(f"❌ FATAL ERROR in transcribe_audio_with_gemini: {e}")
        import traceback
        traceback.print_exc()
        return {"transcription": "Demonstration fallback: Could not process audio file via API."}


def analyze_text_with_gemini(description, max_retries=3):
    try:
        api_key = os.getenv("GOOGLE_API_KEY_TEXT")
        if not api_key: 
            print("❌ ERROR: GOOGLE_API_KEY_TEXT is not set!")
            raise ValueError("GOOGLE_API_KEY_TEXT is not set!")
        
        print(f"📝 Calling Gemini Text API for description: {description[:100]}...")
        genai.configure(api_key=api_key)

        prompt = f"""
        Analyze the following user-submitted civic complaint. Provide a response in a valid JSON object with four keys:
        1. "category": Classify the issue into one of these exact categories: {', '.join(COMPLAINT_CATEGORIES)}.
        2. "priority": Assess the priority as 'Low', 'Medium', or 'High'.
        3. "summary": Create a succinct, one-sentence summary of the core problem.
        4. "actionable_steps": Suggest 2-3 brief, actionable steps.
        Complaint: "{description}"
        """
        
        for attempt in range(max_retries):
            try:
                print(f"📝 Attempt {attempt + 1}/{max_retries}...")
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                response = model.generate_content(prompt)
                response_text = response.text.strip().replace("```json", "").replace("```", "")
                print(f"📝 API Response: {response_text[:200]}...")
                result = json.loads(response_text)
                print(f"✅ Text analysis successful: {result}")
                return result
            except Exception as e:
                error_str = str(e)
                print(f"❌ Text API error (attempt {attempt + 1}): {error_str}")
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2 + 7
                        print(f"⏳ Quota exceeded, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                raise e
                
    except Exception as e:
        print(f"❌ FATAL ERROR in analyze_text_with_gemini: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_formal_report_with_gemini(data, max_retries=3):
    try:
        api_key = os.getenv("GOOGLE_API_KEY_REPORT")
        if not api_key: 
            print("❌ ERROR: GOOGLE_API_KEY_REPORT is not set!")
            raise ValueError("GOOGLE_API_KEY_REPORT is not set!")
        
        print(f"📋 Calling Gemini Report Generation API")
        print(f"📋 Input data: {json.dumps(data, indent=2)}")
        genai.configure(api_key=api_key)

        prompt = f"""
        You are an AI assistant for the GHMC. Synthesize the provided information into a structured, formal complaint.
        The final output must be a single, valid JSON object with the keys: "subject", "description", and "zone".
        Contextual Information:
        - Image Analysis: {data.get('image_analysis')}
        - Voice Transcription: {data.get('voice_transcription')}
        - Text Analysis: {data.get('text_analysis')}
        - Location Text: {data.get('location_text', 'Not provided')}
        """
        
        for attempt in range(max_retries):
            try:
                print(f"📋 Attempt {attempt + 1}/{max_retries}...")
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                response = model.generate_content(prompt)
                response_text = response.text.strip().replace("```json", "").replace("```", "")
                print(f"📋 API Response: {response_text[:200]}...")
                result = json.loads(response_text)
                print(f"✅ Report generation successful: {result}")
                return result
            except Exception as e:
                error_str = str(e)
                print(f"❌ Report API error (attempt {attempt + 1}): {error_str}")
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2 + 7
                        print(f"⏳ Quota exceeded, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                raise e
                
    except Exception as e:
        print(f"❌ FATAL ERROR in generate_formal_report_with_gemini: {e}")
        import traceback
        traceback.print_exc()
        return None

import os
import time
import google.generativeai as genai
import traceback

# Add this new import at the top of app.py
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable

# Replace your reverse_geocode_coordinates function with this one
def reverse_geocode_coordinates(latitude, longitude):
    """
    Converts GPS coordinates to a human-readable address using OpenStreetMap's Nominatim service.
    """
    if latitude is None or longitude is None:
        return "Location not available"

    try:
        # The user_agent is important for Nominatim's usage policy
        geolocator = Nominatim(user_agent="fixmyhyd_app")
        
        # Make the API call
        location = geolocator.reverse((latitude, longitude), exactly_one=True, timeout=10)

        # Check if we got a result and return the address
        if location:
            address = location.address
            print(f"🌍 Nominatim (OSM) Geocoding successful: {address}")
            return address
        else:
            return "Could not determine address from coordinates via Nominatim."
            
    except GeocoderUnavailable as e:
        print(f"❌ Nominatim service is unavailable: {e}")
        return f"Geocoding service is temporarily down. Lat/Lng: ({latitude:.4f}, {longitude:.4f})"
        
    except Exception as e:
        print(f"❌ FATAL ERROR in reverse_geocode_coordinates (Nominatim): {e}")
        return f"Geocoding failed due to an error. Lat/Lng: ({latitude:.4f}, {longitude:.4f})"
    
    
# ==================== 4. AUTHENTICATION FUNCTIONS ====================

def hash_password(password):
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, stored_hash):
    """Verify a password against its hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'admin_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('home')) 
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== 5. UTILITY FUNCTIONS (INCLUDING TIMESTAMP PARSING) ====================

def get_gps_coordinates(image_stream):
    # This function is now unused as device GPS is primary.
    return {"latitude": None, "longitude": None} 

def parse_timestamp(timestamp_str):
    """Convert string timestamp (from SQLite) to datetime object"""
    if isinstance(timestamp_str, datetime):
        return timestamp_str
    if timestamp_str is None:
        return None
    try:
        # Try parsing ISO format
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        try:
            # Try common SQLite format
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

# Add Jinja2 template filters for safe timestamp formatting
@app.template_filter('format_date')
def format_date(timestamp):
    """Format timestamp for display (Date only)"""
    if isinstance(timestamp, str):
        timestamp = parse_timestamp(timestamp)
    if timestamp is None:
        return 'N/A'
    return timestamp.strftime('%d %b %Y')

@app.template_filter('format_datetime')
def format_datetime(timestamp):
    """Format timestamp with time for display"""
    if isinstance(timestamp, str):
        timestamp = parse_timestamp(timestamp)
    if timestamp is None:
        return 'N/A'
    return timestamp.strftime('%d %b %Y %I:%M %p')


# ==================== 6. WEB ROUTES (Logical Errors Fixed & Timestamp Parsing Applied) ====================

@app.route('/')
def home():
    conn = get_db_connection()

    # Complaints stats
    total_complaints = conn.execute('SELECT COUNT(*) FROM complaints').fetchone()[0]
    pending_complaints = conn.execute(
        'SELECT COUNT(*) FROM complaints WHERE status IN ("Submitted", "In Progress")'
    ).fetchone()[0]
    resolved_complaints = conn.execute(
        'SELECT COUNT(*) FROM complaints WHERE status = "Resolved"'
    ).fetchone()[0]

    resolution_rate = round((resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0)

    # Average days to resolve
    avg_days = conn.execute(
        'SELECT AVG(julianday(updated_at) - julianday(created_at)) FROM complaints WHERE status="Resolved"'
    ).fetchone()[0] or 0
    avg_days = round(avg_days, 1)

    # Total citizens/users served
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]

    conn.close()

    admin_stats = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'resolution_rate': resolution_rate,
        'avg_days': avg_days,
        'total_users': total_users
    }

    return render_template('home.html', admin_stats=admin_stats)

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    # Fix: Redirect already logged-in users
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('user_login.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('user_login.html')

@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        if not all([name, email, password]):
            flash('Please fill in all required fields.', 'error')
            return render_template('user_register.html')
        
        conn = get_db_connection()
        try:
            # Check if user already exists
            existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if existing_user:
                flash('Email already registered.', 'error')
                return render_template('user_register.html')
            
            # Create new user
            password_hash = hash_password(password)
            conn.execute('''
                INSERT INTO users (name, email, password_hash, phone)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password_hash, phone))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user_login'))
        except sqlite3.Error as e:
            flash('Registration failed. Please try again.', 'error')
        finally:
            conn.close()
    
    return render_template('user_register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Fix: Redirect already logged-in admins
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('admin_login.html')
        
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if admin and verify_password(password, admin['password_hash']):
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['name']
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin_login.html')

@app.route('/user/dashboard')
@user_required
def user_dashboard():
    conn = get_db_connection()
    
    # Get user's complaints
    complaints_raw = conn.execute('''
        SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC LIMIT 10
    ''', (session['user_id'],)).fetchall()
    
    # Convert to dicts and parse timestamps (REQUIRED for SQLite TIMESTAMP columns in Jinja2)
    user_complaints = []
    for complaint in complaints_raw:
        complaint_dict = dict(complaint)
        complaint_dict['created_at'] = parse_timestamp(complaint_dict['created_at'])
        complaint_dict['updated_at'] = parse_timestamp(complaint_dict['updated_at'])
        user_complaints.append(complaint_dict)
    
    # Get user stats
    total_complaints = conn.execute('SELECT COUNT(*) FROM complaints WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    pending_complaints = conn.execute('SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status IN ("Submitted", "In Progress")', (session['user_id'],)).fetchone()[0]
    resolved_complaints = conn.execute('SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status = "Resolved"', (session['user_id'],)).fetchone()[0]
    resolution_rate = round((resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0)
    
    conn.close()
    
    user_stats = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'resolution_rate': resolution_rate
    }
    
    return render_template('user_dashboard.html', 
                         user_complaints=user_complaints, 
                         user_stats=user_stats)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    
    # Get all complaints
    complaints_raw = conn.execute('SELECT * FROM complaints ORDER BY created_at DESC').fetchall()
    
    # Convert to dicts and parse timestamps (REQUIRED for SQLite TIMESTAMP columns in Jinja2)
    all_complaints = []
    for complaint in complaints_raw:
        complaint_dict = dict(complaint)
        complaint_dict['created_at'] = parse_timestamp(complaint_dict['created_at'])
        complaint_dict['updated_at'] = parse_timestamp(complaint_dict['updated_at'])
        all_complaints.append(complaint_dict)
    
    # Get admin stats
    total_complaints = conn.execute('SELECT COUNT(*) FROM complaints').fetchone()[0]
    pending_complaints = conn.execute('SELECT COUNT(*) FROM complaints WHERE status IN ("Submitted", "In Progress")').fetchone()[0]
    resolved_complaints = conn.execute('SELECT COUNT(*) FROM complaints WHERE status = "Resolved"').fetchone()[0]
    resolution_rate = round((resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0)
    
    conn.close()
    
    admin_stats = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'resolution_rate': resolution_rate
    }
    
    return render_template('admin_dashboard.html', 
                         all_complaints=all_complaints, 
                         admin_stats=admin_stats)

@app.route('/report-issue')
@user_required
def report_issue():
    return render_template('report_issue.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# ==================== 7. API ROUTES ====================

@app.route('/api/report-issue', methods=['POST'])
@user_required
def report_issue_endpoint():
    print("-" * 50)
    print("START: Processing New Complaint Report")
    print("-" * 50)

    if 'image' not in request.files:
        print("ERROR: Image file is missing.")
        return jsonify({"error": "Validation failed: An image file is mandatory."}), 400
    
    image_file = request.files['image']
    audio_file = request.files.get('audio')
    text_description = request.form.get('description')
    
    # Location data from form
    manual_address = request.form.get('location_text')
    device_lat = request.form.get('device_latitude')
    device_lng = request.form.get('device_longitude')

    print(f"User Input - Text: {text_description[:50]}...")
    print(f"User Input - Device GPS: Lat={device_lat}, Lng={device_lng}")
    print(f"User Input - Manual Address: {manual_address}")

    if not text_description and not audio_file:
        print("ERROR: Text or voice description is missing.")
        return jsonify({"error": "Validation failed: Either a text or voice description is mandatory."}), 400

    # 1. Location Extraction
    
    final_lat = None
    final_lng = None
    final_location_string = None
    
    # Priority: 1. Device GPS (if present), 2. Manual Address
    if device_lat and device_lng:
        final_lat = float(device_lat)
        final_lng = float(device_lng)
        print("-> Using DEVICE GPS for coordinates (Primary Source).")
    elif manual_address:
        final_location_string = manual_address
        print("-> Using MANUAL ADDRESS string (Fallback Source).")
    else:
        # If no GPS and no manual address provided, fail.
        print("ERROR: No location data found (GPS or manual).")
        return jsonify({"status": "error", "error": "Location data is required but was not provided."}), 400


    if final_lat and final_lng:
        # Convert coordinates to a full address string
        final_location_string = reverse_geocode_coordinates(final_lat, final_lng)

    gps_coords = {'latitude': final_lat, 'longitude': final_lng}
    print(f"STAGE 1: Final GPS Coords: {gps_coords}")
    print(f"STAGE 1: Final Address: {final_location_string}")
    
    # 2. Image Analysis
    image_analysis = analyze_image_with_gemini(image_file.stream)
    print(f"STAGE 2: Image Analysis Result: {image_analysis}")
    if not image_analysis:
        print("ERROR: Image analysis failed.")
        return jsonify({"error": "AI processing failed for the image."}), 500

    full_description = text_description or ""
    voice_transcription = None
    
    # 3. Voice Analysis (if audio present)
    if audio_file:
        print("STAGE 3: Processing Audio...")
        # Save audio temporarily for Gemini processing (required for file uploads)
        temp_path = os.path.join("/tmp", audio_file.filename)
        audio_file.save(temp_path)
        transcription_result = transcribe_audio_with_gemini(temp_path)
        os.remove(temp_path)
        
        if transcription_result and transcription_result.get("transcription"):
            voice_transcription = transcription_result["transcription"]
            full_description += f"\n\n(Voice Note Transcription: {voice_transcription})"
            print(f"STAGE 3: Voice Transcription Result: {voice_transcription[:50]}...")
    else:
        print("STAGE 3: Audio file skipped.")
    
    full_description = full_description.strip()
    if not full_description:
         print("ERROR: Final description is empty.")
         return jsonify({"error": "Processing failed: Could not generate a description from the provided input."}), 500

    # 4. Text Analysis
    text_analysis = analyze_text_with_gemini(full_description)
    print(f"STAGE 4: Text Analysis Result: {text_analysis}")
    if not text_analysis:
        print("ERROR: Text analysis failed.")
        return jsonify({"error": "AI processing failed for the text description."}), 500

    report_payload = {
        'image_analysis': image_analysis,
        'voice_transcription': voice_transcription,
        'text_analysis': text_analysis,
        'location_text': final_location_string,
    }
    
    # 5. Final Report Generation
    formal_report = generate_formal_report_with_gemini(report_payload)
    print(f"STAGE 5: Formal Report Result: {formal_report}")
    if not formal_report:
        print("ERROR: Final report generation failed.")
        return jsonify({"error": "AI failed to generate the final report."}), 500

    final_category = text_analysis.get("category", image_analysis.get("category", "Other"))
    final_priority = text_analysis.get("priority", "Medium")

    print("-" * 50)
    print(f"FINAL CLASSIFICATION: Category={final_category}, Priority={final_priority}")
    print("-" * 50)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        ghmc_id = f"GHMC/HYD/{int(datetime.now().timestamp())}"
        cursor.execute(
            """
            INSERT INTO complaints (ghmc_id, category, priority, subject, description, location, zone, gps_lat, gps_lng, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ghmc_id, final_category, final_priority,
                formal_report.get('subject', 'Untitled Complaint'),
                formal_report.get('description', full_description),
                final_location_string, # Full address string
                formal_report.get('zone', 'Unknown'),
                final_lat,
                final_lng,
                session.get('user_id')
            )
        )
        complaint_id = cursor.lastrowid
        conn.commit()
        print(f"SUCCESS: Complaint {ghmc_id} inserted into DB (ID: {complaint_id}).")
        
        return jsonify({
            "status": "success",
            "message": "Your complaint has been successfully submitted.",
            "acknowledgement": {
                "complaint_id": complaint_id,
                "ghmc_id": ghmc_id,
                "subject": formal_report.get('subject'),
                "category": final_category,
                "priority": final_priority
            }
        }), 201
    except sqlite3.Error as e:
        conn.rollback()
        print(f"DATABASE ERROR: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    finally:
        conn.close()
        print("-" * 50)
        print("END: Processing Complaint Report")
        print("-" * 50)

# ==================== 8. USER API ROUTES ====================

@app.route('/api/user/complaints')
@user_required
def get_user_complaints():
    conn = get_db_connection()
    complaints = conn.execute('''
        SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify([dict(c) for c in complaints])

@app.route('/api/user/complaints/<int:complaint_id>')
@user_required
def get_user_complaint_by_id(complaint_id):
    conn = get_db_connection()
    complaint = conn.execute('''
        SELECT * FROM complaints WHERE id = ? AND user_id = ?
    ''', (complaint_id, session['user_id'])).fetchone()
    conn.close()
    if complaint:
        return jsonify(dict(complaint))
    return jsonify({"error": "Complaint not found"}), 404

# ==================== 9. ADMIN & OTHER ENDPOINTS ====================

@app.route('/api/admin/complaints', methods=['GET'])
@admin_required
def get_all_complaints_api():
    conn = get_db_connection()
    complaints = conn.execute('SELECT * FROM complaints ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(c) for c in complaints])

@app.route('/api/admin/complaints/<int:complaint_id>', methods=['GET'])
@admin_required
def get_complaint_by_id(complaint_id):
    conn = get_db_connection()
    complaint = conn.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,)).fetchone()
    conn.close()
    if complaint:
        return jsonify(dict(complaint))
    return jsonify({"error": "Complaint not found"}), 404

@app.route('/api/admin/complaints/<int:complaint_id>/status', methods=['PUT'])
@admin_required
def update_complaint_status(complaint_id):
    data = request.get_json()
    new_status = data.get('status')
    changed_by = data.get('changed_by', 'Admin')
    comments = data.get('comments', '')
    
    conn = get_db_connection()
    complaint = conn.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,)).fetchone()
    
    if not complaint:
        conn.close()
        return jsonify({"error": "Complaint not found"}), 404
    
    old_status = complaint['status']
    # Update status and set updated_at to the current time
    conn.execute('UPDATE complaints SET status = ?, updated_at = ? WHERE id = ?',
                 (new_status, datetime.now(), complaint_id))
    # Log the status change
    conn.execute(
        'INSERT INTO status_history (complaint_id, old_status, new_status, changed_by, comments) VALUES (?, ?, ?, ?, ?)',
        (complaint_id, old_status, new_status, changed_by, comments)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Status updated successfully"})

@app.route('/request-location', methods=['GET'])
def request_location_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Request Location</title>
    </head>
    <body>
        <h1>Please enable location access</h1>
        <button onclick="getLocation()">Get My Location</button>
        <div id="location"></div>
        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition);
            } else {
                document.getElementById("location").innerHTML = "Geolocation is not supported by this browser.";
            }
        }
        function showPosition(position) {
            document.getElementById("location").innerHTML = 
            "Latitude: " + position.coords.latitude + "<br>Longitude: " + position.coords.longitude;
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/api/admin/complaints/<int:complaint_id>', methods=['DELETE'])
@admin_required
def delete_complaint(complaint_id):
    """
    Deletes a complaint from the database.
    Only accessible by admins.
    Logs deletion in status_history as 'Deleted'.
    """
    conn = get_db_connection()
    try:
        complaint = conn.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,)).fetchone()
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
        
        # Log deletion in status_history
        conn.execute(
            'INSERT INTO status_history (complaint_id, old_status, new_status, changed_by, comments) '
            'VALUES (?, ?, ?, ?, ?)',
            (complaint_id, complaint['status'], 'Deleted', 'Admin', 'Complaint deleted by admin')
        )
        
        # Delete complaint
        conn.execute('DELETE FROM complaints WHERE id = ?', (complaint_id,))
        conn.commit()
        
        return jsonify({"status": "success", "message": f"Complaint ID {complaint_id} has been deleted."})
    
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    
    finally:
        conn.close()



# ==================== 10. RUN FLASK APP ====================

if __name__ == '__main__':
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
    init_database()
    app.run(debug=True, port=5001)


