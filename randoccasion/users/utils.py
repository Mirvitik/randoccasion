__all__ = ()

import asyncio

from telegram import Bot

from randoccasion.settings import TELEGRAM_BOT_TOKEN


async def send_tg_message(tg_id, message):
    bot = Bot(TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=tg_id, text=message)
    except Exception:
        pass


def send_tg_message_sync(tg_id, message):
    return asyncio.run(send_tg_message(tg_id, message))
