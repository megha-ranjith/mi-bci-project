import numpy as np
import mne
from scipy import signal
from config import EEG_CHANNELS, EEG_SAMPLING_RATE, WINDOW_SIZE

class EEGProcessor:
    def __init__(self):
        self.sampling_rate = EEG_SAMPLING_RATE
        self.window_size = WINDOW_SIZE
    
    def load_bcic_iv_2a(self, subject_id):
        """Load BCIC-IV-2a dataset for a subject"""
        try:
            # Auto-download from MNE
            from mne.datasets import eegbci
            raw_files = eegbci.load_data(subject_id, runs=[6, 10, 14])  # Train runs
            
            raws = [mne.io.read_raw_edf(f, preload=True) for f in raw_files]
            raw = mne.concatenate_raws(raws)
            
            return raw
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def preprocess_eeg(self, raw):
        """
        Preprocess raw EEG:
        - Filter 4-40 Hz
        - Re-reference to common average
        - Standardize
        """
        raw.filter(4, 40, l_trans_bandwidth=1, h_trans_bandwidth=5)
        raw.set_eeg_reference('average')
        
        return raw
    
    def extract_epochs(self, raw, events, event_id, tmin=-0.5, tmax=3.5):
        """Extract epochs from raw data"""
        epochs = mne.Epochs(raw, events, event_id, tmin, tmax, 
                           baseline=None, preload=True)
        return epochs
    
    def get_eeg_data(self, raw, channel_names=None):
        """Get EEG data as numpy array (channels × samples)"""
        data = raw.get_data()
        return data
    
    @staticmethod
    def bandpass_filter(data, lowcut, highcut, fs=250, order=4):
        """Apply butterworth bandpass filter"""
        nyquist = fs / 2
        low = lowcut / nyquist
        high = highcut / nyquist
        
        b, a = signal.butter(order, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, data, axis=-1)
        return filtered
    
    @staticmethod
    def normalize(data):
        """Standardize each channel"""
        mean = np.mean(data, axis=-1, keepdims=True)
        std = np.std(data, axis=-1, keepdims=True) + 1e-6
        return (data - mean) / std

# Global processor
processor = EEGProcessor()
