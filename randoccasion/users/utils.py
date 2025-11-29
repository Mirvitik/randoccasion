__all__ = ()

import asyncio

from telegram import Bot

from django.db.models import Q

from users.models import User
from randoccasion.settings import TELEGRAM_BOT_TOKEN


async def send_tg_message(tg_id, message):
    bot = Bot(TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=tg_id, text=message)
    except Exception:
        pass


def send_tg_message_sync(tg_id, message):
    return asyncio.run(send_tg_message(tg_id, message))


def q_search(query):
    if query.isdigit():
        return User.objects.filter(id=query)

    if "@" in query:
        user = User.objects.by_mail(query)
        if user:
            return User.objects.filter(id=user.id)

        return User.objects.none()

    keywords = [word for word in query.split() if word]

    q_objects = Q()

    for token in keywords:
        q_objects |= Q(username__icontains=token)
        q_objects |= Q(first_name__icontains=token)
        q_objects |= Q(last_name__icontains=token)
        q_objects |= Q(email__icontains=token)
        q_objects |= Q(profile__interests__name__icontains=token)

    return User.objects.filter(q_objects)
