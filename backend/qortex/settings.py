"""
Django settings for qortex project.

Configuration is driven by environment variables loaded from a .env file
(see .env.example). Database is resolved via dj-database-url so the same
settings work for local PostgreSQL and Docker PostgreSQL.
"""

import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Load variables from backend/.env if present (local dev).
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-ga#q228se-_!28w%%rs+lyxg96552+58%e8612)tk!p7g#j1oa"
    else:
        raise RuntimeError("DJANGO_SECRET_KEY must be set when DEBUG=False")

_allowed_hosts_env = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(",") if h.strip()]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    # Local
    "musiq_catalog",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "qortex.urls"

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

WSGI_APPLICATION = "qortex.wsgi.application"


# Database
# Resolved from DATABASE_URL. Falls back to a local PostgreSQL connection
# (qortex user/db on localhost:5432) so `runserver` works without extra config.
# In Docker, DATABASE_URL is provided by docker-compose env vars.

_default_db_url = os.environ.get(
    "DATABASE_URL",
    "postgres://qortex:qortex@localhost:5432/qortex",
)
DATABASES = {
    "default": dj_database_url.parse(_default_db_url, conn_max_age=600, conn_health_checks=True),
}


# Caching
# Redis is used when REDIS_URL is set (Docker / production).
# Falls back to LocMemCache for local dev (note: throttle counts are per-process
# with LocMemCache, so the effective limit is multiplied by the worker count).

if os.environ.get("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": os.environ["REDIS_URL"],
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "throttle-cache",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Security hardening (production only, not during tests)

TESTING = "test" in sys.argv

if not DEBUG and not TESTING:
    _ssl_redirect = os.environ.get("DJANGO_SSL_REDIRECT", "false").lower() in ("true", "1", "yes")
    SECURE_SSL_REDIRECT = _ssl_redirect
    SECURE_REDIRECT_EXEMPT = [r"^health/$"]
    SESSION_COOKIE_SECURE = _ssl_redirect
    CSRF_COOKIE_SECURE = _ssl_redirect
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    if _ssl_redirect:
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Django REST Framework
# No authentication: the catalog API is fully open for read & write.

_default_renderer_classes = [
    "rest_framework.renderers.JSONRenderer",
]
if DEBUG:
    _default_renderer_classes.append("rest_framework.renderers.BrowsableAPIRenderer")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": _default_renderer_classes,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "qortex.pagination.CatalogPagination",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "NUM_PROXIES": int(os.environ.get("DJANGO_NUM_PROXIES", "1")),
    "SEARCH_PARAM": "search",
    "ORDERING_PARAM": "ordering",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Qortex Music Catalog API",
    "DESCRIPTION": "CRUD API for managing artists, albums, and songs.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# CORS
# Allow the Vue dev server and the containerized frontend (nginx on :80).
# Additional origins can be configured via DJANGO_CORS_ORIGINS env var
# (comma-separated, e.g. "https://app.example.com,https://admin.example.com").

_default_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "http://localhost",
    "http://127.0.0.1",
]

_extra_cors = os.environ.get("DJANGO_CORS_ORIGINS", "")
if _extra_cors:
    _default_cors_origins.extend(origin.strip() for origin in _extra_cors.split(",") if origin.strip())

CORS_ALLOWED_ORIGINS = _default_cors_origins


# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
        },
        "musiq_catalog": {
            "handlers": ["console"],
            "level": os.environ.get("MUSIQ_LOG_LEVEL", "INFO"),
        },
    },
}
