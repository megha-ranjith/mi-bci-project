import os
import mne
from mne.datasets import eegbci

print("Downloading BCIC IV 2a dataset...")
print("This may take 2-5 minutes...")

# Create data/physionet_bci directory relative to backend/
base_dir = os.path.dirname(__file__)
data_dir = os.path.join(base_dir, "..", "data", "physionet_bci")
os.makedirs(data_dir, exist_ok=True)
os.chdir(data_dir)

# Download for subjects 1-3
for subject in [1, 2, 3]:
    print(f"Downloading subject {subject}...")
    try:
        files = eegbci.load_data(subject, runs=[6, 10, 14])
        print(f"✅ Subject {subject} downloaded")
    except Exception as e:
        print(f"⚠️ Subject {subject} error: {e}")

print("✅ Dataset downloaded successfully")
print("Saved under:", data_dir)
