from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import pandas as pd
import joblib
import datetime
import random
from dotenv import load_dotenv
from functools import wraps
from utils.fetch_satellite_data import fetch_firms_data, fetch_weather_data
from utils.preprocess import preprocess_input
from utils.sms_alert import send_sms_alert
from utils.telegram_alert import send_telegram_message

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'wildfire-secret-key-change-in-production')

# Session configuration - sessions expire when browser closes
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)
app.config['SESSION_PERMANENT'] = False  # Session expires when browser closes

# Global State to simulate a real-time database
global_data = {
    'active_hotspots': 0,
    'global_risk': 'Low Risk',
    'latest_weather': {
        'temperature': 25,
        'humidity': 50,
        'wind_speed': 10,
        'rainfall': 0,
        'ndvi': 0.5
    },
    'history': [] # Stores past weather for trends
}

# Initial history seed
for i in range(10):
    global_data['history'].append({
        'time': (datetime.datetime.now() - datetime.timedelta(hours=(10-i))).strftime('%H:%M'),
        'temp': random.uniform(20, 30),
        'hum': random.uniform(40, 60)
    })

# Load Model
MODEL_PATH = 'model/wildfire_model.pkl'
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)

load_model()

# Firebase Configuration
firebase_config = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.getenv('FIREBASE_APP_ID')
}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_authenticated' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    # Always show login page - clear any existing session
    session.clear()
    return render_template('login.html', firebase_config=firebase_config)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/auth/verify', methods=['POST'])
def verify_auth():
    """Simple session-based auth verification (client-side Firebase handles actual auth)"""
    data = request.json
    token = data.get('token')
    
    if token:
        # In production, you would verify the Firebase token here
        # For now, we'll trust the client-side Firebase auth
        session['user_authenticated'] = True
        session['firebase_token'] = token
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'No token provided'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/dashboard_stats')
def get_stats():
    return jsonify({
        'active_hotspots': global_data['active_hotspots'],
        'global_risk': global_data['global_risk']
    })

@app.route('/api/weather_trends')
def get_trends():
    return jsonify(global_data['history'])

@app.route('/fetch_satellite_data', methods=['POST'])
def fetch_data():
    data = request.json
    region = data.get('region')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    
    # Simulate fetching
    firms_data = fetch_firms_data(region, from_date, to_date)
    weather_data = fetch_weather_data(region)
    
    # Update Global State
    global_data['active_hotspots'] = len(firms_data)
    global_data['latest_weather'] = weather_data
    
    # Add to history for trends
    global_data['history'].append({
        'time': datetime.datetime.now().strftime('%H:%M'),
        'temp': weather_data['temperature'],
        'hum': weather_data['humidity']
    })
    if len(global_data['history']) > 15:
        global_data['history'].pop(0)
    
    return jsonify({
        'firms_count': len(firms_data),
        'weather_data': weather_data
    })

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        load_model()
        if model is None:
            return jsonify({'error': 'Model not trained yet'}), 500
            
    data = request.json
    processed_df = preprocess_input(data)
    
    prediction = model.predict(processed_df)[0]
    probabilities = model.predict_proba(processed_df)[0]
    confidence = float(max(probabilities) * 100)
    
    risk_map = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}
    risk_level = risk_map[prediction]
    
    # Update global risk state
    global_data['global_risk'] = risk_level
    
    # Alert logic for High Risk
    sms_status = None
    telegram_status = None
    phone_number = data.get('phone_number')
    
    if prediction == 2:
        # 1. Send SMS (Online/Offline) if phone exists
        if phone_number:
            _, sms_status = send_sms_alert(phone_number, f"URGENT: High Wildfire Risk detected! Confidence: {confidence:.2f}%")
        
        # 2. Always try Telegram (Free)
        success_tg, tg_msg = send_telegram_message(f"🔥 *Wildfire Alert*\nRisk: *High*\nConfidence: *{confidence:.2f}%*\nLocation: {data.get('region', 'Unknown Region')}")
        telegram_status = tg_msg

    return jsonify({
        'prediction': int(prediction),
        'risk_level': risk_level,
        'confidence': f"{confidence:.2f}%",
        'sms_status': sms_status,
        'telegram_status': telegram_status
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
