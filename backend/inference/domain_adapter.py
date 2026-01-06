import torch
import torch.nn as nn
import numpy as np

class DomainAdapter:
    """
    INNOVATION #9: Domain Adaptation
    Helps model generalize to new subjects
    """
    
    def __init__(self, model, source_domain_data=None):
        self.model = model
        self.source_domain_data = source_domain_data
    
    def compute_mmd(self, source_features, target_features):
        """
        Maximum Mean Discrepancy loss
        Minimizes distance between source and target feature distributions
        """
        # RBF kernel
        def kernel(x, y):
            x_size = x.size(0)
            y_size = y.size(0)
            
            xx = (x * x).sum(dim=1, keepdim=True).expand(x_size, y_size)
            yy = (y * y).sum(dim=1, keepdim=True).expand(y_size, x_size).t()
            xy = torch.mm(x, y.t())
            
            dist = xx + yy - 2 * xy
            return torch.exp(-dist / 2)
        
        Kxx = kernel(source_features, source_features)
        Kyy = kernel(target_features, target_features)
        Kxy = kernel(source_features, target_features)
        
        mmd = Kxx.mean() + Kyy.mean() - 2 * Kxy.mean()
        return mmd
    
    def adversarial_loss(self, domain_logits):
        """
        Domain discriminator loss
        Fool discriminator to make domains indistinguishable
        """
        # Fake labels (all target domain = 0)
        fake_labels = torch.zeros(domain_logits.size(0)).long()
        loss = nn.CrossEntropyLoss()(domain_logits, fake_labels)
        return loss
    
    def adapt_to_subject(self, target_eeg_samples, n_iterations=100, lr=1e-4):
        """
        Quick adaptation to new subject
        Uses only a few calibration trials
        """
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        
        for i in range(n_iterations):
            # Extract features from target subject
            target_features = self._extract_features(target_eeg_samples)
            
            # MMD loss (align with source)
            if self.source_domain_data is not None:
                source_features = self._extract_features(self.source_domain_data)
                mmd_loss = self.compute_mmd(source_features, target_features)
            else:
                mmd_loss = 0
            
            optimizer.zero_grad()
            mmd_loss.backward()
            optimizer.step()
        
        return self.model
    
    def _extract_features(self, eeg_data):
        """Extract features using model's feature extraction"""
        self.model.eval()
        with torch.no_grad():
            _, features, _ = self.model(eeg_data, return_features=True)
        return features
