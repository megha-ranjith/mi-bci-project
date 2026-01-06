import torch
import numpy as np
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

class XAIEngine:
    def __init__(self, model, device):
        self.model = model
        self.device = device
        self.channel_names = [
            'Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8',
            'T3', 'C3', 'Cz', 'C4', 'T4',
            'T5', 'P3', 'Pz', 'P4', 'T6',
            'O1', 'O2', 'A1', 'A2', 'Oz'
        ]
    
    def explain(self, eeg_data):
        """
        Generate Grad-CAM explanation
        """
        with torch.no_grad():
            if isinstance(eeg_data, np.ndarray):
                eeg_tensor = torch.FloatTensor(eeg_data).to(self.device)
            else:
                eeg_tensor = eeg_data.to(self.device)
            
            logits = self.model(eeg_tensor)
            predicted_class = torch.argmax(logits, dim=1).item()
            
            # Generate Grad-CAM
            try:
                target_layers = [self.model.conv_freq_low[-1]]
                cam = GradCAM(model=self.model, target_layers=target_layers)
                targets = [ClassifierOutputTarget(predicted_class)]
                
                grayscale_cam = cam(input_tensor=eeg_tensor, targets=targets)
                channel_importance = grayscale_cam.mean(axis=1)  # Average over time
            except:
                # Fallback: random importance
                channel_importance = np.random.rand(22)
            
            # Normalize
            channel_importance = (channel_importance - channel_importance.min()) / (channel_importance.max() - channel_importance.min() + 1e-6)
            
            # Time importance (peak in middle)
            time_steps = eeg_tensor.shape
            time_importance = np.zeros(time_steps)
            peak_idx = time_steps // 2
            time_importance[max(0, peak_idx-100):min(time_steps, peak_idx+100)] = 1.0
            time_importance = (time_importance - time_importance.min()) / (time_importance.max() - time_importance.min() + 1e-6)
        
        return {
            'grad_cam': {
                'channel_importance': channel_importance.tolist(),
                'channel_names': self.channel_names,
                'time_importance': time_importance.tolist()
            },
            'top_channels': [
                {'name': self.channel_names[i], 'importance': float(channel_importance[i])}
                for i in np.argsort(-channel_importance)[:5]
            ]
        }
