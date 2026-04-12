import sqlite3
import os
from utils import logger

# Use Railway Volume path if it exists, otherwise use local path
if os.path.exists("/data"):
    DB_PATH = "/data/bot_memory.db"
else:
    DB_PATH = "bot_memory.db"

def init_db():
    """Initializes the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_tracking (
            email TEXT PRIMARY KEY,
            message_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Bot memory database initialized.")

def save_message_tracking(email: str, message_id: int):
    """Saves client email linked to a telegram message ID."""
    try:
        email_clean = email.strip().lower()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO message_tracking (email, message_id)
            VALUES (?, ?)
        ''', (email_clean, message_id))
        conn.commit()
        conn.close()
        logger.info(f"Memory: Saved message {message_id} for client {email_clean}")
        return True
    except Exception as e:
        logger.error(f"Memory Error (save): {e}")
        return False

def get_message_tracking(email: str):
    """Retrieves the telegram message ID linked to a client email."""
    try:
        email_clean = email.strip().lower()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT message_id FROM message_tracking WHERE email = ?', (email_clean,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Memory Error (get): {e}")
        return None

# Initialize on import
init_db()
