import sqlite3
import os

DB_PATH = '../data/bci_system.db'
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Creating database tables...")

# Users
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        condition TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Sessions
c.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        num_trials INTEGER DEFAULT 0,
        avg_accuracy REAL DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
''')

# Trials
c.execute('''
    CREATE TABLE IF NOT EXISTS trials (
        trial_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        true_label INTEGER,
        predicted_label INTEGER,
        confidence REAL,
        uncertainty REAL,
        inference_time REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
    )
''')

# XAI Results
c.execute('''
    CREATE TABLE IF NOT EXISTS xai_results (
        xai_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trial_id INTEGER NOT NULL,
        important_channels TEXT,
        time_importance TEXT,
        frequency_importance TEXT,
        FOREIGN KEY (trial_id) REFERENCES trials(trial_id)
    )
''')

conn.commit()
conn.close()

print("✅ Database initialized at:", DB_PATH)
