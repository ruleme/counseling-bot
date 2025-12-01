# KUECSF Counseling Bot

Anonymous Telegram counseling bot with bilingual support (English & Amharic).

## Features

- 🌐 Bilingual interface (English/አማርኛ)
- 🔒 Anonymous user IDs
- 💬 Real-time counselor assignment
- 🔄 Session management (End/Return Back)
- 📊 SQLite database for sessions and messages

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export BOT_TOKEN="your_bot_token"
export ADMIN_ID="your_telegram_id"
```

3. Run the bot:
```bash
python main.py
```

## Deploy to Railway (Recommended - FREE)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select this repository
5. Add environment variables:
   - `BOT_TOKEN`: Your Telegram bot token
   - `ADMIN_ID`: Your Telegram user ID
6. Click "Deploy"

**Done!** Your bot runs 24/7 with $5 free credit/month.

## Project Structure

```
counseling/
├── main.py                 # Entry point
├── config.py              # Configuration
├── database.py            # Database operations
├── bot_instance.py        # Global bot instance
├── handlers/              # Message handlers
│   ├── user_handlers.py
│   ├── counselor_handlers.py
│   └── admin_handlers.py
├── keyboards/             # Telegram keyboards
│   └── menus.py
└── utils/                 # Utilities
    ├── anonymous.py
    └── counselor_assignment.py
```

## Environment Variables

- `BOT_TOKEN`: Get from @BotFather on Telegram
- `ADMIN_ID`: Your Telegram user ID (get from @userinfobot)

## License

MIT
