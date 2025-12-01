@echo off
echo ========================================
echo GitHub Push Helper
echo ========================================
echo.

cd /d "d:\GFX\fellow kue\counseling"
echo Current directory: %CD%
echo.

echo Step 1: Checking Git status...
git status
echo.

echo ========================================
echo INSTRUCTIONS:
echo ========================================
echo.
echo 1. Create a GitHub repository at: https://github.com/new
echo    - Name: counseling-bot
echo    - Make it PRIVATE
echo    - Do NOT add README or .gitignore
echo.
echo 2. After creating, copy your repository URL
echo    It will look like: https://github.com/YOUR_USERNAME/counseling-bot.git
echo.
echo 3. Run these commands ONE BY ONE:
echo.
echo    git remote add origin YOUR_REPOSITORY_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. When asked for password, use a Personal Access Token from:
echo    https://github.com/settings/tokens
echo.
echo ========================================
pause
