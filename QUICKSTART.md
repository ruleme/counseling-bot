# Setup and Railway deployment

## Local setup (PowerShell)
Use Python 3.11.

```powershell
python -m pip install -r requirements.txt
$env:BOT_TOKEN = "your-new-token"
$env:ADMIN_ID = "your-telegram-user-id"
python main.py
```

On Linux/macOS, use export BOT_TOKEN=... and export ADMIN_ID=....
Never commit tokens. Revoke the previously exposed token using BotFather.

Open the bot privately as a counselor before adding that counselor.
Use /admin, then:
`/add_counselor 987654321 mental_health,stress`
Categories: mental_health, relationship, stress, academic, addiction, family, other.

## Railway preflight
1. Inspect Deployments > Logs and Usage/Billing. Save the shutdown error without sharing tokens.
2. Back up the existing database before deploying or changing its location.
3. Mount a Railway volume at /data.
4. Set BOT_TOKEN, ADMIN_ID, and DATABASE_PATH=/data/counseling_bot.db in Variables.
5. If preserving history, transfer the backed-up database into that location before starting. Changing DATABASE_PATH alone does not move data.
6. Use one service replica, with Serverless/sleep disabled for the polling worker.
7. Use the supplied railway.json: python main.py, /health, and restart-on-failure.
8. Stop the old worker before starting the new one; two workers with one token conflict.
9. Verify startup, /health, user-to-counselor replies, cancellation, ending, and restart/resume with test accounts.
10. Keep the old snapshot for rollback and confirm a restore procedure.

Railway volumes and account settings must be configured separately; repository changes do not create them.
A Railway health check helps deployment readiness; arrange runtime monitoring separately.
Restart policy does not resolve expired credit, billing limits, or intentional shutdowns.
No shutdown cause has been confirmed without the project's actual logs.

## Troubleshooting
- Missing settings: configure environment variables; the application no longer falls back to embedded credentials.
- Telegram conflict: stop other instances using the same token.
- Counselor unreachable: the counselor must open the bot and must not block it.
- Duplicate active sessions: back up the database, inspect duplicates and decide which session to retain; startup deliberately refuses automatic data cleanup.
- Finished/deactivated session: /end and /start let users obtain another available counselor.
- /health 503: inspect application logs, Telegram access and database permissions.
- Data disappears after deployment: verify the volume mount and DATABASE_PATH. An ephemeral filesystem is not persistent storage.

Railway references:
- https://docs.railway.com/config-as-code/reference
- https://docs.railway.com/volumes
