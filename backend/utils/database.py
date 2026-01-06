import sqlite3
from datetime import datetime
from config import DATABASE_PATH
import os

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            condition TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Sessions table
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            num_trials INTEGER,
            avg_accuracy REAL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )''')
        
        # Trials table (detailed logging)
        c.execute('''CREATE TABLE IF NOT EXISTS trials (
            trial_id INTEGER PRIMARY KEY,
            session_id INTEGER NOT NULL,
            true_label INTEGER,
            predicted_label INTEGER,
            confidence REAL,
            inference_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )''')
        
        # XAI results table
        c.execute('''CREATE TABLE IF NOT EXISTS xai_results (
            xai_id INTEGER PRIMARY KEY,
            trial_id INTEGER NOT NULL,
            important_channels TEXT,  
            time_importance TEXT,   
            frequency_importance TEXT,
            FOREIGN KEY (trial_id) REFERENCES trials(trial_id)
        )''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, age, condition):
        """Add new user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO users (name, age, condition) VALUES (?, ?, ?)',
                 (name, age, condition))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    
    def add_session(self, user_id, num_trials=0, avg_accuracy=0.0, notes=''):
        """Add new session"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO sessions (user_id, num_trials, avg_accuracy, notes) VALUES (?, ?, ?, ?)',
                 (user_id, num_trials, avg_accuracy, notes))
        conn.commit()
        session_id = c.lastrowid
        conn.close()
        return session_id
    
    def log_trial(self, session_id, true_label, pred_label, confidence, inf_time):
        """Log single trial result"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO trials (session_id, true_label, predicted_label, confidence, inference_time)
                     VALUES (?, ?, ?, ?, ?)''',
                 (session_id, true_label, pred_label, confidence, inf_time))
        conn.commit()
        trial_id = c.lastrowid
        conn.close()
        return trial_id
    
    def get_session_stats(self, session_id):
        """Get accuracy, confusion matrix for a session"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT true_label, predicted_label FROM trials WHERE session_id = ?',
                 (session_id,))
        results = c.fetchall()
        conn.close()
        
        if not results:
            return {'accuracy': 0, 'total_trials': 0}
        
        correct = sum(1 for true, pred in results if true == pred)
        accuracy = correct / len(results)
        
        return {
            'accuracy': round(accuracy, 3),
            'total_trials': len(results),
            'correct': correct
        }

# Global DB instance
db = Database()