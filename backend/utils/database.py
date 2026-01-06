import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            condition TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Sessions table
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            num_trials INTEGER DEFAULT 0,
            avg_accuracy REAL DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )''')
        
        # Trials table
        c.execute('''CREATE TABLE IF NOT EXISTS trials (
            trial_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            true_label INTEGER DEFAULT -1,
            predicted_label INTEGER,
            confidence REAL,
            uncertainty REAL DEFAULT 0,
            inference_time REAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )''')
        
        # XAI results table
        c.execute('''CREATE TABLE IF NOT EXISTS xai_results (
            xai_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trial_id INTEGER NOT NULL,
            important_channels TEXT,
            time_importance TEXT,
            frequency_importance TEXT,
            FOREIGN KEY (trial_id) REFERENCES trials(trial_id)
        )''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, name, age, condition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO users (name, age, condition) VALUES (?, ?, ?)',
                  (name, age, condition))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    
    def create_session(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO sessions (user_id) VALUES (?)', (user_id,))
        conn.commit()
        session_id = c.lastrowid
        conn.close()
        return session_id
    
    def create_trial(self, session_id, predicted_label, confidence, true_label=-1):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO trials (session_id, predicted_label, confidence, true_label)
                     VALUES (?, ?, ?, ?)''',
                  (session_id, predicted_label, confidence, true_label))
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT user_id, name, age, condition FROM users')
        users = [{'user_id': row, 'name': row, 'age': row, 'condition': row} 
                 for row in c.fetchall()]
        conn.close()
        return users
    
    def update_session(self, session_id, num_trials, avg_accuracy):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE sessions SET num_trials = ?, avg_accuracy = ? WHERE session_id = ?',
                  (num_trials, avg_accuracy, session_id))
        conn.commit()
        conn.close()
