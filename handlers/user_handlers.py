"""
User handlers for the Anonymous Telegram Counseling Bot.
Handles user interactions, issue selection, and messaging.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
"""
User handlers for the Anonymous Telegram Counseling Bot.
Handles user interactions, issue selection, and messaging.
"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from utils.anonymous import get_or_create_anonymous_id
from utils.counselor_assignment import assign_counselor
from keyboards.menus import get_main_menu_keyboard, get_category_keyboard, get_chat_keyboard, get_language_keyboard
import config

logger = logging.getLogger(__name__)
router = Router()
db = Database()


class UserStates(StatesGroup):
    """FSM states for user interactions."""
    waiting_for_language = State()
    waiting_for_issue = State()
    in_chat = State()
    waiting_for_reply = State()


# Category mapping from display name to key
# This is now handled dynamically via config.ISSUE_CATEGORIES
# CATEGORY_MAPPING = {
#     "የአእምሮ ጤና": "mental_health",
#     "ግንኙነት": "relationship",
#     "ውጥረት / ጭንቀት": "stress",
#     "ትምህርት / ሥራ": "academic",
#     "ሱስ": "addiction",
#     "የቤተሰብ ችግሮች": "family",
#     "ሌላ": "other"
# }


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command - show language selection."""
    user_id = message.from_user.id
    
    # Check if user is blocked
    if db.is_user_blocked(user_id):
        # Default to English for blocked message if unknown
        await message.answer(config.STRINGS["blocked"]["en"])
        return
    
    # Get or create anonymous ID (needed for welcome message after language selection)
    get_or_create_anonymous_id(user_id)
    
    # Ask for language
    await message.answer(
        "Please select your language / እባክዎ ቋንቋ ይምረጡ:",
        reply_markup=get_language_keyboard()
    )
    await state.set_state(UserStates.waiting_for_language)


@router.message(StateFilter(UserStates.waiting_for_language))
async def handle_language_selection(message: Message, state: FSMContext):
    """Handle language selection."""
    selection = message.text
    user_id = message.from_user.id
    anonymous_id = get_or_create_anonymous_id(user_id)
    
    lang = "en"
    if selection == "አማርኛ":
        lang = "am"
    elif selection == "English":
        lang = "en"
    else:
        await message.answer("Please select from the menu / እባክዎ ከዝርዝሩ ውስጥ ይምረጡ")
        return
    
    # Save language to state
    await state.update_data(language=lang)
    
    # Show welcome message
    welcome_text = config.STRINGS["welcome"][lang].format(anonymous_id=anonymous_id)
    
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(lang), parse_mode="HTML")
    await state.set_state(UserStates.waiting_for_issue)


@router.message(Command("end"))
async def cmd_end(message: Message, state: FSMContext):
    """Handle /end command - finish the current session."""
    user_id = message.from_user.id
    
    # Get language from state, default to English
    data = await state.get_data()
    lang = data.get("language", "en")
    
    try:
        # Clear state first but keep language
        await state.clear()
        await state.update_data(language=lang)
        
        active_session = db.get_active_session(user_id)
        
        if not active_session:
            await message.answer(
                config.STRINGS["no_active_session"][lang],
                reply_markup=get_main_menu_keyboard(lang)
            )
            await state.set_state(UserStates.waiting_for_issue)
            return
        
        # Finish session
        session_id = active_session["session_id"]
        result = db.finish_session(session_id)
        
        if not result:
            await message.answer(config.STRINGS["session_ended_error"][lang])
            return
        
        # Notify counselor
        try:
            from bot_instance import get_bot
            bot = get_bot()
            anonymous_id = db.get_user_anonymous_id(user_id)
            await bot.send_message(
                active_session["counselor_telegram_id"],
                f"ℹ️ Session with {anonymous_id} has been ended by the user."
            )
        except Exception as e:
            logger.error(f"Error notifying counselor: {e}")
        
        # Always send success message
        await message.answer(
            config.STRINGS["session_ended"][lang],
            reply_markup=get_main_menu_keyboard(lang)
        )
        
        # Set state to waiting for issue
        await state.set_state(UserStates.waiting_for_issue)
        
    except Exception as e:
        logger.error(f"Error in cmd_end: {e}", exc_info=True)
        await message.answer(config.STRINGS["error_generic"][lang].format(error=str(e)))


@router.message(StateFilter(UserStates.waiting_for_issue))
async def handle_issue_selection(message: Message, state: FSMContext):
    """Handle issue category selection."""
    # Ignore commands
    if message.text and message.text.startswith('/'):
        return
    
    user_id = message.from_user.id
    selected_text = message.text
    
    # Get language
    data = await state.get_data()
    lang = data.get("language", "en")
    
    # Check if user selected a language instead of an issue (e.g. double click or old keyboard)
    if selected_text in ["English", "አማርኛ"]:
        new_lang = "en" if selected_text == "English" else "am"
        await state.update_data(language=new_lang)
        
        # Show welcome message with new language
        anonymous_id = get_or_create_anonymous_id(user_id)
        welcome_text = config.STRINGS["welcome"][new_lang].format(anonymous_id=anonymous_id)
        await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(new_lang), parse_mode="HTML")
        return
    
    # Check if user wants to change language
    if selected_text in ["🌐 Change Language", "🌐 ቋንቋ ቀይር"]:
        await message.answer(
            "Please select your language / እባክዎ ቋንቋ ይምረጡ:",
            reply_markup=get_language_keyboard()
        )
        await state.set_state(UserStates.waiting_for_language)
        return

    # Find category key from selected text
    category_key = None
    for key, values in config.ISSUE_CATEGORIES.items():
        if values[lang] == selected_text:
            category_key = key
            break
    
    if not category_key:
        # Try to find category in OTHER language (in case user switched lang but keyboard didn't update)
        other_lang = "am" if lang == "en" else "en"
        for key, values in config.ISSUE_CATEGORIES.items():
            if values[other_lang] == selected_text:
                category_key = key
                # Auto-switch language
                await state.update_data(language=other_lang)
                lang = other_lang
                break
        
        if not category_key:
            await message.answer(config.STRINGS["invalid_selection"][lang])
            return
    
    # Check active session
    active_session = db.get_active_session(user_id)
    if active_session:
        await message.answer(config.STRINGS["active_session_exists"][lang])
        return
    
    # Assign counselor
    counselor_id = assign_counselor(category_key)
    
    if not counselor_id:
        await message.answer(config.STRINGS["no_counselor"][lang])
        return
    
    # Create session
    session_id = db.create_chat_session(user_id, counselor_id, category_key)
    
    if not session_id:
        await message.answer(config.STRINGS["session_error"][lang])
        return
    
    # Get anonymous ID
    anonymous_id = get_or_create_anonymous_id(user_id)
    
    # Notify user
    await message.answer(
        config.STRINGS["connected"][lang].format(category=selected_text, anonymous_id=anonymous_id),
        parse_mode="HTML",
        reply_markup=get_chat_keyboard(lang)
    )
    
    # Notify counselor
    try:
        from bot_instance import get_bot
        bot = get_bot()
        await bot.send_message(
            counselor_id,
            f"🔔 New counseling request\n\n"
            f"Anonymous User: <code>{anonymous_id}</code>\n"
            f"Category: {selected_text} ({lang})\n\n"
            f"Use /counselor to manage your sessions.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error notifying counselor: {e}")
    
    await state.set_state(UserStates.in_chat)


@router.message(StateFilter(UserStates.in_chat))
async def handle_chat_buttons(message: Message, state: FSMContext):
    """Handle chat buttons (End/Back)."""
    # Get language
    data = await state.get_data()
    lang = data.get("language", "en")
    
    text = message.text
    end_text = config.STRINGS["buttons"]["end"][lang]
    back_text = config.STRINGS["buttons"]["back"][lang]
    
    if text == end_text:
        await cmd_end(message, state)
    elif text == back_text:
        await handle_return_back(message, state)
    else:
        # Pass to message handler
        await handle_user_message(message, state)


async def handle_return_back(message: Message, state: FSMContext):
    """Handle return back action."""
    user_id = message.from_user.id
    
    # Get language
    data = await state.get_data()
    lang = data.get("language", "en")
    
    try:
        active_session = db.get_active_session(user_id)
        if active_session:
            session_id = active_session["session_id"]
            db.finish_session(session_id)
            
            # Notify counselor
            try:
                from bot_instance import get_bot
                bot = get_bot()
                anonymous_id = db.get_user_anonymous_id(user_id)
                await bot.send_message(
                    active_session["counselor_telegram_id"],
                    f"ℹ️ Session with {anonymous_id} has been ended by the user (returned back)."
                )
            except Exception as e:
                logger.error(f"Error notifying counselor: {e}")
        
        # Show main menu
        await message.answer(
            config.STRINGS["welcome"][lang].split("\n")[-1], # Just the "choose issue" part
            reply_markup=get_main_menu_keyboard(lang)
        )
        await state.set_state(UserStates.waiting_for_issue)
        
    except Exception as e:
        logger.error(f"Error in handle_return_back: {e}")
        await message.answer(config.STRINGS["error_generic"][lang].format(error=str(e)))


async def handle_user_message(message: Message, state: FSMContext):
    """Handle messages from users in active chat sessions."""
    # Ignore commands
    if message.text and message.text.startswith('/'):
        return
    
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("language", "en")
    
    # Check if user is blocked
    if db.is_user_blocked(user_id):
        await message.answer(config.STRINGS["blocked"][lang])
        await state.clear()
        return
    
    # Get active session
    active_session = db.get_active_session(user_id)
    if not active_session:
        await message.answer(config.STRINGS["no_active_session"][lang])
        await state.set_state(UserStates.waiting_for_issue)
        return
    
    counselor_id = active_session["counselor_telegram_id"]
    session_id = active_session["session_id"]
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
    
    db.save_message(session_id, user_id, message_type, content, file_id)
    
    # Forward message to counselor
    try:
        from bot_instance import get_bot
        bot = get_bot()
        
        if message_type == "text":
            await bot.send_message(
                counselor_id,
                f"💬 Message from {anonymous_id}:\n\n{content}"
            )
        elif message_type == "photo":
            await bot.send_photo(
                counselor_id,
                file_id,
                caption=f"📷 Photo from {anonymous_id}" + (f":\n{content}" if content else "")
            )
        elif message_type == "voice":
            await bot.send_voice(
                counselor_id,
                file_id,
                caption=f"🎤 Voice message from {anonymous_id}"
            )
        elif message_type == "video":
            await bot.send_video(
                counselor_id,
                file_id,
                caption=f"🎥 Video from {anonymous_id}" + (f":\n{content}" if content else "")
            )
        elif message_type == "document":
            await bot.send_document(
                counselor_id,
                file_id,
                caption=f"📄 Document from {anonymous_id}" + (f":\n{content}" if content else "")
            )
    except Exception as e:
        logger.error(f"Error forwarding message to counselor: {e}")
        error_msg = config.STRINGS["error_generic"][lang].format(error="Message delivery failed")
        await message.answer(error_msg)


@router.message()
async def handle_other_messages(message: Message):
    """Handle other messages."""
    if message.text and message.text.startswith('/'):
        return
    
    # Default to English for generic welcome
    await message.answer(config.STRINGS["welcome_back"]["en"])
