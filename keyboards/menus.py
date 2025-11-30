"""
Keyboard menus for the bot.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config


def get_language_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for language selection."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="English"), KeyboardButton(text="አማርኛ")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Create the main menu keyboard with issue categories."""
    # Get categories for the selected language
    categories = []
    for key, values in config.ISSUE_CATEGORIES.items():
        categories.append(values[lang])
    
    # Create rows of 2 buttons
    keyboard_buttons = []
    row = []
    for category in categories:
        row.append(KeyboardButton(text=category))
        if len(row) == 2:
            keyboard_buttons.append(row)
            row = []
    if row:
        keyboard_buttons.append(row)
    
    # Add "Change Language" button at the bottom
    change_lang_text = "🌐 Change Language" if lang == "en" else "🌐 ቋንቋ ቀይር"
    keyboard_buttons.append([KeyboardButton(text=change_lang_text)])
        
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_category_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Create inline keyboard for category selection."""
    buttons = []
    for key, values in config.ISSUE_CATEGORIES.items():
        buttons.append([InlineKeyboardButton(text=values[lang], callback_data=f"category_{key}")])
        
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_counselor_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for counselor panel."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 My Sessions")],
            [KeyboardButton(text="💬 Reply to User")],
            [KeyboardButton(text="✅ Finish Session")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard for admin panel."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Manage Counselors")],
            [KeyboardButton(text="📊 Active Sessions")],
            [KeyboardButton(text="🚫 Block User")],
            [KeyboardButton(text="📥 Export Logs")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_session_keyboard(session_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for session actions."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Reply", callback_data=f"reply_{session_id}")],
            [InlineKeyboardButton(text="✅ Finish", callback_data=f"finish_{session_id}")]
        ]
    )
    return keyboard


def get_chat_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Create keyboard for active chat session."""
    end_text = config.STRINGS["buttons"]["end"][lang]
    back_text = config.STRINGS["buttons"]["back"][lang]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=end_text)],
            [KeyboardButton(text=back_text)]
        ],
        resize_keyboard=True
    )
    return keyboard
