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
from utils.relay import payload, deliver
from keyboards.menus import get_counselor_menu_keyboard, get_session_keyboard
import config

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class CounselorStates(StatesGroup):
    """FSM states for counselor interactions."""
    waiting_for_reply = State()
    selecting_session = State()
    selecting_finish = State()


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
            category = config.ISSUE_CATEGORIES.get(session["category"], {"en": session["category"]})["en"]
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
        category = config.ISSUE_CATEGORIES.get(session["category"], {"en": session["category"]})["en"]
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
        category = config.ISSUE_CATEGORIES.get(session["category"], {"en": session["category"]})["en"]
        sessions_text += f"{idx}. {anonymous_id} - {category} (ID: {session['session_id']})\n"
    
    await message.answer(
        sessions_text + "\nPlease send the session ID you want to reply to:"
    )
    await state.set_state(CounselorStates.selecting_session)


@router.message(StateFilter(CounselorStates.selecting_session), ~F.text.startswith("/"))
async def handle_session_selection(message: Message, state: FSMContext):
    """Handle session selection for replying."""
    counselor_id = message.from_user.id
    
    try:
        session_id = int(message.text or "")
    except (ValueError, TypeError):
        await message.answer("❌ Invalid session ID. Please send a number.")
        return
    
    session = db.get_session_by_id(session_id)
    
    if not session or not db.can_reply(session_id, counselor_id):
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
        f"Send your messages. Type /cancel to stop replying."
    )
    await state.set_state(CounselorStates.waiting_for_reply)


@router.message(StateFilter(CounselorStates.waiting_for_reply), ~F.text.startswith("/"))
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
    if not session or not db.can_reply(session_id, counselor_id):
        await message.answer("❌ Session not found.")
        await state.clear()
        return
    
    anonymous_id = db.get_user_anonymous_id(user_id)
    
    item = payload(message)
    if item is None:
        await message.answer("Please send text, a photo, voice, video or document. / ጽሑፍ፣ ፎቶ፣ ድምጽ፣ ቪዲዮ ወይም ሰነድ ይላኩ።")
        return
    message_type, content, file_id = item
    message_id = db.save_message(session_id, counselor_id, message_type, content, file_id)
    if not message_id:
        await message.answer("Unable to save message. Please try again.")
        return
    try:
        from bot_instance import get_bot
        bot = get_bot()
        await deliver(bot, user_id, "Message from your counselor", item)
        db.set_delivery_status(message_id, "delivered")
    except Exception as e:
        db.set_delivery_status(message_id, "failed")
        logger.error("Telegram delivery failed (%s)", type(e).__name__)
        error_msg = "❌ Message delivery failed. Please try again.\n\n"
        if "chat not found" in str(e).lower() or "blocked" in str(e).lower():
            error_msg += "⚠️ The user hasn't started the bot yet or has blocked it."
        await message.answer(error_msg)
        return
    await message.answer(f"✅ Sent to {anonymous_id}. Continue here or /cancel to switch.")
    
    # Keep selected conversation until cancelled or switched.


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel current operation."""
    await state.clear()
    await message.answer("❌ Operation cancelled.")


@router.message(F.text == "✅ Finish Session")
async def finish_session(message: Message, state: FSMContext):
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
        category = config.ISSUE_CATEGORIES.get(session["category"], {"en": session["category"]})["en"]
        sessions_text += f"{idx}. {anonymous_id} - {category} (ID: {session['session_id']})\n"
    
    await message.answer(
        sessions_text + "\nPlease send the session ID you want to finish:"
    )
    await state.set_state(CounselorStates.selecting_finish)


@router.message(StateFilter(CounselorStates.selecting_finish), ~F.text.startswith("/"))
async def handle_finish_session_id(message: Message, state: FSMContext):
    """Handle finishing a session by ID."""
    counselor_id = message.from_user.id
    
    try:
        session_id = int(message.text or "")
    except (ValueError, TypeError):
        return  # Not a session ID, ignore
    
    session = db.get_session_by_id(session_id)
    
    if not session or not db.can_reply(session_id, counselor_id):
        return  # Not a valid session for this counselor
    
    if session["status"] != "active":
        await message.answer("❌ This session is not active.")
        return
    
    await state.clear()
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



@router.callback_query(F.data.startswith("reply_"))
async def select_reply_button(callback: CallbackQuery, state: FSMContext):
    if not callback.message or callback.message.chat.type != "private":
        await callback.answer("Open the bot privately.")
        return
    try:
        session_id = int(callback.data.split("_", 1)[1])
    except (ValueError, TypeError):
        await callback.answer("Invalid session.")
        return
    if not db.can_reply(session_id, callback.from_user.id):
        await callback.answer("Session ended or access unavailable.")
        return
    session = db.get_session_by_id(session_id)
    await state.update_data(session_id=session_id, user_id=session["user_telegram_id"])
    await state.set_state(CounselorStates.waiting_for_reply)
    alias = db.get_user_anonymous_id(session["user_telegram_id"])
    await callback.answer()
    await callback.message.answer(f"Replying to {alias}. Send messages here. Use /cancel to stop or tap Reply on another conversation.")


@router.callback_query(F.data.startswith("finish_"))
async def confirm_finish_button(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    if not callback.message or callback.message.chat.type != "private":
        await callback.answer("Open the bot privately.")
        return
    try:
        session_id = int(callback.data.split("_", 1)[1])
    except (ValueError, TypeError):
        await callback.answer("Invalid session.")
        return
    if not db.can_reply(session_id, callback.from_user.id):
        await callback.answer("Session ended or access unavailable.")
        return
    session = db.get_session_by_id(session_id)
    alias = db.get_user_anonymous_id(session["user_telegram_id"])
    await callback.answer()
    await callback.message.answer(
        f"End the conversation with {alias}?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Confirm end session", callback_data=f"endconfirm_{session_id}")
        ]])
    )


@router.callback_query(F.data.startswith("endconfirm_"))
async def finish_button(callback: CallbackQuery, state: FSMContext):
    if not callback.message or callback.message.chat.type != "private":
        await callback.answer("Open the bot privately.")
        return
    try:
        session_id = int(callback.data.split("_", 1)[1])
    except (ValueError, TypeError):
        await callback.answer("Invalid session.")
        return
    if not db.can_reply(session_id, callback.from_user.id) or not db.finish_session(session_id):
        await callback.answer("Session ended or access unavailable.")
        return
    session = db.get_session_by_id(session_id)
    data = await state.get_data()
    if data.get("session_id") == session_id:
        await state.clear()
    await callback.answer("Session ended.")
    await callback.message.answer("Session finished successfully.")
    try:
        await callback.bot.send_message(session["user_telegram_id"], "Your counselor ended this session. / አማካሪዎ ውይይቱን ጨርሷል። /start")
    except Exception:
        logger.warning("Unable to deliver session-ended notification")
