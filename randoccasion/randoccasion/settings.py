__all__ = ()

import os
from pathlib import Path

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fake")


def load_bool_env(name, default):
    env_value = os.getenv(name, str(default)).lower()

    return env_value.lower() in ("true", "1", "yes", "y", "t", "")


DEBUG = load_bool_env("DJANGO_DEBUG", False)

ALLOWED_HOSTS_ENV = os.getenv("DJANGO_ALLOWED_HOSTS", "")
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(",")]
else:
    ALLOWED_HOSTS = ["localhost"] if DEBUG else [""]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "homepage.apps.HomepageConfig",
    "sorl.thumbnail",
    "events.apps.EventsConfig",
    "users.apps.UsersConfig",
    "django_ckeditor_5",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "users.middleware.UserMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    INSTALLED_APPS += ["debug_toolbar"]
    INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "randoccasion.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "events.context_processors.get_ymaps_token",
            ],
        },
    },
]

WSGI_APPLICATION = "randoccasion.wsgi.application"

AUTH_USER_MODEL = "users.CustomUser"
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"

DEFAULT_USER_IS_ACTIVE = load_bool_env(
    "DJANGO_DEFAULT_USER_IS_ACTIVE",
    DEBUG,
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation"
        ".MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation"
        ".CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation"
        ".NumericPasswordValidator",
    },
]
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "ru-RU")
LANGUAGES = [
    ("ru", _("Russian")),
    ("en", _("English")),
]
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static_dev",
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "blockQuote",
            "imageUpload",
            "fontColor",
            "fontBackgroundColor",
            "bulletedList",
            "numberedList",
            "todoList",
            "outdent",
            "indent",
        ],
    },
}
CKEDITOR_5_CUSTOM_CSS = "css/ckeditor5/admin_dark.css"
CKEDITOR_5_UPLOAD_PATH = "uploads/"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("DJANGO_EMAIL_HOST", "smtp.yandex.ru")
EMAIL_HOST_USER = os.getenv("DJANGO_MAIL")
EMAIL_HOST_PASSWORD = os.getenv("DJANGO_EMAIL_PASSWORD")
EMAIL_PORT = os.getenv("DJANGO_EMAIL_PORT", 465)
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_MAIL")
SERVER_EMAIL = os.getenv("DJANGO_MAIL")

YMAPS_API = os.getenv("YANDEX_MAPS_API_TOKEN")

AUTHENTICATION_BACKENDS = [
    "users.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

MAX_AUTH_ATTEMPTS = int(os.getenv("DJANGO_MAX_AUTH_ATTEMPTS", default=3))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}
