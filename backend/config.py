import os
from dotenv import load_dotenv

load_dotenv()

# Server
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
HOST = '0.0.0.0'
PORT = 5000

# Database
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'bci_system.db')
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'trained_model.pth')
DEVICE = 'cuda' if __import__('torch').cuda.is_available() else 'cpu'

# EEG
SAMPLING_RATE = 250
WINDOW_SIZE = 750  # 3 seconds
NUM_CHANNELS = 22
NUM_CLASSES = 4

# Aliases for modules that import old names
EEG_SAMPLING_RATE = SAMPLING_RATE
EEG_CHANNELS = NUM_CHANNELS
EEG_WINDOW_SIZE = WINDOW_SIZE

# Features
FREQ_BANDS = {
    'delta': (1, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 45)
}

# XAI
GRAD_CAM_ENABLED = True
INTEGRATED_GRADIENTS_ENABLED = True

# Uncertainty
MC_DROPOUT_SAMPLES = 10
