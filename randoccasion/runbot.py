__all__ = ()

import logging
import os

from asgiref.sync import sync_to_async
import django
from django.contrib.auth.hashers import check_password
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
)

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

TEXTS = {
    "ru": {
        "start": "👋 Здравствуйте!\n\nВыберите язык / Choose language",
        "welcome": "👋 Здравствуйте!\n\n"
        "1. Нажмите на кнопку ниже\n"
        "2. Введите свои логин и пароль от «Встречалок» через пробел\n\n"
        "❓ Нужна помощь?\n"
        "Подробная информация есть в подсказке: /help\n\n"
        "📄 Важно знать:\n"
        "Используя нашего бота, вы автоматически соглашаетесь с:\n"
        "• Политикой обработки персональных данных\n"
        "• Условиями пользования\n"
        "Подробнее: /privacy",
        "help": "👋 Используя данный!\n\n"
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
        "privacy": "• Привязывая аккаунт в Telegram к «Встречалкам», Вы "
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
        "phone_button": "Поделиться номером",
        "phone_request": "Поделитесь своим номером телефона"
        " с нами\nПожалуйста",
        "phone_received": "Ваш телефон: {}\n"
        'Теперь введите ваш ник и пароль на "Встречалках"\n'
        "Через пробел",
        "already_linked": "Ваш аккаунт уже связан с каким-то профилем",
        "success": "Поздравляем, ваш номер привязан к аккаунту!\n"
        "Мы рекомендуем Вам удалить сообщение с логином "
        "и паролем для конфиденциальности Ваших данных",
        "wrong_password": "Неверный пароль",
        "user_not_found": (
            "Пользователя с таким именем нет\nПроверьте корректность ника"
        ),
        "share_contact": "Поделиться номером",
    },
    "en": {
        "start": "👋 Hello!\n\nChoose language / Выберите язык",
        "welcome": "👋 Hello!\n\n"
        "1. Click the button below\n"
        "2. Enter your «Randoccasion» login and password"
        " separated by space\n\n"
        "❓ Need help?\n"
        "Detailed information is in the hint: /help\n\n"
        "📄 Important to know:\n"
        "By using our bot, you automatically agree to:\n"
        "• Personal data processing policy\n"
        "• Terms of use\n"
        "More details: /privacy",
        "help": "👋 Using this!\n\n"
        "🤝 I was created to help you conveniently link your "
        "Telegram account to the «Randoccasion» service. "
        "This will allow you to receive notifications and quickly manage"
        " meetings right here.\n\n"
        "🔐 **What data do I need?**\n"
        "• 📧 **Login** from your «Randoccasion» account\n"
        "• 🔑 **Password** from your «Randoccasion» account\n\n"
        "✅ **What's important to know:**\n"
        "• Your data is used only for secure connection to «Randoccasion»\n"
        "• We never store your password in plain text\n"
        "• All data is transmitted over a secure connection\n"
        "• By linking your Telegram account to"
        " «Randoccasion», you automatically agree"
        " that you personally own this Telegram account\n"
        "• The bot only has access to "
        "information necessary for notifications\n\n"
        "📝 **How to send data?**\n"
        "Just write to me:\n"
        "`login password`\n\n"
        "For example:\n"
        "`user 1234`\n\n"
        "Ready to start? 🚀",
        "privacy": "• By linking your Telegram account to «Randoccasion», you "
        "automatically agree that you personally own this Telegram account "
        "and the «Randoccasion» account whose login and password "
        "you are about to enter\n"
        "• You agree to add your Telegram ID and phone number "
        "to the database about you in the «Randoccasion» service "
        "and to subsequent processing of your data\n"
        "• You agree that all your actions in the bot are performed "
        "consciously and not under pressure from third parties\n",
        "phone_button": "Share phone number",
        "phone_request": "Please share your phone number with us",
        "phone_received": "Your phone: {}\n"
        'Now enter your nickname and password on "Randoccasion"\n'
        "Separated by space",
        "already_linked": "Your account is already linked to some profile",
        "success": "Congratulations, your number is linked to the account!\n"
        "We recommend that you delete the message with your login "
        "and password for the confidentiality of your data",
        "wrong_password": "Wrong password",
        "user_not_found": (
            "User with this name does not"
            " exist\nCheck the nickname correctness"
        ),
        "share_contact": "Share phone number",
    },
}


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


async def echo(update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get("language", "ru")

    if "language" not in context.user_data:
        await update.message.reply_text(
            TEXTS["ru"]["start"],
            reply_markup=get_language_keyboard(),
        )
        return

    pr = await get_user_by_username(update.message.text.split()[0])
    if pr and len(update.message.text.split()) == 2:
        if context.user_data.get("phone") is not None:
            if await is_tg_verified(telegram_id=context.user_data["id"]):
                await update.message.reply_text(
                    TEXTS[user_lang]["already_linked"],
                    reply_markup=get_phone_keyboard(user_lang),
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
                    TEXTS[user_lang]["success"],
                    reply_markup=get_phone_keyboard(user_lang),
                )
            else:
                await update.message.reply_text(
                    TEXTS[user_lang]["wrong_password"],
                    reply_markup=get_phone_keyboard(user_lang),
                )
        else:
            await update.message.reply_text(
                TEXTS[user_lang]["phone_request"],
                reply_markup=get_phone_keyboard(user_lang),
            )
    else:
        await update.message.reply_text(
            TEXTS[user_lang]["user_not_found"],
            reply_markup=get_phone_keyboard(user_lang),
        )


async def get_cont(update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get("language", "ru")
    context.user_data["phone"] = update.message.contact.phone_number
    context.user_data["id"] = update.message.contact.user_id
    return await update.message.reply_text(
        TEXTS[user_lang]["phone_received"].format(
            update.message.contact.phone_number,
        ),
        reply_markup=ReplyKeyboardRemove(),
    )


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    if "language" in context.user_data:
        user_lang = context.user_data["language"]
        await update.message.reply_text(
            TEXTS[user_lang]["welcome"],
            reply_markup=get_phone_keyboard(user_lang),
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            TEXTS["ru"]["start"],
            reply_markup=get_language_keyboard(),
            parse_mode="Markdown",
        )


async def language_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    language = query.data.split("_")[1]
    context.user_data["language"] = language

    await query.edit_message_text(
        "✅ Language selected / Язык выбран: "
        f"{'Русский' if language == 'ru' else 'English'}\n\n"
        "Use /start to begin / Используйте /start для начала",
    )

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=TEXTS[language]["welcome"],
        reply_markup=get_phone_keyboard(language),
        parse_mode="Markdown",
    )


async def help_tg(update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get("language", "ru")
    return await update.message.reply_text(
        TEXTS[user_lang]["help"],
        reply_markup=get_phone_keyboard(user_lang),
        parse_mode="Markdown",
    )


async def privacy(update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get("language", "ru")
    return await update.message.reply_text(
        TEXTS[user_lang]["privacy"],
        reply_markup=get_phone_keyboard(user_lang),
        parse_mode="Markdown",
    )


def get_language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_phone_keyboard(language="ru"):
    reply_keyboard = [
        [
            KeyboardButton(
                TEXTS[language]["phone_button"],
                request_contact=True,
            ),
        ],
    ]
    return ReplyKeyboardMarkup(
        reply_keyboard,
        one_time_keyboard=False,
        resize_keyboard=True,
    )


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(
        CallbackQueryHandler(language_callback, pattern="^lang_"),
    )

    conv_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(conv_handler)

    cont_handler = MessageHandler(filters.CONTACT, get_cont)
    application.add_handler(cont_handler)

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    privacy_handler = CommandHandler("privacy", privacy)
    application.add_handler(privacy_handler)

    help_handler = CommandHandler("help", help_tg)
    application.add_handler(help_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
