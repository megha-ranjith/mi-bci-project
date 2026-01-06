import torch
import torch.nn as nn
import torch.nn.functional as F

class SEBlock(nn.Module):
    """Squeeze-and-Excitation attention block"""
    def __init__(self, channels, reduction=16):
        super(SEBlock, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.fc1 = nn.Linear(channels, channels // reduction)
        self.fc2 = nn.Linear(channels // reduction, channels)
    
    def forward(self, x):
        # x: (batch, channels, length)
        batch, channels, _ = x.size()
        
        # Squeeze
        se = self.avg_pool(x).view(batch, channels)
        # Excitation
        se = F.relu(self.fc1(se))
        se = torch.sigmoid(self.fc2(se))
        se = se.view(batch, channels, 1)
        
        return x * se

class IFNetEnhanced(nn.Module):
    """
    Enhanced IFNet with multiple innovations:
    - Multi-scale frequency processing
    - Attention mechanisms
    - Domain adaptation components
    - Uncertainty estimation
    """
    
    def __init__(self, n_channels=22, n_classes=4, dropout=0.5):
        super(IFNetEnhanced, self).__init__()
        
        self.n_channels = n_channels
        self.n_classes = n_classes
        
        # BRANCH 1: Low frequency (4-16 Hz)
        self.low_freq_spatial = nn.Conv1d(n_channels, 32, kernel_size=50, 
                                         stride=1, padding='same', bias=False)
        self.low_freq_temporal = nn.Conv1d(32, 32, kernel_size=10,
                                          stride=1, padding='same', bias=False)
        self.low_freq_bn = nn.BatchNorm1d(32)
        self.low_freq_se = SEBlock(32)
        
        # BRANCH 2: High frequency (16-40 Hz)
        self.high_freq_spatial = nn.Conv1d(n_channels, 32, kernel_size=25,
                                          stride=1, padding='same', bias=False)
        self.high_freq_temporal = nn.Conv1d(32, 32, kernel_size=5,
                                           stride=1, padding='same', bias=False)
        self.high_freq_bn = nn.BatchNorm1d(32)
        self.high_freq_se = SEBlock(32)
        
        # Fusion: Interactive frequency layer
        self.interaction = nn.Conv1d(64, 64, kernel_size=1)
        self.fusion_bn = nn.BatchNorm1d(64)
        
        # Log power pooling layer (CSP-inspired)
        self.pool = nn.AdaptiveAvgPool1d(1)
        
        # Classification head
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(64, 128)
        self.fc_bn = nn.BatchNorm1d(128)
        self.fc2 = nn.Linear(128, n_classes)
        
        # Uncertainty head (Bayesian MC Dropout)
        self.uncertainty_head = nn.Linear(128, n_classes)
    
    def forward(self, x, return_features=False):
        """
        x: (batch, channels, samples)
        """
        batch_size = x.size(0)
        
        # Branch 1: Low frequency
        low = self.low_freq_spatial(x)
        low = F.elu(self.low_freq_bn(low))
        low = self.low_freq_temporal(low)
        low = self.low_freq_se(low)
        
        # Branch 2: High frequency
        high = self.high_freq_spatial(x)
        high = F.elu(self.high_freq_bn(high))
        high = self.high_freq_temporal(high)
        high = self.high_freq_se(high)
        
        # Fusion: Interactive frequency
        fused = torch.cat([low, high], dim=1)  # (batch, 64, samples)
        fused = self.interaction(fused)
        fused = self.fusion_bn(fused)
        
        # Log power pooling
        fused = torch.log(torch.clamp(self.pool(fused ** 2), min=1e-6))
        fused = fused.view(batch_size, -1)  # (batch, 64)
        
        # Classification
        features = F.relu(self.fc_bn(self.fc1(fused)))
        features_dropout = self.dropout(features)
        logits = self.fc2(features_dropout)
        
        # Uncertainty
        uncertainty = self.uncertainty_head(features_dropout)
        
        if return_features:
            return logits, features, uncertainty
        
        return logits
    
    def predict_with_uncertainty(self, x, n_samples=10):
        """MC Dropout for uncertainty estimation"""
        self.train()  # Enable dropout
        
        predictions = []
        for _ in range(n_samples):
            logits = self.forward(x)
            predictions.append(F.softmax(logits, dim=1))
        
        self.eval()
        
        # Stack predictions
        preds = torch.stack(predictions)  # (n_samples, batch, n_classes)
        
        # Mean and variance
        mean_pred = preds.mean(dim=0)  # (batch, n_classes)
        var_pred = preds.var(dim=0)    # (batch, n_classes)
        
        return mean_pred, var_pred