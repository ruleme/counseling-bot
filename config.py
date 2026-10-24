"""
Configuration file for the Anonymous Telegram Counseling Bot.
Contains bot settings, admin ID, and counselor categories.
"""

import os
from typing import Dict, List

# Bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin Telegram ID (bot owner)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Counselor categories mapping
# Format: category_key -> list of counselor Telegram IDs
COUNSELOR_CATEGORIES: Dict[str, List[int]] = {
    "mental_health": [],  # Add counselor IDs here
    "relationship": [],
    "stress": [],
    "academic": [],
    "addiction": [],
    "family": [],
    "other": []
}

# Issue categories for users
ISSUE_CATEGORIES = {
    "mental_health": {"en": "Mental Health", "am": "የአእምሮ ጤና"},
    "relationship": {"en": "Relationship", "am": "ግንኙነት"},
    "stress": {"en": "Stress / Anxiety", "am": "ውጥረት / ጭንቀት"},
    "academic": {"en": "Academic / Career", "am": "ትምህርት / ሥራ"},
    "addiction": {"en": "Addiction", "am": "ሱስ"},
    "family": {"en": "Family Problems", "am": "የቤተሰብ ችግሮች"},
    "other": {"en": "Other", "am": "ሌላ"}
}

# Bilingual Strings
STRINGS = {
    "welcome": {
        "en": "👋 Welcome to the Anonymous Counseling Bot\n\nYour anonymous ID: <code>{anonymous_id}</code>\n\nCounselors see your anonymous ID. The service stores your Telegram ID and messages; authorized administrators can access them. Shared media may reveal your identity.\n\nPlease choose your issue:",
        "am": "👋 ወደ ሚስጥራዊ የምክር አገልግሎት ቦት እንኳን በደህና መጡ\n\nየእርስዎ ሚስጥራዊ መታወቂያ: <code>{anonymous_id}</code>\n\nአማካሪዎች ሚስጥራዊ መታወቂያዎን ያያሉ። አገልግሎቱ የቴሌግራም መታወቂያዎን እና መልእክቶችዎን ያስቀምጣል፤ ፈቃድ ያላቸው አስተዳዳሪዎች ሊያዩአቸው ይችላሉ። የሚልኩት ሚዲያ ማንነትዎን ሊገልጽ ይችላል።\n\nእባክዎ የምክር አገልግሎት የሚፈልጉበትን ጉዳይ ይምረጡ:"
    },
    "choose_language": {
        "en": "Please select your language:",
        "am": "እባክዎ ቋንቋ ይምረጡ:"
    },
    "invalid_selection": {
        "en": "❌ Invalid selection. Please choose from the menu.",
        "am": "❌ የተሳሳተ ምርጫ። እባክዎ ከዝርዝሩ ውስጥ ይምረጡ።"
    },
    "active_session_exists": {
        "en": "⚠️ You already have an active session.\nPlease finish your current session before starting a new one.",
        "am": "⚠️ አስቀድሞ ንቁ የሆነ ውይይት አለዎት።\nአዲስ ከመጀመርዎ በፊት እባክዎ አሁን ያለውን ውይይት ይጨርሱ።"
    },
    "no_counselor": {
        "en": "❌ No counselor is available for this category at the moment.\nPlease try again later or contact the administrator.",
        "am": "❌ ለዚህ ጉዳይ የሚሆን አማካሪ በአሁኑ ጊዜ የለም።\nእባክዎ ትንሽ ቆይተው ይሞክሩ።"
    },
    "session_error": {
        "en": "❌ Error creating session. Please try again.",
        "am": "❌ ውይይት ለመጀመር ችግር አጋጥሟል። እባክዎ እንደገና ይሞክሩ።"
    },
    "connected": {
        "en": "✅ You have been connected to a counselor!\n\nCategory: {category}\nYour anonymous ID: <code>{anonymous_id}</code>\n\nYou can now send messages. The counselor will see you as {anonymous_id}.\n\nType /end or press the button below to end the session.",
        "am": "✅ ከአማካሪ ጋር ተገናኝተዋል!\n\nጉዳይ: {category}\nየእርስዎ ሚስጥራዊ መታወቂያ: <code>{anonymous_id}</code>\n\nአሁን መልእክት መላክ ይችላሉ። አማካሪው እርስዎን የሚያዩት በዚህ መታወቂያ ነው: {anonymous_id}።\n\nውይይቱን ለመጨረስ 'ጨርስ' የሚለውን ቁልፍ ይጫኑ ወይም /end ብለው ይጻፉ።"
    },
    "no_active_session": {
        "en": "❌ You don't have an active session.\n\nType /start to begin a new session.",
        "am": "❌ ምንም ንቁ የሆነ ውይይት የለዎትም።\n\nአዲስ ውይይት ለመጀመር /start ብለው ይጻፉ።"
    },
    "session_ended_error": {
        "en": "❌ Failed to end session. Please try again or contact support.",
        "am": "❌ ውይይቱን ለመጨረስ ችግር አጋጥሟል። እባክዎ እንደገና ይሞክሩ።"
    },
    "session_ended": {
        "en": "✅ Your session has been ended.\n\nThank you for using our counseling service.\nIf you want another counseling service, please select an issue below.",
        "am": "✅ ውይይቱ ተጠናቋል።\n\nየእኛን የምክር አገልግሎት ስለተጠቀሙ እናመሰግናለን።\nሌላ የምክር አገልግሎት ከፈለጉ፣ እባክዎ ከታች ያለውን ጉዳይ ይምረጡ።"
    },
    "error_generic": {
        "en": "❌ Error: {error}\nPlease try again or contact support.",
        "am": "❌ ስህተት አጋጥሟል: {error}\nእባክዎ እንደገና ይሞክሩ።"
    },
    "blocked": {
        "en": "❌ You have been blocked from using this bot.",
        "am": "❌ ይህን ቦት እንዳይጠቀሙ ታግደዋል።"
    },
    "welcome_back": {
        "en": "👋 Welcome! Type /start to begin using the counseling bot.",
        "am": "👋 ሰላም! ቦቱን ለመጠቀም /start ብለው ይጻፉ።"
    },
    "buttons": {
        "end": {"en": "End Session", "am": "ጨርስ"},
        "back": {"en": "Return Back", "am": "ተመለስ"}
    }
}

# Database file path
DATABASE_PATH = os.getenv("DATABASE_PATH", "counseling_bot.db")

# Anonymous ID format
ANONYMOUS_ID_PREFIX = "User-"
ANONYMOUS_ID_LENGTH = 12  # New aliases; existing aliases are preserved



def validate():
    if not BOT_TOKEN:
        raise ValueError("Set BOT_TOKEN in the environment")
    if ADMIN_ID <= 0:
        raise ValueError("Set a positive ADMIN_ID in the environment")
