"""
Database module for the Anonymous Telegram Counseling Bot.
Handles all SQLite database operations.
"""

import sqlite3
from pathlib import Path
from contextlib import closing
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class Database:
    """Database handler for storing users, counselors, chats, and sessions."""
    
    def __init__(self, db_path=None):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = str(db_path if db_path is not None else config.DATABASE_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
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
        
        message_columns = {row[1] for row in cursor.execute("PRAGMA table_info(messages)")}
        if "delivery_status" not in message_columns:
            cursor.execute("ALTER TABLE messages ADD COLUMN delivery_status TEXT DEFAULT 'unknown'")
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)")}
        if "language" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
        if cursor.execute("SELECT 1 FROM chat_sessions WHERE status='active' GROUP BY user_telegram_id HAVING COUNT(*)>1").fetchone():
            conn.close()
            raise RuntimeError("Duplicate active sessions: back up and resolve before startup")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_active_session_per_user ON chat_sessions(user_telegram_id) WHERE status='active'")
        cursor.execute("CREATE INDEX IF NOT EXISTS sessions_counselor_status ON chat_sessions(counselor_telegram_id,status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS messages_session ON messages(session_id,message_id)")
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
    
    def block_user(self, telegram_id):
        with closing(self.get_connection()) as conn, conn:
            result = conn.execute("UPDATE users SET is_blocked=1 WHERE telegram_id=?", (telegram_id,))
            conn.execute("UPDATE chat_sessions SET status='finished', finished_at=CURRENT_TIMESTAMP WHERE user_telegram_id=? AND status='active'", (telegram_id,))
            return result.rowcount > 0

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
                "INSERT INTO counselors (telegram_id, categories) VALUES (?, ?) ON CONFLICT(telegram_id) DO UPDATE SET categories=excluded.categories, is_active=1",
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
            cursor.execute("UPDATE counselors SET is_active=0 WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error removing counselor: {e}")
            return False
    
    def get_counselors_by_category(self, category):
        with closing(self.get_connection()) as conn:
            return [row[0] for row in conn.execute("SELECT telegram_id,categories FROM counselors WHERE is_active=1")
                    if category in row[1].split(",")]

    def is_counselor(self, telegram_id: int) -> bool:
        """Check if a user is a counselor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM counselors WHERE telegram_id = ? AND is_active=1", (telegram_id,))
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
    def create_chat_session(self, user_telegram_id, counselor_telegram_id, category):
        try:
            with closing(self.get_connection()) as conn, conn:
                conn.execute("BEGIN IMMEDIATE")
                user = conn.execute("SELECT is_blocked FROM users WHERE telegram_id=?", (user_telegram_id,)).fetchone()
                counselor = conn.execute("SELECT categories FROM counselors WHERE telegram_id=? AND is_active=1", (counselor_telegram_id,)).fetchone()
                if not user or user[0] or not counselor or category not in counselor[0].split(','):
                    return None
                cursor = conn.execute("INSERT INTO chat_sessions(user_telegram_id,counselor_telegram_id,category,status) VALUES (?,?,?,'active')", (user_telegram_id,counselor_telegram_id,category))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
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
    
    def finish_session(self, session_id):
        with closing(self.get_connection()) as conn, conn:
            return conn.execute("UPDATE chat_sessions SET status='finished',finished_at=CURRENT_TIMESTAMP WHERE session_id=? AND status='active'", (session_id,)).rowcount > 0

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
    def save_message(self, session_id, sender_telegram_id, message_type, content=None, file_id=None):
        try:
            with closing(self.get_connection()) as conn, conn:
                cursor = conn.execute("INSERT INTO messages(session_id,sender_telegram_id,message_type,content,file_id,delivery_status) VALUES (?,?,?,?,?,'pending')",
                                      (session_id,sender_telegram_id,message_type,content,file_id))
                return cursor.lastrowid
        except sqlite3.Error:
            logger.error("Unable to persist message")
            return None

    def get_session_messages(self, session_id: int) -> List[Dict]:
        """Get all messages for a session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT sender_telegram_id, message_type, content, file_id, sent_at
               FROM messages WHERE session_id = ? ORDER BY message_id ASC""",
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


    def get_language(self, telegram_id):
        with closing(self.get_connection()) as conn:
            row = conn.execute("SELECT language FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
            return row[0] if row and row[0] in ('en','am') else 'en'

    def set_language(self, telegram_id, language):
        if language not in ('en','am'):
            raise ValueError("Unsupported language")
        with closing(self.get_connection()) as conn, conn:
            conn.execute("UPDATE users SET language=? WHERE telegram_id=?", (language,telegram_id))

    def can_reply(self, session_id, counselor_id):
        with closing(self.get_connection()) as conn:
            return bool(conn.execute("SELECT 1 FROM chat_sessions s JOIN counselors c ON c.telegram_id=s.counselor_telegram_id JOIN users u ON u.telegram_id=s.user_telegram_id WHERE s.session_id=? AND c.telegram_id=? AND c.is_active=1 AND s.status='active' AND u.is_blocked=0", (session_id,counselor_id)).fetchone())

    def set_delivery_status(self, message_id, status):
        if status not in ("delivered", "failed"):
            raise ValueError("Invalid delivery status")
        with closing(self.get_connection()) as conn, conn:
            conn.execute("UPDATE messages SET delivery_status=? WHERE message_id=?", (status,message_id))
