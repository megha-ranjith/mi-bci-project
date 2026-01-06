import torch
import numpy as np
import torch.nn.functional as F

class XAIEngine:
    """
    Explainability Engine
    INNOVATION #7: Full XAI stack
    """
    
    def __init__(self, model, device='cpu'):
        self.model = model
        self.device = device
    
    def grad_cam(self, x, class_idx):
        """
        Grad-CAM for EEG
        x: (1, channels, samples)
        Returns: importance map for each channel
        """
        x = x.to(self.device)
        x.requires_grad = True
        
        # Forward pass with feature extraction
        logits, features, _ = self.model(x, return_features=True)
        
        # Get gradient of target class
        target_score = logits[0, class_idx]
        self.model.zero_grad()
        target_score.backward()
        
        # Get gradients from features
        gradients = x.grad  # (1, channels, samples)
        
        # Channel-wise importance
        channel_importance = gradients.abs().mean(dim=2).squeeze()  # (channels,)
        
        # Time-wise importance
        time_importance = gradients.abs().mean(dim=1).squeeze()  # (samples,)
        
        return {
            'channel_importance': channel_importance.detach().cpu().numpy(),
            'time_importance': time_importance.detach().cpu().numpy()
        }
    
    def integrated_gradients(self, x, class_idx, n_steps=20):
        """
        Integrated Gradients attribution
        More robust than simple gradients
        """
        x = x.to(self.device)
        baseline = torch.zeros_like(x)
        
        attributions = torch.zeros_like(x)
        
        for step in range(n_steps):
            alpha = step / n_steps
            interpolated = baseline + alpha * (x - baseline)
            interpolated.requires_grad = True
            
            logits = self.model(interpolated)
            target_score = logits[0, class_idx]
            
            self.model.zero_grad()
            target_score.backward()
            
            attributions += interpolated.grad
        
        attributions /= n_steps
        attributions *= (x - baseline)
        
        # Aggregate over samples
        channel_attr = attributions.abs().mean(dim=2).squeeze()
        time_attr = attributions.abs().mean(dim=1).squeeze()
        
        return {
            'channel_importance': channel_attr.detach().cpu().numpy(),
            'time_importance': time_attr.detach().cpu().numpy()
        }
    
    def feature_importance_attention(self, logits):
        """
        Convert softmax attention to importance scores
        INNOVATION #8: Attention-based explanation
        """
        probs = F.softmax(logits, dim=1)
        confidence = probs.max(item=1).values
        
        return {
            'class_probabilities': probs.detach().cpu().numpy()[0],
            'confidence': confidence.item(),
            'predicted_class': logits.argmax(dim=1).item()
        }
    
    def generate_explanation(self, x, class_idx):
        """Generate full explanation for a prediction"""
        grad_cam_result = self.grad_cam(x, class_idx)
        ig_result = self.integrated_gradients(x, class_idx)
        
        return {
            'grad_cam': grad_cam_result,
            'integrated_gradients': ig_result,
            'method': 'Hybrid Grad-CAM + Integrated Gradients'
        }
