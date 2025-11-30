# 24/7 Bot Hosting Guide

This guide covers different options for hosting your Telegram counseling bot 24/7.

## Option 1: Free Cloud Hosting (Recommended for Testing)

### Render.com (Free Tier)
1. **Create a `requirements.txt`** (already exists in your project)
2. **Create a `Procfile`** in your project root:
   ```
   worker: python main.py
   ```
3. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```
4. **Deploy on Render**:
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Background Worker"
   - Connect your repository
   - Set environment variables:
     - `BOT_TOKEN`: Your bot token
     - `ADMIN_ID`: Your Telegram user ID
   - Click "Create Background Worker"

**Pros**: Free, easy setup, auto-restarts on crash
**Cons**: May sleep after inactivity on free tier

### Railway.app (Free $5 Credit)
1. **Create a `Procfile`** (same as above)
2. **Deploy**:
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add environment variables (BOT_TOKEN, ADMIN_ID)
   - Deploy

**Pros**: Better free tier, faster deployment
**Cons**: Limited free credits ($5/month)

---

## Option 2: VPS Hosting (Best for Production)

### DigitalOcean / Linode / Vultr ($5-10/month)

1. **Create a VPS** (Ubuntu 22.04 recommended)

2. **SSH into your server**:
   ```bash
   ssh root@YOUR_SERVER_IP
   ```

3. **Install Python and dependencies**:
   ```bash
   apt update
   apt install python3 python3-pip git -y
   ```

4. **Clone your repository**:
   ```bash
   git clone YOUR_REPO_URL
   cd counseling
   ```

5. **Install requirements**:
   ```bash
   pip3 install -r requirements.txt
   ```

6. **Set environment variables**:
   ```bash
   export BOT_TOKEN="your_bot_token"
   export ADMIN_ID="your_admin_id"
   ```

7. **Run with systemd (auto-restart on crash)**:

   Create `/etc/systemd/system/counseling-bot.service`:
   ```ini
   [Unit]
   Description=Counseling Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/counseling
   Environment="BOT_TOKEN=YOUR_BOT_TOKEN"
   Environment="ADMIN_ID=YOUR_ADMIN_ID"
   ExecStart=/usr/bin/python3 /root/counseling/main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   systemctl daemon-reload
   systemctl enable counseling-bot
   systemctl start counseling-bot
   systemctl status counseling-bot
   ```

**Pros**: Full control, reliable, can handle high traffic
**Cons**: Costs $5-10/month, requires server management

---

## Option 3: Windows PC/Laptop (Keep Running 24/7)

### Using Task Scheduler

1. **Create a batch file** `start_bot.bat`:
   ```batch
   @echo off
   cd /d "d:\GFX\fellow kue\counseling"
   python main.py
   ```

2. **Open Task Scheduler**:
   - Press Win+R, type `taskschd.msc`
   - Click "Create Basic Task"
   - Name: "Counseling Bot"
   - Trigger: "When the computer starts"
   - Action: "Start a program"
   - Program: `d:\GFX\fellow kue\counseling\start_bot.bat`
   - Check "Run with highest privileges"

3. **Configure for auto-restart**:
   - Right-click task → Properties
   - Settings tab:
     - ✅ "If the task fails, restart every: 1 minute"
     - ✅ "Attempt to restart up to: 3 times"

**Pros**: Free, uses your existing PC
**Cons**: PC must stay on 24/7, uses electricity, not reliable if PC restarts

---

## Option 4: Docker (Advanced)

### Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: always
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
    volumes:
      - ./counseling.db:/app/counseling.db
```

### Run:
```bash
docker-compose up -d
```

**Pros**: Isolated environment, easy to deploy anywhere
**Cons**: Requires Docker knowledge

---

## Recommended Approach

**For Testing/Personal Use**: 
- Use **Render.com** (free, easy setup)

**For Production/Professional Use**: 
- Use **DigitalOcean VPS** ($5/month, reliable)

**For Development**: 
- Keep running on your PC with Task Scheduler

---

## Monitoring & Maintenance

### Check Bot Status
- **Render/Railway**: Check dashboard
- **VPS**: `systemctl status counseling-bot`
- **Windows**: Task Manager → Background processes

### View Logs
- **Render/Railway**: Dashboard → Logs
- **VPS**: `journalctl -u counseling-bot -f`
- **Windows**: Check console output

### Update Bot
1. Pull latest changes: `git pull`
2. Restart service:
   - **Render/Railway**: Auto-deploys on git push
   - **VPS**: `systemctl restart counseling-bot`
   - **Windows**: Restart task in Task Scheduler

---

## Security Tips

1. **Never commit your bot token** to GitHub
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use HTTPS** for webhooks (if using webhook mode)

3. **Backup your database** regularly:
   ```bash
   cp counseling.db counseling_backup_$(date +%Y%m%d).db
   ```

4. **Monitor logs** for errors and suspicious activity

---

## Need Help?

- **Render Issues**: https://render.com/docs
- **VPS Setup**: https://www.digitalocean.com/community/tutorials
- **Bot API**: https://core.telegram.org/bots/api
