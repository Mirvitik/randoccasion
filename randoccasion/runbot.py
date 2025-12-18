__all__ = ()

import logging
import os

from asgiref.sync import sync_to_async
from botconstants import INTERTEXTS
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

TEXTS = INTERTEXTS


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

    language_names = {
        "ru": "Русский",
        "en": "English",
        "fr": "Français",
        "es": "Español",
        "de": "Deutsch",
    }

    await query.edit_message_text(
        "✅ Language selected / Язык выбран: "
        f"{language_names[language]}\n\n"
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
            InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"),
        ],
        [
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
            InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
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
