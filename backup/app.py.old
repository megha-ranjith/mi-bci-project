from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import torch
import numpy as np
import json
from datetime import datetime
import threading
from inference.predictor import IFNetPredictor
from utils.database import db
from utils.constants import CLASS_LABELS, CLASS_COLORS
from config import HOST, PORT, FLASK_ENV
import traceback

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize predictor
try:
    predictor = IFNetPredictor(device='cuda' if torch.cuda.is_available() else 'cpu')
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    predictor = None

# Active sessions tracking
active_sessions = {}

# ============= REST API ENDPOINTS =============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'device': 'CUDA' if torch.cuda.is_available() else 'CPU',
        'model_loaded': predictor is not None
    }), 200

@app.route('/api/user/create', methods=['POST'])
def create_user():
    """Create new BCI user"""
    try:
        data = request.json
        user_id = db.add_user(
            name=data.get('name'),
            age=data.get('age'),
            condition=data.get('condition', '')
        )
        return jsonify({'user_id': user_id, 'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start new BCI session for a user"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        session_id = db.add_session(user_id, notes=data.get('notes', ''))
        active_sessions[session_id] = {
            'user_id': user_id,
            'start_time': datetime.now(),
            'trials': []
        }
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'timestamp': datetime.now().isoformat()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Make prediction on EEG window
    Input: JSON with 'eeg_data' (channels x samples)
    """
    try:
        if predictor is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.json
        eeg_data = np.array(data.get('eeg_data'))
        session_id = data.get('session_id')
        true_label = data.get('true_label', -1)
        
        # Make prediction
        result = predictor.predict(eeg_data, return_explanation=True)
        
        # Log to database if session provided
        if session_id and session_id in active_sessions:
            trial_id = db.log_trial(
                session_id=session_id,
                true_label=true_label,
                pred_label=result['predicted_class'],
                confidence=result['confidence'],
                inf_time=result['inference_time']
            )
            result['trial_id'] = trial_id
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Prediction error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<int:session_id>/stats', methods=['GET'])
def get_session_stats(session_id):
    """Get session statistics"""
    try:
        stats = db.get_session_stats(session_id)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get MI class labels and colors"""
    return jsonify({
        'classes': CLASS_LABELS,
        'colors': CLASS_COLORS
    }), 200

# ============= WebSocket Events (Real-time Streaming) =============

@socketio.on('connect')
def handle_connect():
    """Client connects"""
    print(f"✅ Client connected: {request.sid}")
    emit('response', {'data': 'Connected to BCI server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnects"""
    print(f"❌ Client disconnected: {request.sid}")

@socketio.on('start_stream')
def handle_start_stream(data):
    """Start real-time prediction stream"""
    session_id = data.get('session_id')
    print(f"🎬 Stream started for session {session_id}")
    emit('stream_started', {'session_id': session_id})

@socketio.on('eeg_chunk')
def handle_eeg_chunk(data):
    """Receive and predict on EEG chunk"""
    try:
        eeg_data = np.array(data.get('eeg_data'))
        session_id = data.get('session_id')
        
        result = predictor.predict(eeg_data)
        result['class_name'] = CLASS_LABELS[result['predicted_class']]
        result['class_color'] = CLASS_COLORS[result['predicted_class']]
        
        # Emit to client
        emit('prediction_result', result, room=request.sid)
    
    except Exception as e:
        emit('error', {'message': str(e)}, room=request.sid)

@socketio.on('stop_stream')
def handle_stop_stream(data):
    """Stop streaming"""
    session_id = data.get('session_id')
    print(f"⏹️  Stream stopped for session {session_id}")
    emit('stream_stopped', {'session_id': session_id})

# ============= Error Handlers =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============= Run Server =============

if __name__ == '__main__':
    print(f"""
    🚀 Starting BCI Backend Server
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Environment: {FLASK_ENV}
    Host: {HOST}
    Port: {PORT}
    Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}
    Model: {'Loaded ✅' if predictor else 'Not Loaded ❌'}
    """)
    
    socketio.run(app, host=HOST, port=PORT, debug=(FLASK_ENV == 'development'))