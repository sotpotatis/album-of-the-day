"""
Django settings for album_of_the_day project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os, cx_Oracle, logging
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)
LOGGING_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "critical": logging.CRITICAL,
}
logging.basicConfig(
    level=LOGGING_LEVELS[os.environ.get("LOGGING_LEVEL", "info").lower()]
)
from expand_files_from_environment import expand_files

expand_files()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "django.db.backends.postgresql")
# Some database connection optimizations.
# Set the max age to 0 by default so that Django doesn't preserve database connections.
CONN_MAX_AGE = int(os.environ.get("DATABASE_CONNECTION_AGE", 0))
# Enable connection health checks by default. From the Django documentation:
# "If set to True, existing persistent database connections
# will be health checked before they are reused in each request performing database access.
# If the health check fails, the connection will be reestablished without failing the request
# when the connection is no longer usable but the database server is ready to accept and '
# serve new connections (e.g. after database server restart closing existing connections)."
CONN_HEALTH_CHECKS = bool(os.environ.get("DATABASE_HEALTH_CHECKS", True))
DATABASE_OPTIONS = {}
if DATABASE_ENGINE == "django.db.backends.oracle":
    ORACLE_DATABASE_CONFIG_DIR = os.environ.get(
        "ORACLE_DATABASE_WALLET_PATH", os.path.join(os.getcwd(), ".wallet")
    )
    if not os.path.exists(ORACLE_DATABASE_CONFIG_DIR):
        raise FileNotFoundError(
            f"""The wallet file path {ORACLE_DATABASE_CONFIG_DIR} does not exist. 
        It must exist to make the database connection possible."""
        )
    # If using the Oracle Cloud database, you can set an ORACLE_DATABASE_CLIENT_PATH variable
    # to specify where you have installed the library, if you don't want to add it to
    # path or is unable to get it to work (like me)
    cx_Oracle.init_oracle_client(
        lib_dir=os.environ.get("ORACLE_DATABASE_CLIENT_PATH", None),
        config_dir=ORACLE_DATABASE_CONFIG_DIR,
    )

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get("DJANGO_DEBUG", False))
if DEBUG:
    logger.warning("Debug mode is active - do not use in production!")

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "DJANGO_CSRF_ORIGINS", "http://localhost,http://127.0.0.1"
).split(",")
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",  # Filter for API
    "rest_framework",
    "rest_framework.authtoken",  # Use auth in form of tokens
    "filters",  # Additional filters for API
    "website",
    "corsheaders",  # For CORS
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Allow serving static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"  # Use WhiteNoise's caching & compression

ROOT_URLCONF = "album_of_the_day.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "album_of_the_day.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,
        "NAME": os.environ.get("DATABASE_NAME", None),
        "USER": os.environ["DATABASE_USER"],
        "PASSWORD": os.environ["DATABASE_PASSWORD"],
        "HOST": os.environ.get("DATABASE_HOST", None),
        "PORT": os.environ.get("DATABASE_PORT", None),
        "OPTIONS": {**DATABASE_OPTIONS},
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Django-REST configuration
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    # Note: default filtering backends are set individually on each view, see views.py.
    "DEFAULT_PAGINATION_CLASS": "album_of_the_day.rest_framework_settings.PaginationSettings",
}


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "sv-se"

TIME_ZONE = os.environ.get("TIMEZONE", "Europe/Stockholm")

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    f"{BASE_DIR}/static",
]
FILE_PATH = os.path.realpath(__file__)
FILE_DIRECTORY = os.path.dirname(FILE_PATH)
STATIC_ROOT = os.path.join(FILE_DIRECTORY, "static")
SESSION_SAVE_EVERY_REQUEST = True  # Save sessions on every request
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True  # To prevent access from JavaScript
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
