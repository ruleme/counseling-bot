"""Explicit media handling and bounded Telegram message sizes."""


def payload(message):
    if message.photo:
        return "photo", message.caption or "", message.photo[-1].file_id
    for kind in ("voice", "video", "document"):
        media = getattr(message, kind, None)
        if media:
            return kind, message.caption or "", media.file_id
    if message.text:
        return "text", message.text, None
    return None


async def deliver(bot, target, label, item, reply_markup=None):
    kind, content, file_id = item
    if kind != "text":
        await getattr(bot, "send_" + kind)(target, file_id, caption=label, reply_markup=reply_markup if not content else None)
    if content:
        # 1,800 Unicode code points fit even when each uses two UTF-16 units.
        for offset in range(0, len(content), 1800):
            await bot.send_message(target, label + "\n\n" + content[offset:offset + 1800],
                                   reply_markup=reply_markup if offset + 1800 >= len(content) else None)
