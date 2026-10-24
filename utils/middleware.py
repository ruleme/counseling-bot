"""Private messages and cancellation are handled before role-specific states."""
from aiogram import BaseMiddleware


class PrivateChatMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if event.chat.type != "private":
            return
        text = event.text or ""
        command = text.split(maxsplit=1)[0].split("@", 1)[0] if text else ""
        if command == "/cancel":
            await data["state"].clear()
            await event.answer("Operation cancelled. Use /start or /counselor to continue. / ተሰርዟል። ለመቀጠል /start ይጠቀሙ።")
            return
        return await handler(event, data)
