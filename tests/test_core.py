import asyncio
import concurrent.futures
import sqlite3
import tempfile
import unittest
import asyncio
from contextlib import closing

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import config
from database import Database
from keep_alive import Health
from utils.relay import deliver, payload


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.db = Database(str(Path(self.temp.name) / "bot.db"))
        self.db.create_user(1, "User-existing")
        self.db.add_counselor(2, ["stress"])

    def test_only_one_active_session_under_competing_requests(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda _: self.db.create_chat_session(1, 2, "stress"), range(5)))
        self.assertEqual(sum(result is not None for result in results), 1)

    def test_finished_session_rejects_reply(self):
        sid = self.db.create_chat_session(1, 2, "stress")
        self.assertTrue(self.db.can_reply(sid, 2))
        self.assertTrue(self.db.finish_session(sid))
        self.assertFalse(self.db.can_reply(sid, 2))
        self.assertFalse(self.db.finish_session(sid))

    def test_removed_counselor_loses_access_without_losing_history(self):
        sid = self.db.create_chat_session(1, 2, "stress")
        self.db.remove_counselor(2)
        self.assertFalse(self.db.is_counselor(2))
        self.assertFalse(self.db.can_reply(sid, 2))
        self.assertIsNotNone(self.db.get_session_by_id(sid))
        self.db.add_counselor(2, ["stress"])
        self.assertTrue(self.db.can_reply(sid, 2))

    def test_blocking_closes_sessions_and_prevents_new_ones(self):
        sid = self.db.create_chat_session(1, 2, "stress")
        self.assertTrue(self.db.block_user(1))
        self.assertFalse(self.db.can_reply(sid, 2))
        self.assertIsNone(self.db.get_active_session(1))
        self.assertIsNone(self.db.create_chat_session(1, 2, "stress"))

    def test_exact_category_and_role_required(self):
        self.assertIsNone(self.db.create_chat_session(1, 2, "mental_health"))
        self.assertIsNone(self.db.create_chat_session(1, 999, "stress"))
        sid = self.db.create_chat_session(1, 2, "stress")
        self.assertFalse(self.db.can_reply(sid, 999))

    def test_foreign_keys_enforced(self):
        with closing(self.db.get_connection()) as conn, conn:
            self.assertEqual(conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO messages(session_id,sender_telegram_id,message_type) VALUES (999,1,'text')")

    def test_restart_preserves_language_and_active_session(self):
        self.db.set_language(1, "am")
        sid = self.db.create_chat_session(1, 2, "stress")
        restarted = Database(self.db.db_path)
        self.assertEqual(restarted.get_language(1), "am")
        self.assertEqual(restarted.get_active_session(1)["session_id"], sid)

    def test_message_delivery_status(self):
        sid = self.db.create_chat_session(1, 2, "stress")
        mid = self.db.save_message(sid, 1, "text", "hello")
        self.db.set_delivery_status(mid, "failed")
        with closing(self.db.get_connection()) as conn, conn:
            self.assertEqual(conn.execute("SELECT delivery_status FROM messages WHERE message_id=?", (mid,)).fetchone()[0], "failed")

    def test_old_schema_migrates_without_losing_data(self):
        old = str(Path(self.temp.name) / "old.db")
        with closing(sqlite3.connect(old)) as conn, conn:
            conn.execute("CREATE TABLE users(telegram_id INTEGER PRIMARY KEY,anonymous_id TEXT UNIQUE NOT NULL,created_at TIMESTAMP,is_blocked INTEGER DEFAULT 0)")
            conn.execute("INSERT INTO users(telegram_id,anonymous_id) VALUES (50,'User-2941')")
        migrated = Database(old)
        self.assertEqual(migrated.get_user_anonymous_id(50), "User-2941")
        self.assertEqual(migrated.get_language(50), "en")

    def test_duplicate_legacy_sessions_fail_without_deleting_history(self):
        sid = self.db.create_chat_session(1, 2, "stress")
        with closing(self.db.get_connection()) as conn, conn:
            conn.execute("DROP INDEX one_active_session_per_user")
            conn.execute("INSERT INTO chat_sessions(user_telegram_id,counselor_telegram_id,category) VALUES (1,2,'stress')")
        with self.assertRaisesRegex(RuntimeError, "Duplicate"):
            Database(self.db.db_path)
        self.assertIsNotNone(self.db.get_session_by_id(sid))


def run_inline(coro):
    # Mock transport completes immediately; no OS sockets are needed.
    try:
        coro.send(None)
    except StopIteration:
        return
    finally:
        coro.close()
    raise AssertionError("Mock relay unexpectedly awaited external work")


class RelayTests(unittest.TestCase):
    def test_long_emoji_text_fits_telegram_limit(self):
        bot = SimpleNamespace(send_message=AsyncMock())
        run_inline(deliver(bot, 2, "Anonymous user", ("text", "😀" * 5000, None)))
        self.assertEqual(bot.send_message.await_count, 3)
        for call in bot.send_message.call_args_list:
            self.assertLessEqual(len(call.args[1].encode("utf-16-le")) // 2, 4096)

    def test_caption_is_sent_separately_from_media(self):
        bot = SimpleNamespace(send_photo=AsyncMock(), send_message=AsyncMock())
        run_inline(deliver(bot, 2, "Anonymous user", ("photo", "x" * 2000, "file")))
        self.assertEqual(bot.send_photo.call_args.kwargs["caption"], "Anonymous user")
        self.assertEqual(bot.send_message.await_count, 2)

    def test_unsupported_payload(self):
        message = SimpleNamespace(text=None, photo=None, voice=None, video=None, document=None)
        self.assertIsNone(payload(message))


class HealthTests(unittest.TestCase):
    def test_readiness_expires_and_can_be_revoked(self):
        health = Health()
        self.assertFalse(health.ready())
        health.mark_ready()
        self.assertTrue(health.ready())
        health.last_success -= 100
        self.assertFalse(health.ready())
        health.mark_ready()
        health.unavailable()
        self.assertFalse(health.ready())


if __name__ == "__main__":
    unittest.main()
