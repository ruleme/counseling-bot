"""Persistent pseudonymous aliases; existing aliases remain unchanged."""
import secrets
import sqlite3
from contextlib import closing
import config
from database import Database

db = Database()


def generate_anonymous_id():
    return config.ANONYMOUS_ID_PREFIX + secrets.token_hex(6).upper()


def get_or_create_anonymous_id(telegram_id):
    with closing(db.get_connection()) as conn, conn:
        for _ in range(10):
            existing = conn.execute("SELECT anonymous_id FROM users WHERE telegram_id=?", (telegram_id,)).fetchone()
            if existing:
                return existing[0]
            alias = generate_anonymous_id()
            try:
                conn.execute("INSERT INTO users(telegram_id,anonymous_id) VALUES (?,?)", (telegram_id,alias))
                return alias
            except sqlite3.IntegrityError:
                continue
    raise RuntimeError("Unable to allocate anonymous alias")
