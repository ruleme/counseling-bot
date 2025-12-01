# Google Cloud Platform Deployment Guide

## ☁️ Deploy Your Telegram Bot on GCP Free Tier

Google Cloud offers $300 free credit for 90 days, plus an always-free f1-micro VM perfect for your bot.

---

## 📋 Prerequisites

- Google account
- GitHub repository with your code
- Bot token and admin ID

---

## 🎯 Step-by-Step Deployment

### **Step 1: Create GCP Account**

1. Go to https://cloud.google.com/free
2. Click "Get started for free"
3. Sign in with Google account
4. Enter payment info (required for verification, won't be charged)
5. Activate $300 free credit

---

### **Step 2: Create a VM Instance**

1. Go to **Console** → **Compute Engine** → **VM instances**
2. Click "Create Instance"
3. Configure:
   - **Name**: `counseling-bot`
   - **Region**: Choose closest to you (e.g., `us-central1`)
   - **Machine type**: `e2-micro` (FREE tier)
   - **Boot disk**: 
     - Click "Change"
     - Select "Ubuntu 22.04 LTS"
     - Size: 10 GB (free tier allows 30 GB)
   - **Firewall**: ✅ Allow HTTP traffic
4. Click "Create"

---

### **Step 3: Connect to Your VM**

1. Click "SSH" button next to your instance
2. A terminal will open in your browser

---

### **Step 4: Install Dependencies**

Run these commands in the SSH terminal:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip git -y

# Verify installation
python3 --version
pip3 --version
```

---

### **Step 5: Clone Your Repository**

```bash
# Clone your bot code
git clone https://github.com/YOUR_USERNAME/counseling-bot.git

# Navigate to directory
cd counseling-bot

# Install Python dependencies
pip3 install -r requirements.txt
```

---

### **Step 6: Set Environment Variables**

```bash
# Edit bashrc
nano ~/.bashrc

# Add at the end:
export BOT_TOKEN="your_bot_token_here"
export ADMIN_ID="your_telegram_id_here"

# Save: Ctrl+O, Enter, Ctrl+X

# Apply changes
source ~/.bashrc
```

---

### **Step 7: Create Systemd Service (Auto-restart)**

This makes your bot run 24/7 and restart automatically if it crashes.

```bash
# Create service file
sudo nano /etc/systemd/system/counseling-bot.service
```

Add this content:
```ini
[Unit]
Description=Counseling Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/counseling-bot
Environment="BOT_TOKEN=your_bot_token_here"
Environment="ADMIN_ID=your_telegram_id_here"
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/counseling-bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace**:
- `YOUR_USERNAME` with your GCP username (run `whoami` to see it)
- `your_bot_token_here` with your actual bot token
- `your_telegram_id_here` with your Telegram user ID

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

---

### **Step 8: Start the Bot**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable counseling-bot

# Start the bot
sudo systemctl start counseling-bot

# Check status
sudo systemctl status counseling-bot
```

You should see:
```
● counseling-bot.service - Counseling Telegram Bot
   Active: active (running)
```

---

## ✅ Verify Deployment

### **Check if bot is running:**
```bash
sudo systemctl status counseling-bot
```

### **View logs:**
```bash
sudo journalctl -u counseling-bot -f
```

You should see:
```
Bot starting...
Run polling for bot @YourBot
```

### **Test on Telegram:**
1. Open Telegram
2. Send `/start` to your bot
3. Should respond with language selection!

---

## 🔧 Management Commands

### **Stop the bot:**
```bash
sudo systemctl stop counseling-bot
```

### **Restart the bot:**
```bash
sudo systemctl restart counseling-bot
```

### **View logs:**
```bash
sudo journalctl -u counseling-bot -f
```

### **Update bot code:**
```bash
cd ~/counseling-bot
git pull
sudo systemctl restart counseling-bot
```

---

## 💰 Cost Breakdown

### **Free Tier (Always Free):**
- ✅ 1 e2-micro VM instance
- ✅ 30 GB standard storage
- ✅ 1 GB network egress/month
- ✅ Perfect for your bot!

### **After $300 Credit:**
- Your bot uses minimal resources
- Should stay within free tier limits
- Estimated cost: **$0/month** if you stay within limits

### **Monitor Usage:**
- Go to **Billing** → **Reports**
- Check your usage monthly
- Set up billing alerts

---

## 🔒 Security Best Practices

### **1. Set up Firewall:**
```bash
# Allow only SSH
sudo ufw allow 22/tcp
sudo ufw enable
```

### **2. Keep System Updated:**
```bash
sudo apt update && sudo apt upgrade -y
```

### **3. Backup Database:**
```bash
# Create backup script
nano ~/backup.sh
```

Add:
```bash
#!/bin/bash
cp ~/counseling-bot/counseling.db ~/backups/counseling_$(date +%Y%m%d).db
```

Make executable:
```bash
chmod +x ~/backup.sh
```

Add to crontab (run daily):
```bash
crontab -e
# Add: 0 2 * * * /home/YOUR_USERNAME/backup.sh
```

---

## 📊 Monitoring

### **Set up Uptime Monitoring:**
1. Use https://uptimerobot.com (free)
2. Monitor your bot's health
3. Get alerts if it goes down

### **Check Resource Usage:**
```bash
# CPU and memory
htop

# Disk usage
df -h

# Bot process
ps aux | grep python
```

---

## 🆙 Scaling (If Needed)

If your bot gets popular:
1. **Upgrade VM**: Change to `e2-small` or `e2-medium`
2. **Add Load Balancer**: Distribute traffic
3. **Use Cloud SQL**: For database (instead of SQLite)

---

## ❓ Troubleshooting

### **Bot not starting?**
```bash
sudo journalctl -u counseling-bot -n 50
```

### **Permission denied?**
```bash
sudo chown -R $USER:$USER ~/counseling-bot
```

### **Out of memory?**
```bash
free -h
# Upgrade to e2-small if needed
```

---

## 🎯 Summary

**Pros:**
- ✅ Professional hosting
- ✅ 100% uptime
- ✅ Auto-restart on crash
- ✅ Free (within limits)
- ✅ Scalable

**Cons:**
- ⚠️ Requires credit card for verification
- ⚠️ More complex setup
- ⚠️ Need to monitor usage

**Perfect for:** Production deployment, long-term hosting

---

## 📚 Additional Resources

- GCP Free Tier: https://cloud.google.com/free
- GCP Documentation: https://cloud.google.com/docs
- Systemd Guide: https://www.digitalocean.com/community/tutorials/systemd-essentials-working-with-services-units-and-the-journal

---

**Your bot will run 24/7 on Google's infrastructure!** 🚀
