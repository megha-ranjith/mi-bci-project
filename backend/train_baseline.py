import torch
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import mne
from mne.datasets import eegbci
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from models.ifnet_enhanced import IFNetEnhanced
from utils.constants import *

print("=" * 60)
print("TRAINING BASELINE IFNET MODEL")
print("=" * 60)

# 1. Load dataset
print("\n[1/5] Loading dataset...")
subject = 1
raw_files = eegbci.load_data(subject, runs=[6, 10, 14], path='../data/physionet_bci')

raw = mne.concatenate_raws([mne.io.read_raw_edf(f, preload=True) for f in raw_files])

# 2. Preprocess
print("[2/5] Preprocessing...")
raw.filter(4, 40, fir_design='firwin')

# 3. Extract epochs
print("[3/5] Extracting epochs...")
events, event_ids = mne.events_from_annotations(raw)
event_map = {'T1': 0, 'T2': 1, 'T3': 2, 'T4': 3}
events[:, 2] = np.array([event_map.get(list(event_ids.keys())[v-1], v) for v in events[:, 2]])

epochs = mne.Epochs(raw, events, event_ids=event_map, tmin=0, tmax=3, baseline=None)
X = epochs.get_data()  # (n_epochs, 22, 750)
y = epochs.events[:, 2]

print(f"   Shape: {X.shape}, Labels: {np.unique(y)}")

# 4. Train-test split
print("[4/5] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalize
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1])).reshape(X_train.shape)
X_test = scaler.transform(X_test.reshape(-1, X_test.shape[-1])).reshape(X_test.shape)

X_train = torch.FloatTensor(X_train)
X_test = torch.FloatTensor(X_test)
y_train = torch.LongTensor(y_train)
y_test = torch.LongTensor(y_test)

# 5. Initialize and train model
print("[5/5] Training model...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"   Using device: {device}")

model = IFNetEnhanced(num_classes=4).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()

epochs_to_train = 50
batch_size = 32

best_accuracy = 0
for epoch in range(epochs_to_train):
    # Training
    model.train()
    train_loss = 0
    for i in range(0, len(X_train), batch_size):
        batch_x = X_train[i:i+batch_size].to(device)
        batch_y = y_train[i:i+batch_size].to(device)
        
        optimizer.zero_grad()
        logits = model(batch_x)
        loss = criterion(logits, batch_y)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    
    # Validation
    model.eval()
    with torch.no_grad():
        logits = model(X_test.to(device))
        predictions = logits.argmax(dim=1).cpu()
        accuracy = (predictions == y_test).float().mean().item()
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        torch.save(model.state_dict(), 'models/trained_model.pth')
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs_to_train} - Loss: {train_loss/len(X_train):.4f}, Accuracy: {accuracy:.4f}")

print(f"\n✅ Training complete!")
print(f"Best accuracy: {best_accuracy:.4f} ({best_accuracy*100:.1f}%)")
print(f"Model saved to: models/trained_model.pth")
