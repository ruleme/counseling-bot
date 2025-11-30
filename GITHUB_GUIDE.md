# GitHub Push Guide

## Step-by-Step Instructions

### 1. Create a GitHub Account (if you don't have one)
- Go to https://github.com
- Click "Sign up"
- Follow the registration process

### 2. Create a New Repository
1. Go to https://github.com/new
2. Repository name: `counseling-bot` (or any name you like)
3. Description: "Anonymous Telegram Counseling Bot"
4. Choose: **Private** (to keep your code private)
5. **DO NOT** check "Add a README file"
6. Click "Create repository"

### 3. Install Git (if not installed)
Download from: https://git-scm.com/download/win

### 4. Configure Git (First Time Only)
Open PowerShell in your project folder and run:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 5. Push Your Code

Run these commands in PowerShell (in your project folder):

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: Bilingual counseling bot"

# Add your GitHub repository as remote
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/counseling-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 6. Enter GitHub Credentials
When prompted:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your password)

#### How to Create a Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: "Counseling Bot Deploy"
4. Expiration: "No expiration" or "1 year"
5. Select scopes: ✅ **repo** (all)
6. Click "Generate token"
7. **COPY THE TOKEN** (you won't see it again!)
8. Use this token as your password when pushing

### 7. Verify Upload
- Go to your GitHub repository: `https://github.com/YOUR_USERNAME/counseling-bot`
- You should see all your files!

---

## Quick Commands Reference

```bash
# Check status
git status

# Add new changes
git add .

# Commit changes
git commit -m "Your message here"

# Push to GitHub
git push

# Pull latest changes
git pull
```

---

## Important Security Notes

⚠️ **NEVER commit your bot token to GitHub!**

The `.gitignore` file I created will prevent:
- `counseling.db` (database)
- `.env` files (environment variables)
- `__pycache__/` (Python cache)

Your `config.py` **WILL** be uploaded. Make sure to:
1. Remove the actual bot token from `config.py`
2. Use environment variables instead (see below)

### Using Environment Variables (Recommended)

Update your `config.py`:
```python
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
```

Then set environment variables on Render/Railway instead of hardcoding them.

---

## Troubleshooting

### "fatal: not a git repository"
Run: `git init`

### "remote origin already exists"
Run: `git remote remove origin` then add it again

### "failed to push"
Run: `git pull origin main --rebase` then `git push`

### Authentication failed
Make sure you're using a **Personal Access Token**, not your password

---

## Next Steps After Pushing

1. ✅ Code is on GitHub
2. Go to https://render.com
3. Create a new "Background Worker"
4. Connect your GitHub repository
5. Add environment variables (BOT_TOKEN, ADMIN_ID)
6. Deploy!

Your bot will be live 24/7! 🚀
