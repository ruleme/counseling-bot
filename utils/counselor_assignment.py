"""
Utility functions for counselor assignment logic.
Implements round-robin and random assignment strategies.
"""

import random
from typing import Optional, List
from database import Database
import config

db = Database()


def assign_counselor(category: str, assignment_method: str = "round_robin") -> Optional[int]:
    """
    Assign a counselor to a user based on category.
    
    Args:
        category: The issue category
        assignment_method: "round_robin" or "random"
    
    Returns:
        Counselor Telegram ID or None if no counselor available
    """
    # Get counselors from database first
    counselor_ids = db.get_counselors_by_category(category)
    
    # If no counselors in database, check config
    if not counselor_ids:
        counselor_ids = config.COUNSELOR_CATEGORIES.get(category, [])
    
    if not counselor_ids:
        return None
    
    if assignment_method == "random":
        return random.choice(counselor_ids)
    else:  # round_robin
        # Simple round-robin: get active sessions for this category
        # and assign to counselor with least active sessions
        active_sessions = db.get_all_active_sessions()
        category_sessions = [s for s in active_sessions if s["category"] == category]
        
        # Count sessions per counselor
        counselor_session_count = {}
        for counselor_id in counselor_ids:
            counselor_session_count[counselor_id] = sum(
                1 for s in category_sessions if s["counselor_telegram_id"] == counselor_id
            )
        
        # Return counselor with least sessions
        return min(counselor_ids, key=lambda cid: counselor_session_count.get(cid, 0))

