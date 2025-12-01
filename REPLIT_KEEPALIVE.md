# Replit Keep-Alive Setup

## 🔧 Fix: Bot Stops Running on Replit

Your bot stops because Replit's free tier sleeps after inactivity. Here's the complete fix:

---

## ✅ **Solution Steps:**

### **Step 1: Update Your Code**

I've created `main_replit.py` with a built-in web server. 

**In Replit:**
1. Rename `main.py` to `main_backup.py`
2. Rename `main_replit.py` to `main.py`
3. Update `requirements.txt` to include Flask (already done)

### **Step 2: Push Changes to GitHub**

```bash
git add .
git commit -m "Add Replit keep-alive web server"
git push
```

### **Step 3: Update Replit**

In Replit:
1. Open Shell tab
2. Run: `git pull`
3. Run: `pip install -r requirements.txt`
4. Click "Run"

### **Step 4: Set Up UptimeRobot (FREE)**

1. **Get your Repl URL:**
   - In Replit, look at the Webview tab
   - Copy the URL (e.g., `https://counseling-bot.YOUR_USERNAME.repl.co`)

2. **Create UptimeRobot account:**
   - Go to https://uptimerobot.com
   - Sign up (free, no credit card)

3. **Add Monitor:**
   - Click "+ Add New Monitor"
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: Counseling Bot
   - **URL**: Your Repl URL
   - **Monitoring Interval**: 5 minutes
   - Click "Create Monitor"

4. **Done!** ✅

---

## 🎯 **How It Works:**

1. The bot now runs a Flask web server on port 8080
2. UptimeRobot pings this server every 5 minutes
3. Replit sees activity and keeps your bot awake
4. Your bot runs 24/7 for FREE! 🎉

---

## ✅ **Verify It's Working:**

1. **Check Replit Console:**
   ```
   Flask server started on port 8080
   Bot starting...
   Run polling for bot
   ```

2. **Visit Your Repl URL:**
   - Should show: "✅ Counseling Bot is running!"

3. **Check UptimeRobot Dashboard:**
   - Monitor should show "Up" (green)

4. **Test Telegram Bot:**
   - Send `/start` to your bot
   - Should respond immediately!

---

## 🔄 **Troubleshooting:**

### **Bot still stops?**
- Check UptimeRobot is pinging every 5 minutes
- Verify Repl URL is correct
- Check Replit console for errors

### **"Port already in use"?**
- Restart the Repl
- Click Stop, then Run again

### **Flask not installed?**
```bash
pip install Flask==3.0.0
```

---

## 💰 **Cost:**

- ✅ **Replit**: FREE
- ✅ **UptimeRobot**: FREE
- ✅ **Total**: $0/month

---

## 📊 **Alternative: Paid Option**

If you don't want to use UptimeRobot:
- **Replit Always On**: $7/month
- Guaranteed 24/7 uptime
- No pinging needed

---

**Your bot will now run 24/7 on Replit for FREE!** 🚀
