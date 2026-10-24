"""Exercise real Aiogram dispatch with an in-memory Telegram transport."""
import importlib.util
import tempfile
import unittest
import asyncio
from contextlib import closing

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from datetime import datetime, timezone
from pathlib import Path

HAS_AIOGRAM = importlib.util.find_spec("aiogram") is not None

if HAS_AIOGRAM:
    from aiogram import Bot, Dispatcher
    from aiogram.client.session.base import BaseSession
    from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
    from aiogram.types import Chat, Message, Update, User, CallbackQuery
    import config
    # Handler module initialization must never create a production database in tests.
    _bootstrap = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
    config.DATABASE_PATH = str(Path(_bootstrap.name) / "bootstrap.db")
    from database import Database
    from handlers import admin_handlers as admin, counselor_handlers as counselor, user_handlers as user
    from utils import anonymous, counselor_assignment
    from utils.middleware import PrivateChatMiddleware
    from bot_instance import set_bot

    class RecordingSession(BaseSession):
        def __init__(self):
            super().__init__()
            self.calls = []
            self.fail_chat = None

        async def close(self):
            pass

        async def make_request(self, bot, method, timeout=None):
            self.calls.append(method)
            if not hasattr(method, "chat_id"):
                return True
            if method.chat_id == self.fail_chat:
                raise RuntimeError("Simulated unavailable chat")
            return Message(message_id=100, date=datetime.now(timezone.utc),
                           chat=Chat(id=int(method.chat_id), type="private"),
                           text=getattr(method, "text", None))

        async def stream_content(self, *args, **kwargs):
            if False:
                yield b""


@unittest.skipUnless(HAS_AIOGRAM, "Aiogram unavailable locally; CI installs requirements")
class HandlerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.db = Database(str(Path(self.temp.name) / "test.db"))
        for module in (admin, counselor, user, anonymous, counselor_assignment):
            module.db = self.db
        self.db.create_user(1, "User-2941")
        self.db.add_counselor(2, ["stress"])
        self.sid = self.db.create_chat_session(1, 2, "stress")
        self.transport = RecordingSession()
        self.bot = Bot(token="123456789:" + "A" * 35, session=self.transport)
        set_bot(self.bot)
        # Routers may only have one parent; detach after each test.
        self.dp = Dispatcher(storage=MemoryStorage(), events_isolation=SimpleEventIsolation())
        self.dp.message.outer_middleware(PrivateChatMiddleware())
        for router in (admin.router, counselor.router, user.router):
            self.dp.include_router(router)
        self.counter = 0

    async def asyncTearDown(self):
        for router in (admin.router, counselor.router, user.router):
            router._parent_router = None
        self.dp.sub_routers.clear()
        await self.dp.storage.close()
        await self.bot.session.close()
        self.temp.cleanup()

    async def send(self, sender, text=None, chat_type="private"):
        self.counter += 1
        message = Message(message_id=self.counter, date=datetime.now(timezone.utc),
                          chat=Chat(id=sender if chat_type == "private" else -100, type=chat_type),
                          from_user=User(id=sender, is_bot=False, first_name="Test"), text=text)
        await self.dp.feed_update(self.bot, Update(update_id=self.counter, message=message))

    def state(self, sender):
        return self.dp.fsm.get_context(bot=self.bot, chat_id=sender, user_id=sender)

    async def test_start_resumes_existing_session(self):
        self.db.set_language(1, "am")
        await self.send(1, "/start")
        self.assertEqual(await self.state(1).get_state(), user.UserStates.in_chat.state)
        self.assertEqual((await self.state(1).get_data())["language"], "am")

    async def test_normal_message_recovers_after_restart(self):
        await self.send(1, "hello after restart")
        self.assertEqual(self.transport.calls[-1].chat_id, 2)
        self.assertIn("hello after restart", self.transport.calls[-1].text)

    async def test_cancel_does_not_relay_as_counselor_reply(self):
        state = self.state(2)
        await state.set_state(counselor.CounselorStates.waiting_for_reply)
        await state.update_data(session_id=self.sid, user_id=1)
        await self.send(2, "/cancel")
        self.assertIsNone(await state.get_state())
        self.assertTrue(all(call.chat_id != 1 for call in self.transport.calls))

    async def test_numeric_message_does_not_finish_without_finish_state(self):
        await self.send(2, str(self.sid))
        self.assertEqual(self.db.get_session_by_id(self.sid)["status"], "active")

    async def test_selected_reply_cannot_reach_finished_session(self):
        state = self.state(2)
        await state.set_state(counselor.CounselorStates.waiting_for_reply)
        await state.update_data(session_id=self.sid, user_id=1)
        self.db.finish_session(self.sid)
        await self.send(2, "late reply")
        self.assertTrue(all(call.chat_id != 1 for call in self.transport.calls))

    async def test_removed_counselor_cannot_send_selected_reply(self):
        state = self.state(2)
        await state.set_state(counselor.CounselorStates.waiting_for_reply)
        await state.update_data(session_id=self.sid, user_id=1)
        self.db.remove_counselor(2)
        await self.send(2, "late reply")
        self.assertTrue(all(call.chat_id != 1 for call in self.transport.calls))

    async def test_group_command_has_no_sensitive_response(self):
        await self.send(config.ADMIN_ID or 3, "/admin", "group")
        self.assertEqual(self.transport.calls, [])

    async def test_reply_selection_persists_across_messages(self):
        state = self.state(2)
        await state.set_state(counselor.CounselorStates.waiting_for_reply)
        await state.update_data(session_id=self.sid, user_id=1)
        await self.send(2, "first")
        await self.send(2, "second")
        delivered = [call for call in self.transport.calls if call.chat_id == 1]
        self.assertEqual(len(delivered), 2)
        self.assertEqual(await state.get_state(), counselor.CounselorStates.waiting_for_reply.state)

    async def test_finish_requires_explicit_selection(self):
        await self.send(2, "✅ Finish Session")
        await self.send(2, str(self.sid))
        self.assertEqual(self.db.get_session_by_id(self.sid)["status"], "finished")

    async def callback(self, sender, action, chat_type="private"):
        self.counter += 1
        message = Message(message_id=100, date=datetime.now(timezone.utc),
                          chat=Chat(id=sender, type=chat_type), text="session")
        callback = CallbackQuery(id=str(self.counter), from_user=User(id=sender, is_bot=False, first_name="Test"),
                                 chat_instance="test", data=action, message=message)
        await self.dp.feed_update(self.bot, Update(update_id=self.counter, callback_query=callback))

    async def test_reply_button_selects_correct_user(self):
        await self.callback(2, f"reply_{self.sid}")
        self.assertEqual((await self.state(2).get_data())["user_id"], 1)
        self.assertEqual(await self.state(2).get_state(), counselor.CounselorStates.waiting_for_reply.state)

    async def test_reply_button_rejects_other_counselor(self):
        self.db.add_counselor(3, ["stress"])
        await self.callback(3, f"reply_{self.sid}")
        self.assertIsNone(await self.state(3).get_state())

    async def test_finish_button_requires_confirmation(self):
        await self.callback(2, f"finish_{self.sid}")
        self.assertEqual(self.db.get_session_by_id(self.sid)["status"], "active")
        await self.callback(2, f"endconfirm_{self.sid}")
        self.assertEqual(self.db.get_session_by_id(self.sid)["status"], "finished")

    async def test_group_reply_button_cannot_select_conversation(self):
        await self.callback(2, f"reply_{self.sid}", "group")
        self.assertIsNone(await self.state(2).get_state())

    async def test_unreachable_counselor_does_not_leave_false_connection(self):
        self.db.finish_session(self.sid)
        await self.state(1).set_state(user.UserStates.waiting_for_issue)
        self.transport.fail_chat = 2
        await self.send(1, config.ISSUE_CATEGORIES["stress"]["en"])
        self.assertIsNone(self.db.get_active_session(1))

    async def test_cancel_admin_number_prompt(self):
        config.ADMIN_ID = 3
        await self.state(3).set_state(admin.AdminStates.blocking_user)
        await self.send(3, "/cancel")
        self.assertIsNone(await self.state(3).get_state())

    async def test_end_command_works_during_language_selection(self):
        await self.state(1).set_state(user.UserStates.waiting_for_language)
        await self.send(1, "/end")
        self.assertIsNone(self.db.get_active_session(1))
