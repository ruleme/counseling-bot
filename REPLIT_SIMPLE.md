# ✅ REPLIT SETUP - SIMPLE STEPS

## What I Did For You:
1. ✅ Added Flask web server to `main.py`
2. ✅ Updated `requirements.txt` with Flask
3. ✅ Your bot now has a web server to stay awake!

---

## 🚀 What You Need To Do (3 Steps):

### **Step 1: Push to GitHub**
```bash
git add .
git commit -m "Add Replit keep-alive"
git push
```

### **Step 2: Update Replit**
1. Go to your Replit project
2. Open Shell tab
3. Run: `git pull`
4. Run: `pip install Flask`
5. Click the green "Run" button

### **Step 3: Set Up UptimeRobot (Keeps Bot Awake 24/7)**
1. Go to https://uptimerobot.com
2. Sign up (FREE, no credit card)
3. Click "+ Add New Monitor"
4. Fill in:
   - Monitor Type: **HTTP(s)**
   - Friendly Name: **Counseling Bot**
   - URL: **Your Repl URL** (from Replit Webview tab)
   - Monitoring Interval: **5 minutes**
5. Click "Create Monitor"

**DONE!** ✅ Your bot will run 24/7 for FREE!

---

## 🎯 How To Get Your Repl URL:
1. In Replit, click the "Webview" tab (next to Console)
2. Copy the URL (looks like: `https://counseling-bot.YOUR_USERNAME.repl.co`)
3. Use this URL in UptimeRobot

---

## ✅ Verify It's Working:
1. Visit your Repl URL in browser
2. Should show: "✅ Counseling Bot is running!"
3. Test bot on Telegram: Send `/start`

---

**That's it! Your bot stays awake because UptimeRobot pings it every 5 minutes!** 🎉
