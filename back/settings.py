from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = [
    "sternhalma.onrender.com",
    "127.0.0.1",
    "cchecker-backend.onrender.com",
]
render_external_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_external_hostname:
    ALLOWED_HOSTS.append(render_external_hostname)

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "game",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # deploy in product
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "back.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "front/dist")],  # nach index.html suchen
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "back.wsgi.application"
ASGI_APPLICATION = "back.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "bjv43dmw65b7obui857u",
        "USER": "uwss14x03ljxhvrjdqvo",
        "PASSWORD": os.environ.get("DB_PASSWORD"),  # on render
        "HOST": "bjv43dmw65b7obui857u-postgresql.services.clever-cloud.com",
        "PORT": "50013",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
# STATIC_URL = "assets/"
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "front/dist/assets")]
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # deploy in product
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS_ALLOWED_ORIGINS = [
#     # "http://localhost:5173",
#     # "http://127.0.0.1:5173",
#     "*"
# ]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# SESSION_ENGINE = 'django.contrib.sessions.backends.file'
# SESSION_FILE_PATH = '/tmp'

# SESSION_ENGINE = 'django.contrib.sessions.backends.cache' # default: django.contrib.sessions.models.Session
# SESSION_CACHE_ALIAS = 'default'
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#     }
# }
# SESSION_COOKIE_SECURE = False  # True for HTTPS only
# SESSION_COOKIE_HTTPONLY = True
# SESSION_SAVE_EVERY_REQUEST = True  # Save the session on every request
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False
