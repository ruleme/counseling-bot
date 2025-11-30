# Quick Start Guide

## 1. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy your bot token

## 2. Get Your Admin ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Start a chat - it will reply with your User ID
3. Copy your User ID

## 3. Configure the Bot

Edit `config.py`:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your token
ADMIN_ID = 123456789  # Replace with your User ID
```

Or set environment variables:

```bash
export BOT_TOKEN="your_bot_token"
export ADMIN_ID=123456789
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the Bot

```bash
python main.py
```

## 6. Add Counselors

Once the bot is running, send to your bot:

```
/admin
```

Then use:

```
/add_counselor <counselor_telegram_id> <category1,category2>
```

Example:
```
/add_counselor 987654321 mental_health,stress,relationship
```

## 7. Test the Bot

1. Start a chat with your bot
2. Send `/start`
3. Choose an issue category
4. You should be connected to a counselor (if one is assigned to that category)

## Available Commands

### For Users
- `/start` - Start using the bot
- `/end` - End current session

### For Counselors
- `/counselor` - Access counselor panel

### For Admins
- `/admin` - Access admin panel
- `/add_counselor <id> <categories>` - Add a counselor
- `/remove_counselor <id>` - Remove a counselor
- `/unblock_user <id>` - Unblock a user

## Troubleshooting

**Bot not responding?**
- Check if BOT_TOKEN is correct
- Make sure the bot is running
- Check console for errors

**Can't add counselors?**
- Make sure ADMIN_ID is set correctly
- Verify you're using the admin account
- Check category names are valid (see config.py)

**Messages not forwarding?**
- Check if counselor is added and active
- Verify session is active
- Check bot logs for errors

