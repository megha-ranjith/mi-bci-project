import numpy as np
from scipy import signal
from scipy.fft import fft
import pywt

class FeatureExtractor:
    """Extract multi-modal EEG features"""
    
    @staticmethod
    def frequency_features(eeg_window, fs=250, bands=None):
        """
        INNOVATION #1: Multi-band frequency analysis
        Extract power in multiple frequency bands
        eeg_window: (channels, samples)
        """
        if bands is None:
            bands = {'delta': (0.5, 4), 'theta': (4, 8), 'alpha': (8, 13),
                    'beta': (13, 30), 'gamma': (30, 100)}
        
        n_channels = eeg_window.shape[0]
        features = []
        
        for band_name, (low, high) in bands.items():
            # Butterworth filter
            nyquist = fs / 2
            low_norm = low / nyquist
            high_norm = high / nyquist
            b, a = signal.butter(4, [low_norm, high_norm], btype='band')
            
            # Filter each channel
            filtered = np.zeros_like(eeg_window)
            for ch in range(n_channels):
                filtered[ch] = signal.filtfilt(b, a, eeg_window[ch])
            
            # Log power (like CSP)
            power = np.log(np.var(filtered, axis=-1) + 1e-6)
            features.append(power)
        
        return np.concatenate(features)  # (n_channels * n_bands,)
    
    @staticmethod
    def wavelet_features(eeg_window, fs=250, wavelet='db4', levels=5):
        """
        INNOVATION #2: Continuous Wavelet Transform (CWT) features
        More time-frequency resolution than simple bands
        """
        n_channels = eeg_window.shape[0]
        features = []
        
        scales = np.arange(1, levels + 1)
        
        for ch in range(n_channels):
            # CWT using db4 wavelet
            coefficients, frequencies = pywt.cwt(eeg_window[ch], scales, wavelet)
            
            # Mean power across time for each scale (frequency)
            power = np.mean(np.abs(coefficients) ** 2, axis=1)
            power_log = np.log(power + 1e-6)
            features.append(power_log)
        
        return np.concatenate(features)  # (n_channels * levels,)
    
    @staticmethod
    def emd_features(eeg_window, max_imf=5):
        """
        INNOVATION #3: Empirical Mode Decomposition
        Adaptive, data-driven feature extraction
        Extract intrinsic mode functions (IMFs)
        """
        try:
            from PyEMD import EMD
        except ImportError:
            print("PyEMD not installed, skipping EMD")
            return np.zeros(eeg_window.shape[0] * max_imf)
        
        n_channels = eeg_window.shape[0]
        features = []
        
        for ch in range(n_channels):
            emd = EMD()
            imfs = emd(eeg_window[ch])[:max_imf]
            
            # Pad if fewer IMFs
            if len(imfs) < max_imf:
                imfs = np.vstack([imfs, np.zeros((max_imf - len(imfs), eeg_window.shape[1]))])
            
            # Mean energy per IMF
            energy = np.mean(imfs ** 2, axis=1)
            energy_log = np.log(energy + 1e-6)
            features.append(energy_log)
        
        return np.concatenate(features)  # (n_channels * max_imf,)
    
    @staticmethod
    def temporal_features(eeg_window):
        """
        INNOVATION #4: Statistical temporal features
        Variance, skewness, kurtosis per channel
        """
        n_channels = eeg_window.shape[0]
        features = []
        
        for ch in range(n_channels):
            signal_ch = eeg_window[ch]
            
            var = np.var(signal_ch)
            mean = np.mean(signal_ch)
            skew = signal.skew(signal_ch)
            kurt = signal.kurtosis(signal_ch)
            
            features.extend([var, mean, skew, kurt])
        
        return np.array(features)  # (n_channels * 4,)
    
    @staticmethod
    def spatial_features(eeg_window):
        """
        INNOVATION #5: Spatial correlation between channels
        Captures cross-channel coupling
        """
        # Compute correlation matrix
        corr_matrix = np.corrcoef(eeg_window)
        
        # Extract upper triangle (avoid redundancy)
        triu_indices = np.triu_indices_from(corr_matrix, k=1)
        corr_features = corr_matrix[triu_indices]
        
        return corr_features  # (n_channels * (n_channels - 1) / 2,)
    
    @classmethod
    def extract_multimodal(cls, eeg_window, fs=250):
        """
        INNOVATION #6: Multi-modal fusion
        Concatenate all feature types
        """
        freq_feat = cls.frequency_features(eeg_window, fs)
        wav_feat = cls.wavelet_features(eeg_window, fs)
        temporal_feat = cls.temporal_features(eeg_window)
        spatial_feat = cls.spatial_features(eeg_window)
        
        # Skip EMD if not available
        try:
            emd_feat = cls.emd_features(eeg_window)
        except:
            emd_feat = np.array([])
        
        # Concatenate all
        all_features = np.concatenate([feat for feat in 
                                     [freq_feat, wav_feat, emd_feat, 
                                      temporal_feat, spatial_feat] 
                                     if len(feat) > 0])
        
        return all_features
