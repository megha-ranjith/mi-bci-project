"""
MI-BCI Flask Backend Server
Real-time motor imagery EEG classification with explainability
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import torch
import numpy as np
import json
import time
import threading
from datetime import datetime
import sqlite3
import os

from config import *
from utils.database import Database
from models.ifnet_enhanced import IFNetEnhanced
from inference.predictor import IFNetPredictor
from inference.xai_engine import XAIEngine

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi-bci-secret-key-2026'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
db = Database(DATABASE_PATH)
predictor = None
xai_engine = None
active_sessions = {}
streaming_threads = {}

print("[INFO] Initializing MI-BCI Backend...")

# Initialize model
def init_model():
    global predictor, xai_engine
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[INFO] Using device: {device}")
        
        model = IFNetEnhanced(num_classes=NUM_CLASSES).to(device)
        
        # Load weights if exists
        if os.path.exists(MODEL_PATH):
            model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
            print(f"[INFO] Model loaded from {MODEL_PATH}")
        else:
            print(f"[WARNING] No model found at {MODEL_PATH}. Using random weights.")
        
        predictor = IFNetPredictor(model, device)
        xai_engine = XAIEngine(model, device)
        print("[INFO] Model initialized successfully")
    except Exception as e:
        print(f"[ERROR] Model initialization failed: {e}")

init_model()

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': predictor is not None,
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'database': 'connected'
    }), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = db.get_all_users()
        return jsonify({'users': users}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user"""
    try:
        data = request.json
        user_id = db.create_user(
            name=data.get('name', 'Unknown'),
            age=data.get('age', 0),
            condition=data.get('condition', 'unknown')
        )
        return jsonify({'user_id': user_id, 'status': 'created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    """Start a new BCI session"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)
        
        session_id = db.create_session(user_id)
        active_sessions[session_id] = {
            'user_id': user_id,
            'start_time': datetime.now(),
            'trials': [],
            'predictions': []
        }
        
        return jsonify({
            'session_id': session_id,
            'user_id': user_id,
            'status': 'started'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>/end', methods=['POST'])
def end_session(session_id):
    """End current BCI session"""
    try:
        if session_id in active_sessions:
            session_data = active_sessions[session_id]
            predictions = np.array(session_data['predictions'])
            
            if len(predictions) > 0:
                accuracy = np.mean(predictions[:, 2])  # Confidence column
            else:
                accuracy = 0
            
            db.update_session(session_id, len(session_data['trials']), accuracy)
            del active_sessions[session_id]
            
            return jsonify({
                'session_id': session_id,
                'status': 'ended',
                'total_trials': len(session_data['trials']),
                'accuracy': float(accuracy)
            }), 200
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    try:
        if session_id in active_sessions:
            session_data = active_sessions[session_id]
            return jsonify({
                'session_id': session_id,
                'user_id': session_data['user_id'],
                'start_time': session_data['start_time'].isoformat(),
                'trials_count': len(session_data['trials']),
                'predictions': session_data['predictions'][:20]  # Last 20
            }), 200
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make a prediction from EEG data"""
    try:
        data = request.json
        eeg_data = np.array(data.get('eeg_data', []))
        
        if eeg_data.size == 0:
            return jsonify({'error': 'No EEG data provided'}), 400
        
        # Reshape: (channels, samples) -> (1, channels, samples)
        if len(eeg_data.shape) == 2:
            eeg_data = eeg_data[np.newaxis, :, :]
        
        # Predict
        result = predictor.predict(eeg_data)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# WEBSOCKET EVENTS (Real-time streaming)
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"[SOCKET] Client connected: {request.sid}")
    emit('response', {'data': 'Connected to MI-BCI server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"[SOCKET] Client disconnected: {request.sid}")

@socketio.on('start_stream')
def handle_start_stream(data):
    """Start EEG streaming"""
    session_id = data.get('session_id', 1)
    
    def stream_eeg():
        """Simulate EEG streaming"""
        for i in range(100):  # 100 predictions
            if session_id not in active_sessions:
                break
            
            # Simulate EEG data
            eeg_data = np.random.randn(1, NUM_CHANNELS, WINDOW_SIZE).astype(np.float32)
            
            # Predict
            prediction = predictor.predict(eeg_data)
            
            # Get XAI
            xai_data = xai_engine.explain(eeg_data)
            
            # Combine
            result = {
                **prediction,
                'xai': xai_data,
                'trial_number': i + 1
            }
            
            # Log to DB
            db.create_trial(
                session_id=session_id,
                predicted_label=prediction['predicted_class'],
                confidence=prediction['confidence']
            )
            
            # Emit to client
            socketio.emit('prediction_update', result, room=request.sid)
            
            time.sleep(0.1)  # 100ms between predictions
    
    # Start streaming in background
    thread = threading.Thread(target=stream_eeg, daemon=True)
    streaming_threads[session_id] = thread
    thread.start()
    
    emit('stream_started', {'session_id': session_id, 'status': 'streaming'})

@socketio.on('stop_stream')
def handle_stop_stream(data):
    """Stop EEG streaming"""
    session_id = data.get('session_id', 1)
    
    if session_id in streaming_threads:
        del streaming_threads[session_id]
    
    emit('stream_stopped', {'session_id': session_id, 'status': 'stopped'})

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print(f"[INFO] Starting MI-BCI server on {HOST}:{PORT}")
    print(f"[INFO] API docs available at http://{HOST}:{PORT}/api/health")
    
    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=DEBUG,
        allow_unsafe_werkzeug=True
    )