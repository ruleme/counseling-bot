# Anonymous Telegram Counseling Bot

A complete anonymous counseling bot built with Python and aiogram v3. This bot allows users to seek counseling anonymously while protecting their identity from counselors.

## Features

### 🔒 Anonymous System
- Users are assigned random anonymous IDs (e.g., "User-2941")
- Counselors never see usernames or Telegram IDs
- Only admins can view real Telegram IDs

### 📋 Main Menu
- Easy-to-use menu with issue categories:
  - Mental Health
  - Relationship
  - Stress / Anxiety
  - Academic / Career
  - Addiction
  - Family Problems
  - Other

### 💬 Counseling Flow
- Automatic counselor assignment by category
- Round-robin or random assignment based on availability
- Private 1-to-1 anonymous chat sessions
- Full two-way messaging support (text, voice, images, videos, documents)

### 👨‍⚕️ Counselor Panel
- `/counselor` command for counselor access
- View assigned anonymous users
- Reply to users
- Mark chats as finished

### 👑 Admin Panel
- `/admin` command for bot owner
- Add or remove counselors
- Assign counselors to categories
- View active chats
- Block abusive users
- Export chat logs

## Project Structure

```
counseling/
├── main.py                 # Main entry point
├── config.py              # Configuration and settings
├── database.py            # Database operations
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── handlers/              # Message handlers
│   ├── __init__.py
│   ├── user_handlers.py   # User interaction handlers
│   ├── counselor_handlers.py  # Counselor panel handlers
│   └── admin_handlers.py  # Admin panel handlers
├── keyboards/             # Keyboard menus
│   ├── __init__.py
│   └── menus.py           # Keyboard layouts
└── utils/                 # Utility functions
    ├── __init__.py
    ├── anonymous.py       # Anonymous ID generation
    └── counselor_assignment.py  # Counselor assignment logic
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID (for admin access)

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   
   Edit `config.py` or set environment variables:
   
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ADMIN_ID = 123456789  # Your Telegram User ID
   ```
   
   Or set environment variables:
   ```bash
   export BOT_TOKEN="your_bot_token"
   export ADMIN_ID=123456789
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

### Getting Your Telegram User ID

1. Start a chat with [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your User ID
3. Use this ID as `ADMIN_ID` in the configuration

## Usage

### For Users

1. Start the bot with `/start`
2. Choose your issue category from the menu
3. Wait for counselor assignment
4. Start chatting anonymously
5. Use `/end` to finish the session

### For Counselors

1. Admin must add you as a counselor first
2. Use `/counselor` to access the counselor panel
3. View your active sessions
4. Reply to users using "💬 Reply to User"
5. Finish sessions when done

### For Admins

1. Use `/admin` to access the admin panel
2. Add counselors: `/add_counselor <telegram_id> <category1,category2,...>`
   - Example: `/add_counselor 123456789 mental_health,stress`
3. Remove counselors: `/remove_counselor <telegram_id>`
4. View active sessions
5. Block users: Use "🚫 Block User" menu
6. Export logs: Use "📥 Export Logs" menu

## Deployment

### Heroku

1. **Create a Heroku app:**
   ```bash
   heroku create your-bot-name
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set ADMIN_ID=123456789
   ```

3. **Create a Procfile:**
   ```
   worker: python main.py
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

### Render

1. **Create a new Web Service** on Render
2. **Set build command:**
   ```
   pip install -r requirements.txt
   ```
3. **Set start command:**
   ```
   python main.py
   ```
4. **Add environment variables:**
   - `BOT_TOKEN`: Your bot token
   - `ADMIN_ID`: Your Telegram user ID
5. **Deploy**

### Railway

1. **Create a new project** on Railway
2. **Connect your repository** or deploy from GitHub
3. **Add environment variables:**
   - `BOT_TOKEN`: Your bot token
   - `ADMIN_ID`: Your Telegram user ID
4. **Railway will automatically detect Python and install dependencies**
5. **Deploy**

### Local Deployment (Linux/Mac)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with systemd (optional):**
   
   Create `/etc/systemd/system/counseling-bot.service`:
   ```ini
   [Unit]
   Description=Anonymous Counseling Bot
   After=network.target

   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/counseling
   Environment="BOT_TOKEN=your_bot_token"
   Environment="ADMIN_ID=123456789"
   ExecStart=/usr/bin/python3 main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start:**
   ```bash
   sudo systemctl enable counseling-bot
   sudo systemctl start counseling-bot
   ```

## Database

The bot uses SQLite database (`counseling_bot.db`) to store:
- Users and their anonymous IDs
- Counselor information and categories
- Chat sessions
- Messages

The database is automatically created on first run.

## Security Notes

- **Never commit** your `BOT_TOKEN` or `ADMIN_ID` to version control
- Use environment variables for sensitive data
- Regularly backup the database file
- Monitor logs for suspicious activity
- Use the block feature for abusive users

## Troubleshooting

### Bot not responding
- Check if `BOT_TOKEN` is correct
- Verify the bot is running
- Check logs for errors

### Can't add counselors
- Ensure you're using the admin account
- Verify `ADMIN_ID` is set correctly
- Check category names are valid

### Messages not forwarding
- Check if counselor is active
- Verify session is active
- Check bot logs for errors

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions, please check the code comments or create an issue in the repository.

## Contributing

Feel free to submit pull requests or open issues for improvements.

