"""
Utility functions for anonymous ID generation and management.
"""

import random
import string
import config
from database import Database

db = Database()


def generate_anonymous_id() -> str:
    """
    Generate a unique anonymous ID for a user.
    Format: User-XXXX where XXXX is a random 4-digit number.
    """
    while True:
        # Generate random 4-digit number
        random_number = random.randint(1000, 9999)
        anonymous_id = f"{config.ANONYMOUS_ID_PREFIX}{random_number}"
        
        # Check if ID already exists
        if db.get_user_telegram_id(anonymous_id) is None:
            return anonymous_id


def get_or_create_anonymous_id(telegram_id: int) -> str:
    """
    Get existing anonymous ID for a user or create a new one.
    Returns the anonymous ID.
    """
    anonymous_id = db.get_user_anonymous_id(telegram_id)
    if anonymous_id is None:
        anonymous_id = generate_anonymous_id()
        db.create_user(telegram_id, anonymous_id)
    return anonymous_id

