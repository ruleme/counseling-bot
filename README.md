# KUECSF Counseling Bot

A Telegram relay connecting users with human counselors, with English and Amharic user menus. This version stabilizes the existing bot; it does not add a Mini App.

## Setup
Use Python 3.11. Install with `python -m pip install -r requirements.txt`.
Set `BOT_TOKEN` and a positive `ADMIN_ID` in your environment, then run `python main.py`.
See [QUICKSTART.md](QUICKSTART.md) for Windows and Railway instructions.
The application does not load .env files automatically; .env.example documents the variables.

The previous public token must be revoked in BotFather. Removing it from code does not invalidate it or erase history. Enter the replacement directly in Railway Variables.

## Behavior
- Users choose a language/category, send supported messages, and end or resume sessions.
- Incoming user messages have Reply and Finish buttons. Tap Reply to select that anonymous conversation; Finish requires confirmation. Counselors can also use /counselor, select Reply to User, and enter a session ID. The conversation remains selected across replies until /cancel or switching.
- Finishing requires selecting Finish Session before entering its ID.
- /cancel works in every state. Counseling and admin functions operate only in private chats.
- Users, aliases, preferred language, sessions and transcripts survive application restarts when the database is on persistent storage.
- Message delivery is marked pending, delivered or failed. There is no automatic retry; a failed multi-part delivery may be partial. Check before resending.
- Admin exports omit direct identity fields and attachment IDs but contain sensitive transcript text, which may itself identify people.
- /remove_counselor deactivates access without deleting history. Existing sessions remain visible to admin; users can end them and start again with another counselor. Automatic reassignment is not included.

## Administration
/admin; /add_counselor <id> <category1,category2>; /remove_counselor <id>;
/unblock_user <id>; /force_end <user_id>.
The admin panel includes blocking, active sessions, and redacted transcript export.
Counselors must open the bot in a private chat before being assigned.

## Storage and migrations
SQLite remains in use for this repair release. Keep exactly one polling instance.
Set DATABASE_PATH to a persistent writable location. Default: counseling_bot.db.
Startup adds language, delivery status and indexes without changing existing aliases or transcripts.
Older delivery records are marked unknown.
If duplicate active sessions exist, startup fails instead of silently deleting or closing conversations.
Back up and resolve those duplicates deliberately before retrying.
Legacy orphaned records are retained; enabled foreign keys protect new writes.

Before any update, take a consistent snapshot:
`python tools/backup_database.py counseling_bot.db backups/before-upgrade.db`
To restore, stop the bot and copy the snapshot to DATABASE_PATH, then restart.
Keep backups outside public repositories; restrict access and rehearse recovery.

## Reliability
The health server uses PORT (default 8080). /health returns 200 after Telegram API and database checks succeed, or 503 when checks fail or become stale.
This verifies dependencies and a running event loop, not counselor availability or successful receipt of every Telegram update.
Fatal startup/polling failures propagate to the process exit status. Railway can restart failed processes.
Health checks alone do not guarantee continuous runtime monitoring or prevent account/usage suspensions.

## Verification
`python -m compileall -q .`
`python -m unittest discover -s tests -v`
GitHub Actions installs dependencies and runs database, relay and actual Aiogram-dispatch tests with a fake Telegram transport.
No tests use real credentials or send real Telegram messages.

## Remaining work
A counselor Mini App, persistent waiting queue, automatic reassignment/retries, service-specific retention/deletion policy, audit trails and broader staff localization are future work.
SQLite operations are synchronous and intended for a small single-worker deployment. PostgreSQL/async data access should precede multi-worker scaling.
The service owner must define service hours, urgent-help wording, consent and data retention before broad use.
Staff interfaces are primarily English. Have a fluent speaker review the Amharic privacy wording.
No standalone license file has been supplied.
