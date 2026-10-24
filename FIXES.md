# Existing bot repair release

Prepared against main commit d3856455ae1c54254daed334b74f612b016df3c7.
No Mini App has been added. No live deployment or existing production database was changed.

## Included
- Environment-only credentials with startup validation.
- Private-chat restriction for messages and access checks on conversation callbacks.
- Resume active user sessions after /start and lost in-memory state; persisted language.
- Per-conversation Reply buttons, persistent selected counselor replies, and confirmed Finish buttons.
- Cancellation before role-specific input handlers; explicit finish selection.
- Recheck active counselor registration, session ownership, session status and user blocking.
- Prevent duplicate active sessions; enable foreign keys; preserve counselor/session history.
- Larger new anonymous aliases; existing aliases retained.
- Bounded text chunks, supported-media validation and delivery-state recording.
- Close unconfirmed sessions if the counselor cannot be notified.
- Redacted identity fields in admin exports; no temporary transcript files.
- Dependency-aware readiness endpoint, graceful shutdown and fatal startup failure propagation.
- Configurable persistent database path, Railway configuration and backup utility.

## Validation
All Python files compile.
14 database/relay/readiness tests passed locally.
16 real-Aiogram dispatcher tests are included but could not run: dependencies are unavailable and network installation was blocked by the environment's approval policy.
GitHub workflow is supplied to install requirements and run all 30 tests.
No live Telegram calls or Railway deployment were performed.

## Publication
Changes are prepared on a dedicated repair branch for review. No live deployment has been performed.

## Before deployment
1. Review the repair branch and run the supplied GitHub checks before merging.
2. Run all tests with requirements installed and use a separate test Telegram bot for acceptance testing.
3. Revoke the exposed token and set the replacement directly in Railway.
4. Back up the existing database and preserve it when setting DATABASE_PATH on a volume.
5. Inspect Railway shutdown logs, billing limits and service settings. The actual shutdown cause is unconfirmed.
6. Keep one polling replica; stop the previous worker before starting the replacement.

## Remaining scope
No Mini App, waiting queue, automated reassignment, automatic delivery retries, retention/deletion automation or PostgreSQL migration is included.
Partial multi-message delivery is possible; failed delivery is recorded and reported.
Staff menus remain primarily English. Review translated privacy wording with a fluent speaker.
