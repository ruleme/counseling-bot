# Replit Deployment Guide

## 🚀 Easiest Deployment Option - 5 Minutes Setup!

Replit is perfect for beginners - no terminal commands, no complex setup!

---

## ✅ **Why Replit:**

- ✅ **Super easy** - just import from GitHub
- ✅ **Free tier** available
- ✅ **Built-in editor** - edit code in browser
- ✅ **Auto-restart** on crash
- ✅ **Always-on** (with paid plan or keep tab open)

---

## 📋 **Quick Setup (5 Minutes)**

### **Step 1: Create Replit Account**
1. Go to https://replit.com
2. Click "Sign up"
3. Sign up with GitHub (easiest)

---

### **Step 2: Import Your Repository**

1. Click "+ Create Repl"
2. Select "Import from GitHub"
3. Paste your repository URL: `https://github.com/YOUR_USERNAME/counseling-bot`
4. Click "Import from GitHub"
5. Wait for import (30 seconds)

---

### **Step 3: Set Environment Variables (Secrets)**

1. Click the **lock icon** 🔒 on the left sidebar (Secrets)
2. Add two secrets:
   - **Key**: `BOT_TOKEN`
     **Value**: `your_actual_bot_token`
   - **Key**: `ADMIN_ID`
     **Value**: `your_telegram_user_id`
3. Click "Add new secret" for each

---

### **Step 4: Configure Replit**

Replit should auto-detect Python. If not:

1. Click the three dots ⋮ next to "Run"
2. Select "Configure the Repl"
3. Set:
   - **Language**: Python
   - **Run command**: `python main.py`

---

### **Step 5: Run Your Bot**

1. Click the big green **"Run"** button
2. You'll see in the console:
   ```
   Bot starting...
   Run polling for bot @YourBot
   ```
3. **Done!** Your bot is live! 🎉

---

## 🔄 **Keeping It Running 24/7**

### **Option 1: Free (with limitations)**
- Keep the Replit tab open in your browser
- Bot runs as long as tab is open
- **Limitation**: Stops when you close the tab

### **Option 2: Always On (Paid - $7/month)**
1. Click "Deployments" tab
2. Click "Deploy"
3. Select "Reserved VM"
4. Your bot runs 24/7 even when tab is closed

### **Option 3: UptimeRobot Ping (Free Hack)**
1. Get your Repl URL (looks like: `https://counseling-bot.YOUR_USERNAME.repl.co`)
2. Go to https://uptimerobot.com
3. Create a monitor that pings your Repl every 5 minutes
4. This keeps your Repl awake on free tier!

---

## 📝 **Editing Your Code**

1. Click any file in the left sidebar
2. Edit directly in browser
3. Click "Run" to restart with changes
4. Changes auto-save!

---

## 📊 **Monitoring**

### **Check if bot is running:**
- Look at the console output
- Should see "Run polling for bot"

### **View logs:**
- All logs appear in the console window
- Scroll to see history

### **Restart bot:**
- Click "Stop" then "Run"
- Or just click "Run" again

---

## 🔧 **Troubleshooting**

### **"ModuleNotFoundError"?**
Replit should auto-install from `requirements.txt`. If not:
1. Open Shell tab
2. Run: `pip install -r requirements.txt`

### **Bot not responding?**
1. Check console for errors
2. Verify secrets are set correctly
3. Make sure bot token is valid

### **Repl keeps sleeping?**
- Use UptimeRobot to ping it
- Or upgrade to Always On ($7/month)

---

## 💰 **Pricing**

### **Free Tier:**
- ✅ Unlimited public Repls
- ✅ 500 MB storage
- ✅ 0.5 GB RAM
- ⚠️ Sleeps after inactivity (unless pinged)

### **Hacker Plan ($7/month):**
- ✅ Always On deployments
- ✅ 5 GB storage
- ✅ 2 GB RAM
- ✅ Private Repls

---

## 🎯 **Comparison with Other Options**

| Feature | Replit Free | Replit Paid | PythonAnywhere | GCP |
|---------|-------------|-------------|----------------|-----|
| **Ease of Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Cost** | Free* | $7/mo | Free | Free* |
| **24/7 Uptime** | No** | Yes | Yes*** | Yes |
| **Code Editor** | Built-in | Built-in | Basic | None |
| **Auto-restart** | Yes | Yes | No | Yes |

*With limitations
**Unless pinged by UptimeRobot
***Restart every 3 months

---

## 🚀 **Quick Start Checklist**

- [ ] Create Replit account
- [ ] Import from GitHub
- [ ] Add secrets (BOT_TOKEN, ADMIN_ID)
- [ ] Click "Run"
- [ ] Test bot on Telegram
- [ ] (Optional) Set up UptimeRobot ping

---

## 💡 **Pro Tips**

1. **Keep it running free**: Use UptimeRobot to ping your Repl every 5 minutes
2. **Quick edits**: Edit code directly in Replit browser
3. **Collaborate**: Share your Repl with team members
4. **Version control**: Changes sync with GitHub automatically

---

## 🔗 **Useful Links**

- Replit: https://replit.com
- UptimeRobot: https://uptimerobot.com
- Replit Docs: https://docs.replit.com

---

## ✅ **Summary**

**Pros:**
- ✅ Easiest setup (5 minutes)
- ✅ Built-in code editor
- ✅ No terminal needed
- ✅ Auto-install dependencies
- ✅ Great for beginners

**Cons:**
- ⚠️ Free tier sleeps (but can be pinged)
- ⚠️ $7/month for always-on

**Perfect for:** Quick deployment, beginners, testing

---

**Ready to deploy?** Go to https://replit.com and import your GitHub repo! 🚀
