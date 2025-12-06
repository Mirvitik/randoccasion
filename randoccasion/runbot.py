__all__ = ()

import logging
import os

from asgiref.sync import sync_to_async
import django
from django.contrib.auth.hashers import check_password
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, filters, MessageHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "randoccasion.settings")
django.setup()

from randoccasion.settings import TELEGRAM_BOT_TOKEN  # noqa
from users.models import Profile, User  # noqa

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    filename="tglog.log",
)
logger = logging.getLogger(__name__)

reply_keyboard = [[KeyboardButton("Поделиться номером", request_contact=True)]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


@sync_to_async
def get_user_by_username(username):
    try:
        return User.objects.get(username=username)
    except Exception:
        return None


@sync_to_async
def log_in_by_pass(username, password, telephone, telegram_id):
    try:
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            pr = Profile.objects.get(user=user)
            pr.telephone = int(telephone)
            pr.telegram_id = int(telegram_id)
            pr.save()
            return True

        return False
    except User.DoesNotExist:
        return False
    except Exception:
        return False


@sync_to_async
def is_tg_verified(telegram_id):
    try:
        Profile.objects.get(telegram_id=telegram_id)
        return True
    except Profile.DoesNotExist:
        return False
    except Exception:
        return False


async def echo(update, context):
    pr = await get_user_by_username(update.message.text.split()[0])
    if pr and len(update.message.text.split()) == 2:
        if context.user_data["phone"] is not None:
            if await is_tg_verified(telegram_id=context.user_data["id"]):
                await update.message.reply_text(
                    "Ваш аккаунт уже связан с каким-то профилем",
                    reply_markup=markup,
                )

                return

            flag = await log_in_by_pass(
                username=update.message.text.split()[0],
                password=update.message.text.split()[1],
                telephone=context.user_data["phone"],
                telegram_id=context.user_data["id"],
            )
            if flag:
                await update.message.reply_text(
                    "Поздравляем, ваш номер привязан к аккаунту!",
                    reply_markup=markup,
                )
            else:
                await update.message.reply_text(
                    "Неверный пароль",
                    reply_markup=markup,
                )
        else:
            await update.message.reply_text(
                "Поделитесь своим номером телефона с нами\nПожалуйста",
                reply_markup=markup,
            )
    else:
        await update.message.reply_text(
            "Пользователя с таким именем нет\nПроверьте корректность ника",
            reply_markup=markup,
        )


async def get_cont(update, context):
    context.user_data["phone"] = update.message.contact.phone_number
    context.user_data["id"] = update.message.contact.user_id
    return await update.message.reply_text(
        f"Ваш телефон: {update.message.contact.phone_number}\n"
        'Теперь введите ваш ник и пароль на "Встречалках"\n'
        "Через пробел",
    )


async def start(update, context):
    return await update.message.reply_text(
        "Здравствуйте, нажмите на кнопку, а затем введите "
        "свои логин и пароль от 'Встречалок' через пробел",
        reply_markup=markup,
    )


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    conv_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(conv_handler)
    cont_handler = MessageHandler(filters.CONTACT, get_cont)
    application.add_handler(cont_handler)
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
