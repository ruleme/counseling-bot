"""
Counselor handlers for the Anonymous Telegram Counseling Bot.
Handles counselor panel and interactions.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from keyboards.menus import get_counselor_menu_keyboard, get_session_keyboard
import config

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class CounselorStates(StatesGroup):
    """FSM states for counselor interactions."""
    waiting_for_reply = State()
    selecting_session = State()


@router.message(Command("counselor"))
async def cmd_counselor(message: Message, state: FSMContext):
    """Handle /counselor command - show counselor panel."""
    counselor_id = message.from_user.id
    
    if not db.is_counselor(counselor_id):
        await message.answer("❌ You are not authorized as a counselor.")
        return
    
    # Get active sessions
    active_sessions = db.get_counselor_sessions(counselor_id, status="active")
    
    if not active_sessions:
        await message.answer(
            "👋 Counselor Panel\n\n"
            "You currently have no active sessions.\n\n"
            "Use the menu below to manage your sessions.",
            reply_markup=get_counselor_menu_keyboard()
        )
    else:
        sessions_text = "📋 Your Active Sessions:\n\n"
        for session in active_sessions:
            anonymous_id = db.get_user_anonymous_id(session["user_telegram_id"])
            category = config.ISSUE_CATEGORIES.get(session["category"], session["category"])
            sessions_text += (
                f"• {anonymous_id} - {category}\n"
                f"  Session ID: {session['session_id']}\n\n"
            )
        
        await message.answer(
            sessions_text + "Use the menu below to manage your sessions.",
            reply_markup=get_counselor_menu_keyboard()
        )
    
    await state.clear()


@router.message(F.text == "📋 My Sessions")
async def show_sessions(message: Message):
    """Show all active sessions for the counselor."""
    counselor_id = message.from_user.id
    
    if not db.is_counselor(counselor_id):
        await message.answer("❌ You are not authorized as a counselor.")
        return
    
    active_sessions = db.get_counselor_sessions(counselor_id, status="active")
    
    if not active_sessions:
        await message.answer("📭 You have no active sessions.")
        return
    
    sessions_text = "📋 Your Active Sessions:\n\n"
    for session in active_sessions:
        anonymous_id = db.get_user_anonymous_id(session["user_telegram_id"])
        category = config.ISSUE_CATEGORIES.get(session["category"], session["category"])
        sessions_text += (
            f"• {anonymous_id} - {category}\n"
            f"  Session ID: {session['session_id']}\n"
            f"  Started: {session['created_at']}\n\n"
        )
    
    await message.answer(sessions_text)


@router.message(F.text == "💬 Reply to User")
async def start_reply(message: Message, state: FSMContext):
    """Start replying to a user."""
    counselor_id = message.from_user.id
    
    if not db.is_counselor(counselor_id):
        await message.answer("❌ You are not authorized as a counselor.")
        return
    
    active_sessions = db.get_counselor_sessions(counselor_id, status="active")
    
    if not active_sessions:
        await message.answer("❌ You have no active sessions to reply to.")
        return
    
    # Show sessions to choose from
    sessions_text = "Select a session to reply to:\n\n"
    for idx, session in enumerate(active_sessions, 1):
        anonymous_id = db.get_user_anonymous_id(session["user_telegram_id"])
        category = config.ISSUE_CATEGORIES.get(session["category"], session["category"])
        sessions_text += f"{idx}. {anonymous_id} - {category} (ID: {session['session_id']})\n"
    
    await message.answer(
        sessions_text + "\nPlease send the session ID you want to reply to:"
    )
    await state.set_state(CounselorStates.selecting_session)


@router.message(StateFilter(CounselorStates.selecting_session))
async def handle_session_selection(message: Message, state: FSMContext):
    """Handle session selection for replying."""
    counselor_id = message.from_user.id
    
    try:
        session_id = int(message.text)
    except ValueError:
        await message.answer("❌ Invalid session ID. Please send a number.")
        return
    
    session = db.get_session_by_id(session_id)
    
    if not session or session["counselor_telegram_id"] != counselor_id:
        await message.answer("❌ Session not found or you don't have access to it.")
        await state.clear()
        return
    
    if session["status"] != "active":
        await message.answer("❌ This session is not active.")
        await state.clear()
        return
    
    anonymous_id = db.get_user_anonymous_id(session["user_telegram_id"])
    await state.update_data(session_id=session_id, user_id=session["user_telegram_id"])
    
    await message.answer(
        f"💬 Replying to {anonymous_id}\n\n"
        f"Send your message. Type /cancel to cancel."
    )
    await state.set_state(CounselorStates.waiting_for_reply)


@router.message(StateFilter(CounselorStates.waiting_for_reply))
async def handle_counselor_reply(message: Message, state: FSMContext):
    """Handle counselor's reply message."""
    counselor_id = message.from_user.id
    data = await state.get_data()
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    
    if not session_id or not user_id:
        await message.answer("❌ Session data lost. Please try again.")
        await state.clear()
        return
    
    session = db.get_session_by_id(session_id)
    if not session or session["counselor_telegram_id"] != counselor_id:
        await message.answer("❌ Session not found.")
        await state.clear()
        return
    
    anonymous_id = db.get_user_anonymous_id(user_id)
    
    # Save message to database
    message_type = "text"
    content = message.text
    file_id = None
    
    if message.photo:
        message_type = "photo"
        content = message.caption or ""
        file_id = message.photo[-1].file_id
    elif message.voice:
        message_type = "voice"
        content = ""
        file_id = message.voice.file_id
    elif message.video:
        message_type = "video"
        content = message.caption or ""
        file_id = message.video.file_id
    elif message.document:
        message_type = "document"
        content = message.caption or ""
        file_id = message.document.file_id
    
    db.save_message(session_id, counselor_id, message_type, content, file_id)
    
    # Forward message to user
    try:
        from bot_instance import get_bot
        bot = get_bot()
        
        if message_type == "text":
            await bot.send_message(
                user_id,
                f"💬 Message from your counselor:\n\n{content}"
            )
        elif message_type == "photo":
            await bot.send_photo(
                user_id,
                file_id,
                caption=f"📷 Photo from your counselor" + (f":\n{content}" if content else "")
            )
        elif message_type == "voice":
            await bot.send_voice(
                user_id,
                file_id,
                caption=f"🎤 Voice message from your counselor"
            )
        elif message_type == "video":
            await bot.send_video(
                user_id,
                file_id,
                caption=f"🎥 Video from your counselor" + (f":\n{content}" if content else "")
            )
        elif message_type == "document":
            await bot.send_document(
                user_id,
                file_id,
                caption=f"📄 Document from your counselor" + (f":\n{content}" if content else "")
            )
        
        await message.answer(f"✅ Message sent to {anonymous_id}")
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")
        error_msg = f"❌ Error sending message: {str(e)}\n\n"
        if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
            error_msg += "⚠️ The user hasn't started the bot yet or has blocked it."
        await message.answer(error_msg)
    
    await state.clear()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation."""
    await state.clear()
    await message.answer("❌ Operation cancelled.")


@router.message(F.text == "✅ Finish Session")
async def finish_session(message: Message):
    """Finish a session."""
    counselor_id = message.from_user.id
    
    if not db.is_counselor(counselor_id):
        await message.answer("❌ You are not authorized as a counselor.")
        return
    
    active_sessions = db.get_counselor_sessions(counselor_id, status="active")
    
    if not active_sessions:
        await message.answer("❌ You have no active sessions.")
        return
    
    # Show sessions to choose from
    sessions_text = "Select a session to finish:\n\n"
    for idx, session in enumerate(active_sessions, 1):
        anonymous_id = db.get_user_anonymous_id(session["user_telegram_id"])
        category = config.ISSUE_CATEGORIES.get(session["category"], session["category"])
        sessions_text += f"{idx}. {anonymous_id} - {category} (ID: {session['session_id']})\n"
    
    await message.answer(
        sessions_text + "\nPlease send the session ID you want to finish:"
    )


@router.message(lambda m: m.text and m.text.isdigit() and db.is_counselor(m.from_user.id))
async def handle_finish_session_id(message: Message):
    """Handle finishing a session by ID."""
    counselor_id = message.from_user.id
    
    try:
        session_id = int(message.text)
    except ValueError:
        return  # Not a session ID, ignore
    
    session = db.get_session_by_id(session_id)
    
    if not session or session["counselor_telegram_id"] != counselor_id:
        return  # Not a valid session for this counselor
    
    if session["status"] != "active":
        await message.answer("❌ This session is not active.")
        return
    
    # Finish session
    db.finish_session(session_id)
    
    # Notify user
    try:
        from bot_instance import get_bot
        bot = get_bot()
        anonymous_id = db.get_user_anonymous_id(session["user_telegram_id"])
        await bot.send_message(
            session["user_telegram_id"],
            f"ℹ️ Your counseling session has been finished by the counselor.\n\n"
            f"Thank you for using our service. Type /start to begin a new session."
        )
    except Exception as e:
        logger.error(f"Error notifying user: {e}")
    
    await message.answer("✅ Session finished successfully.")

