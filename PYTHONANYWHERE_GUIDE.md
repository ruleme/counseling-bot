# PythonAnywhere Deployment Guide

## 🆓 100% Free Forever - No Credit Card Required

PythonAnywhere offers a free tier that's perfect for your Telegram bot.

---

## 📋 Step-by-Step Setup

### **Step 1: Create PythonAnywhere Account**
1. Go to https://www.pythonanywhere.com
2. Click "Start running Python online in less than a minute!"
3. Click "Create a Beginner account" (FREE)
4. Sign up with email
5. Verify your email

---

### **Step 2: Upload Your Code**

#### **Option A: Using Git (Recommended)**
1. Click on "Consoles" tab
2. Click "Bash"
3. Run these commands:
```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/counseling-bot.git

# Navigate to the folder
cd counseling-bot

# Install dependencies
pip3 install --user -r requirements.txt
```

#### **Option B: Upload Files Manually**
1. Click "Files" tab
2. Create a new directory: `counseling-bot`
3. Upload all your files one by one

---

### **Step 3: Set Environment Variables**

1. Click "Files" tab
2. Navigate to your home directory
3. Click on `.bashrc` file (or create it)
4. Add these lines at the end:
```bash
export BOT_TOKEN="your_actual_bot_token_here"
export ADMIN_ID="your_telegram_user_id_here"
```
5. Save the file
6. Go back to Bash console and run:
```bash
source ~/.bashrc
```

---

### **Step 4: Create Always-On Task**

1. Click "Tasks" tab
2. In the "Scheduled tasks" section, add:
   - **Command**: `/home/YOUR_USERNAME/counseling-bot/run_bot.sh`
   - **Hour**: `00` (midnight)
   - **Minute**: `00`
3. Click "Create"

But first, create the `run_bot.sh` script:

```bash
cd ~/counseling-bot
nano run_bot.sh
```

Add this content:
```bash
#!/bin/bash
cd /home/YOUR_USERNAME/counseling-bot
source ~/.bashrc
python3 main.py >> bot.log 2>&1
```

Make it executable:
```bash
chmod +x run_bot.sh
```

---

### **Step 5: Start the Bot**

In the Bash console:
```bash
cd ~/counseling-bot
./run_bot.sh &
```

The `&` runs it in the background.

---

## ✅ Verify It's Running

Check if the bot is running:
```bash
ps aux | grep python
```

You should see `python3 main.py` in the list.

Check logs:
```bash
tail -f ~/counseling-bot/bot.log
```

You should see:
```
Bot starting...
Run polling for bot @YourBot
```

---

## ⚠️ Important Limitations

### **Free Tier Restrictions:**
1. **Console timeout**: Your bot will stop after 3 months
   - **Solution**: Just restart it every 3 months (set a calendar reminder)
2. **CPU seconds**: 100 seconds/day
   - Your bot uses minimal CPU, so this is fine
3. **Disk space**: 512 MB
   - Your bot is ~5 MB, plenty of space

### **Keeping It Running:**
The bot will run continuously, but you need to:
- Restart it every 3 months (PythonAnywhere limitation)
- Or upgrade to paid ($5/month) for always-on tasks

---

## 🔄 How to Restart (Every 3 Months)

1. Log into PythonAnywhere
2. Go to "Consoles" → "Bash"
3. Run:
```bash
cd ~/counseling-bot
git pull  # Get latest changes
./run_bot.sh &
```

**Set a reminder** for 3 months from now!

---

## 📊 Monitoring

### **Check if bot is running:**
```bash
ps aux | grep python
```

### **View logs:**
```bash
tail -f ~/counseling-bot/bot.log
```

### **Stop the bot:**
```bash
pkill -f "python3 main.py"
```

### **Restart the bot:**
```bash
cd ~/counseling-bot
./run_bot.sh &
```

---

## 🔧 Troubleshooting

### **Bot not responding?**
1. Check if it's running: `ps aux | grep python`
2. Check logs: `tail -f ~/counseling-bot/bot.log`
3. Restart: `./run_bot.sh &`

### **"Command not found"?**
Make sure you're using `python3`, not `python`:
```bash
which python3
```

### **Dependencies not installed?**
```bash
pip3 install --user -r requirements.txt
```

---

## 💡 Pro Tips

1. **Set a calendar reminder** for 3 months from now to restart
2. **Check logs weekly** to ensure it's running
3. **Test the bot** after deployment
4. **Backup your database** monthly:
```bash
cp ~/counseling-bot/counseling.db ~/counseling-bot/backup_$(date +%Y%m%d).db
```

---

## 🆙 Upgrade Options

If you need 100% uptime without restarts:
- **PythonAnywhere Hacker Plan**: $5/month
  - Always-on tasks
  - No 3-month limit
  - More CPU/disk

---

## ✅ Summary

**Pros:**
- ✅ 100% free forever
- ✅ No credit card required
- ✅ Easy to set up
- ✅ Reliable hosting

**Cons:**
- ⚠️ Need to restart every 3 months
- ⚠️ Limited CPU (but enough for your bot)

**Perfect for**: Low to medium traffic bots like yours!

---

## 🎯 Quick Start Checklist

- [ ] Create PythonAnywhere account
- [ ] Clone repository or upload files
- [ ] Install dependencies
- [ ] Set environment variables in `.bashrc`
- [ ] Create and run `run_bot.sh`
- [ ] Test bot on Telegram
- [ ] Set 3-month reminder

---

**Need help with any step?** Let me know!
