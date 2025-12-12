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
        "👋 Здравствуйте!\n\n"
        ""
        "1. Нажмите на кнопку ниже\n"
        "2. Введите свои логин и пароль от «Встречалок» через пробел\n\n"
        "❓ Нужна помощь?\n"
        "Подробная информация есть в подсказке: /help\n\n"
        "📄 Важно знать:\n"
        "Используя нашего бота, вы автоматически соглашаетесь с:\n"
        "• Политикой обработки персональных данных\n"
        "• Условиями пользования\n"
        "Подробнее: /privacy",
        reply_markup=markup,
    )


async def help_tg(update, context):
    return await update.message.reply_text(
        "👋 Используя данный!\n\n"
        "🤝 Я создан, чтобы помочь вам удобно привязать ваш "
        "Telegram-аккаунт к сервису «Встречалки». "
        "Это позволит вам получать уведомления и быстро управлять"
        " встречами прямо здесь.\n\n"
        "🔐 **Какие данные мне нужны?**\n"
        "• 📧 **Логин** от вашего аккаунта в «Встречалках»\n"
        "• 🔑 **Пароль** от вашего аккаунта в «Встречалках»\n\n"
        "✅ **Что важно знать:**\n"
        "• Ваши данные используются только для безопасного подключения"
        " к «Встречалкам»\n"
        "• Мы никогда не храним ваш пароль в открытом виде\n"
        "• Все данные передаются по защищённому соединению\n"
        "• Привязывая аккаунт в Telegram к «Встречалкам», вы автоматиче"
        "ски соглашаетесь с тем,"
        "что Вам лично принадлежит данный Telegram-аккаунт\n"
        "• Бот имеет доступ только к информации, необходимой"
        " для уведомлений\n\n"
        "📝 **Как отправить данные?**\n"
        "Просто напишите мне:\n"
        "`логин пароль`\n\n"
        "Например:\n"
        "`user 1234`\n\n"
        "Готовы начать? 🚀",
        reply_markup=markup,
        parse_mode="Markdown",
    )


async def privacy(update, context):
    return await update.message.reply_text(
        "• Привязывая аккаунт в Telegram к «Встречалкам», Вы "
        "автоматически соглашаетесь с тем, "
        "что Вам лично принадлежит данный Telegram-аккаунт и аккаунт"
        " в «Встречалках», логин и пароль"
        " от которого Вы собираетесь ввести\n"
        "• Вы соглашаетесь на добавление в базу данных о Вас в сервисе "
        "«Встречалки» Вашего Telegram ID"
        "и номер телефона и на последующую обработку Ваших данных\n"
        "• Вы соглашаетесь с тем, что все Ваши действия в боте происходят"
        " осознано и не под"
        " давлением третьих лиц\n",
        reply_markup=markup,
        parse_mode="Markdown",
    )


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    conv_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(conv_handler)
    cont_handler = MessageHandler(filters.CONTACT, get_cont)
    application.add_handler(cont_handler)
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    privacy_handler = CommandHandler("privacy", privacy)
    application.add_handler(privacy_handler)
    privacy_handler = CommandHandler("help", help_tg)
    application.add_handler(privacy_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
