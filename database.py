"""
Database module for the Anonymous Telegram Counseling Bot.
Handles all SQLite database operations.
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class Database:
    """Database handler for storing users, counselors, chats, and sessions."""
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Create all necessary tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table - stores Telegram users with their anonymous IDs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                anonymous_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked INTEGER DEFAULT 0
            )
        """)
        
        # Counselors table - stores counselor information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS counselors (
                telegram_id INTEGER PRIMARY KEY,
                categories TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chat sessions table - stores active chat sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER NOT NULL,
                counselor_telegram_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP,
                FOREIGN KEY (user_telegram_id) REFERENCES users(telegram_id),
                FOREIGN KEY (counselor_telegram_id) REFERENCES counselors(telegram_id)
            )
        """)
        
        # Messages table - stores all messages in chat sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                sender_telegram_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT,
                file_id TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    # User operations
    def create_user(self, telegram_id: int, anonymous_id: str) -> bool:
        """Create a new user with an anonymous ID."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (telegram_id, anonymous_id) VALUES (?, ?)",
                (telegram_id, anonymous_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
    
    def get_user_anonymous_id(self, telegram_id: int) -> Optional[str]:
        """Get anonymous ID for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT anonymous_id FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_user_telegram_id(self, anonymous_id: str) -> Optional[int]:
        """Get Telegram ID from anonymous ID (admin only)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id FROM users WHERE anonymous_id = ?", (anonymous_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def block_user(self, telegram_id: int) -> bool:
        """Block a user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_blocked = 1 WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error blocking user: {e}")
            return False
    
    def unblock_user(self, telegram_id: int) -> bool:
        """Unblock a user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_blocked = 0 WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error unblocking user: {e}")
            return False
    
    def is_user_blocked(self, telegram_id: int) -> bool:
        """Check if a user is blocked."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_blocked FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] == 1 if result else False
    
    # Counselor operations
    def add_counselor(self, telegram_id: int, categories: List[str]) -> bool:
        """Add a counselor with their categories."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            categories_str = ",".join(categories)
            cursor.execute(
                "INSERT OR REPLACE INTO counselors (telegram_id, categories) VALUES (?, ?)",
                (telegram_id, categories_str)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding counselor: {e}")
            return False
    
    def remove_counselor(self, telegram_id: int) -> bool:
        """Remove a counselor."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM counselors WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error removing counselor: {e}")
            return False
    
    def get_counselors_by_category(self, category: str) -> List[int]:
        """Get all active counselors for a specific category."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT telegram_id FROM counselors WHERE is_active = 1 AND categories LIKE ?",
            (f"%{category}%",)
        )
        results = cursor.fetchall()
        conn.close()
        return [row[0] for row in results]
    
    def is_counselor(self, telegram_id: int) -> bool:
        """Check if a user is a counselor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM counselors WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0 if result else False
    
    def get_all_counselors(self) -> List[Dict]:
        """Get all counselors (admin only)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id, categories, is_active FROM counselors")
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "telegram_id": row[0],
                "categories": row[1].split(","),
                "is_active": bool(row[2])
            }
            for row in results
        ]
    
    # Chat session operations
    def create_chat_session(self, user_telegram_id: int, counselor_telegram_id: int, category: str) -> Optional[int]:
        """Create a new chat session and return session_id."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO chat_sessions 
                   (user_telegram_id, counselor_telegram_id, category, status)
                   VALUES (?, ?, ?, 'active')""",
                (user_telegram_id, counselor_telegram_id, category)
            )
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return None
    
    def get_active_session(self, user_telegram_id: int) -> Optional[Dict]:
        """Get active session for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT session_id, user_telegram_id, counselor_telegram_id, category
               FROM chat_sessions 
               WHERE user_telegram_id = ? AND status = 'active'
               ORDER BY created_at DESC LIMIT 1""",
            (user_telegram_id,)
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "session_id": result[0],
                "user_telegram_id": result[1],
                "counselor_telegram_id": result[2],
                "category": result[3]
            }
        return None
    
    def get_counselor_sessions(self, counselor_telegram_id: int, status: str = "active") -> List[Dict]:
        """Get all sessions for a counselor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT session_id, user_telegram_id, category, created_at
               FROM chat_sessions 
               WHERE counselor_telegram_id = ? AND status = ?
               ORDER BY created_at DESC""",
            (counselor_telegram_id, status)
        )
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "session_id": row[0],
                "user_telegram_id": row[1],
                "category": row[2],
                "created_at": row[3]
            }
            for row in results
        ]
    
    def finish_session(self, session_id: int) -> bool:
        """Mark a session as finished."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chat_sessions SET status = 'finished', finished_at = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error finishing session: {e}")
            return False
    
    def get_session_by_id(self, session_id: int) -> Optional[Dict]:
        """Get session details by session_id."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT session_id, user_telegram_id, counselor_telegram_id, category, status
               FROM chat_sessions WHERE session_id = ?""",
            (session_id,)
        )
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                "session_id": result[0],
                "user_telegram_id": result[1],
                "counselor_telegram_id": result[2],
                "category": result[3],
                "status": result[4]
            }
        return None
    
    def get_all_active_sessions(self) -> List[Dict]:
        """Get all active sessions (admin only)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT session_id, user_telegram_id, counselor_telegram_id, category, created_at
               FROM chat_sessions WHERE status = 'active' ORDER BY created_at DESC"""
        )
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "session_id": row[0],
                "user_telegram_id": row[1],
                "counselor_telegram_id": row[2],
                "category": row[3],
                "created_at": row[4]
            }
            for row in results
        ]
    
    # Message operations
    def save_message(self, session_id: int, sender_telegram_id: int, message_type: str, content: str = None, file_id: str = None) -> bool:
        """Save a message to the database."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO messages (session_id, sender_telegram_id, message_type, content, file_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, sender_telegram_id, message_type, content, file_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False
    
    def get_session_messages(self, session_id: int) -> List[Dict]:
        """Get all messages for a session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT sender_telegram_id, message_type, content, file_id, sent_at
               FROM messages WHERE session_id = ? ORDER BY sent_at ASC""",
            (session_id,)
        )
        results = cursor.fetchall()
        conn.close()
        return [
            {
                "sender_telegram_id": row[0],
                "message_type": row[1],
                "content": row[2],
                "file_id": row[3],
                "sent_at": row[4]
            }
            for row in results
        ]

