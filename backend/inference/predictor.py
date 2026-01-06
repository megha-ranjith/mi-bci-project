import torch
import numpy as np
from utils.eeg_processor import EEGProcessor
from models.ifnet_enhanced import IFNetEnhanced
from models.feature_extractors import FeatureExtractor
from inference.xai_engine import XAIEngine
from utils.database import db
import time

class IFNetPredictor:
    """
    Main prediction engine
    Handles: preprocessing, inference, XAI, DB logging
    """
    
    def __init__(self, model_path=None, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model = IFNetEnhanced(n_channels=22, n_classes=4)
        
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=device))
        
        self.model = self.model.to(device)
        self.model.eval()
        
        self.xai_engine = XAIEngine(self.model, device)
        self.processor = EEGProcessor()
    
    def predict(self, eeg_window, return_explanation=True):
        """
        Single prediction
        eeg_window: (channels, samples)
        Returns: class, confidence, explanation
        """
        start_time = time.time()
        
        # Preprocess
        eeg_window = self._preprocess(eeg_window)
        eeg_tensor = torch.FloatTensor(eeg_window).unsqueeze(0).to(self.device)
        
        # Predict with uncertainty
        with torch.no_grad():
            mean_pred, var_pred = self.model.predict_with_uncertainty(eeg_tensor, n_samples=10)
        
        predicted_class = mean_pred.argmax(dim=1).item()
        confidence = mean_pred[0, predicted_class].item()
        uncertainty = var_pred[0, predicted_class].item()
        
        inference_time = time.time() - start_time
        
        result = {
            'predicted_class': predicted_class,
            'confidence': confidence,
            'uncertainty': uncertainty,
            'inference_time': inference_time,
            'probabilities': mean_pred[0].cpu().numpy().tolist()
        }
        
        # Generate explanation if requested
        if return_explanation:
            explanation = self.xai_engine.generate_explanation(eeg_tensor, predicted_class)
            result['explanation'] = explanation
        
        return result
    
    def _preprocess(self, eeg_window):
        """Normalize EEG window"""
        return self.processor.normalize(eeg_window)
    
    def batch_predict(self, eeg_windows):
        """Predict multiple windows"""
        results = []
        for window in eeg_windows:
            results.append(self.predict(window))
        return results

import os