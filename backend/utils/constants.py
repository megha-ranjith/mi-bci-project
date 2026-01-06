# EEG Band definitions (Hz)
EEG_BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'beta': (13, 30),
    'gamma': (30, 100)
}

# Motor cortex channels (for attention)
MOTOR_CHANNELS = ['C3', 'C4', 'CP3', 'CP4', 'P3', 'P4', 'Cz', 'CPz']

# Class labels
CLASS_LABELS = {
    0: 'Left Hand',
    1: 'Right Hand',
    2: 'Both Feet',
    3: 'Tongue'
}

# Color mapping for visualization
CLASS_COLORS = {
    0: '#FF6B6B',  # Red for left
    1: '#4ECDC4',  # Teal for right
    2: '#45B7D1',  # Blue for feet
    3: '#FFA07A'   # Salmon for tongue
}