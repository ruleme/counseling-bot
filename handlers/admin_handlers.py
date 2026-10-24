"""
Admin handlers for the Anonymous Telegram Counseling Bot.
Handles admin panel and administrative functions.
"""

import logging
import json
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from contextlib import closing

from database import Database
from keyboards.menus import get_admin_menu_keyboard
import config

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class AdminStates(StatesGroup):
    """FSM states for admin interactions."""
    adding_counselor = State()
    removing_counselor = State()
    blocking_user = State()
    assigning_categories = State()


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == config.ADMIN_ID


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Handle /admin command - show admin panel."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ You are not authorized as an administrator.")
        return
    
    # Get statistics
    all_sessions = db.get_all_active_sessions()
    all_counselors = db.get_all_counselors()
    
    stats_text = (
        f"👑 Admin Panel\n\n"
        f"📊 Statistics:\n"
        f"• Active Sessions: {len(all_sessions)}\n"
        f"• Total Counselors: {len(all_counselors)}\n\n"
        f"Use the menu below to manage the bot."
    )
    
    await message.answer(stats_text, reply_markup=get_admin_menu_keyboard())
    await state.clear()


@router.message(F.text == "👥 Manage Counselors")
async def manage_counselors(message: Message):
    """Show counselor management options."""
    if not is_admin(message.from_user.id):
        return
    
    counselors = db.get_all_counselors()
    
    if not counselors:
        await message.answer(
            "👥 Manage Counselors\n\n"
            "No counselors registered.\n\n"
            "To add a counselor, send:\n"
            "/add_counselor <telegram_id> <category1,category2,...>\n\n"
            "Example: /add_counselor 123456789 mental_health,stress"
        )
        return
    
    counselors_text = "👥 Registered Counselors:\n\n"
    for counselor in counselors:
        status = "✅ Active" if counselor["is_active"] else "❌ Inactive"
        counselors_text += (
            f"• ID: {counselor['telegram_id']}\n"
            f"  Categories: {', '.join(counselor['categories'])}\n"
            f"  Status: {status}\n\n"
        )
    
    counselors_text += (
        "\nCommands:\n"
        "/add_counselor <id> <categories> - Add counselor\n"
        "/remove_counselor <id> - Remove counselor"
    )
    
    await message.answer(counselors_text)


@router.message(Command("add_counselor"))
async def cmd_add_counselor(message: Message):
    """Add a new counselor."""
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()[1:]
        if len(parts) < 2:
            await message.answer(
                "❌ Usage: /add_counselor <telegram_id> <category1,category2,...>\n"
                "Example: /add_counselor 123456789 mental_health,stress"
            )
            return
        
        counselor_id = int(parts[0])
        categories = [cat.strip() for cat in ",".join(parts[1:]).split(",")]
        
        # Validate categories
        valid_categories = list(config.ISSUE_CATEGORIES.keys())
        invalid_categories = [cat for cat in categories if cat not in valid_categories]
        
        if invalid_categories:
            await message.answer(
                f"❌ Invalid categories: {', '.join(invalid_categories)}\n"
                f"Valid categories: {', '.join(valid_categories)}"
            )
            return
        
        # Add counselor
        if db.add_counselor(counselor_id, categories):
            await message.answer(
                f"✅ Counselor {counselor_id} added successfully.\n"
                f"Categories: {', '.join(categories)}"
            )
        else:
            await message.answer("❌ Error adding counselor.")
    except (ValueError, TypeError):
        await message.answer("❌ Invalid counselor ID. Must be a number.")


@router.message(Command("remove_counselor"))
async def cmd_remove_counselor(message: Message):
    """Remove a counselor."""
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Usage: /remove_counselor <telegram_id>")
            return
        
        counselor_id = int(parts[1])
        
        if db.remove_counselor(counselor_id):
            await message.answer(f"✅ Counselor {counselor_id} removed successfully.")
        else:
            await message.answer("❌ Error removing counselor.")
    except (ValueError, TypeError):
        await message.answer("❌ Invalid counselor ID. Must be a number.")


@router.message(F.text == "📊 Active Sessions")
async def show_active_sessions(message: Message):
    """Show all active sessions."""
    if not is_admin(message.from_user.id):
        return
    
    sessions = db.get_all_active_sessions()
    
    if not sessions:
        await message.answer("📭 No active sessions.")
        return
    
    sessions_text = "📊 Active Sessions:\n\n"
    for session in sessions:
        user_anonymous_id = db.get_user_anonymous_id(session["user_telegram_id"])
        category = config.ISSUE_CATEGORIES.get(session["category"], {"en": session["category"]})["en"]
        sessions_text += (
            f"• Session ID: {session['session_id']}\n"
            f"  User: {user_anonymous_id} (ID: {session['user_telegram_id']})\n"
            f"  Counselor: {session['counselor_telegram_id']}\n"
            f"  Category: {category}\n"
            f"  Started: {session['created_at']}\n\n"
        )
    
    await message.answer(sessions_text)


@router.message(F.text == "🚫 Block User")
async def start_block_user(message: Message, state: FSMContext):
    """Start blocking a user."""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🚫 Block User\n\n"
        "Send the Telegram ID of the user you want to block.\n"
        "Or send /cancel to cancel."
    )
    await state.set_state(AdminStates.blocking_user)


@router.message(StateFilter(AdminStates.blocking_user), ~F.text.startswith("/"))
async def handle_block_user(message: Message, state: FSMContext):
    """Handle blocking a user."""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    try:
        user_id = int(message.text or "")
        
        if db.block_user(user_id):
            await message.answer(f"✅ User {user_id} has been blocked.")
        else:
            await message.answer("❌ Error blocking user.")
    except (ValueError, TypeError):
        await message.answer("❌ Invalid user ID. Must be a number.")
    
    await state.clear()


@router.message(Command("unblock_user"))
async def cmd_unblock_user(message: Message):
    """Unblock a user."""
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Usage: /unblock_user <telegram_id>")
            return
        
        user_id = int(parts[1])
        
        if db.unblock_user(user_id):
            await message.answer(f"✅ User {user_id} has been unblocked.")
        else:
            await message.answer("❌ Error unblocking user.")
    except (ValueError, TypeError):
        await message.answer("❌ Invalid user ID. Must be a number.")


@router.message(Command("force_end"))
async def cmd_force_end(message: Message):
    """Force end a session (admin only)."""
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ Usage: /force_end <user_telegram_id>\nExample: /force_end 123456789")
            return
        
        user_id = int(parts[1])
        active_session = db.get_active_session(user_id)
        
        if not active_session:
            await message.answer(f"❌ User {user_id} doesn't have an active session.")
            return
        
        # Force end the session
        result = db.finish_session(active_session["session_id"])
        if result:
            await message.answer(f"✅ Session {active_session['session_id']} has been force-ended for user {user_id}.")
        else:
            await message.answer(f"❌ Failed to end session for user {user_id}.")
    except (ValueError, TypeError):
        await message.answer("❌ Invalid user ID. Must be a number.")
    except Exception as e:
        logger.error(f"Error in force_end: {e}")
        await message.answer("❌ Operation failed. Please try again.")


@router.message(F.text == "📥 Export Logs")
async def export_logs(message: Message):
    """Export chat logs."""
    if not is_admin(message.from_user.id):
        return
    
    try:
        # Get all finished sessions
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT session_id, user_telegram_id, counselor_telegram_id, category, 
                      created_at, finished_at
               FROM chat_sessions 
               WHERE status = 'finished'
               ORDER BY finished_at DESC
               LIMIT 100"""
        )
        sessions = cursor.fetchall()
        
        logs = []
        for session in sessions:
            session_id = session[0]
            user_anonymous_id = db.get_user_anonymous_id(session[1])
            
            # Get messages for this session
            messages = db.get_session_messages(session_id)
            
            session_log = {
                "session_id": session_id,
                "user_anonymous_id": user_anonymous_id,
                "identity_redacted": True,
                
                "category": session[3],
                "created_at": session[4],
                "finished_at": session[5],
                "messages": [
                    {
                        "sender_role": "user" if msg["sender_telegram_id"] == session[1] else "counselor",
                        "message_type": msg["message_type"],
                        "content": msg["content"],
                        
                        "sent_at": msg["sent_at"]
                    }
                    for msg in messages
                ]
            }
            logs.append(session_log)
        
        conn.close()
        
        # Create JSON export
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_sessions": len(logs),
            "sessions": logs
        }
        
        export_text = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Send only to the configured admin, without HTML or disk transcripts.
        await message.bot.send_document(
            config.ADMIN_ID,
            BufferedInputFile(export_text.encode("utf-8"), filename="counseling_logs.json"),
            caption=f"Chat logs export: {len(logs)} sessions. Treat transcripts as sensitive."
        )
    except Exception:
        logger.exception("Error exporting logs")
        await message.answer("❌ Error exporting logs.")
