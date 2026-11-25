import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env(name, default):
    value = os.getenv(name)
    return value if value else default


def _env_list(name, default):
    return [item.strip() for item in _env(name, default).split(",") if item.strip()]


SECRET_KEY = _env("SECRET_KEY", "keypass-dev-secret-key-change-me-0123456789")
DEBUG = _env("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")

INSTALLED_APPS = [
    "corsheaders",
    "rest_framework",
    "accounts",
    "transitions",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = []
DATABASES = {}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_TZ = True

CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8080")

MONGO_URI = _env("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = _env("MONGO_DB_NAME", "keypass")
MONGO_SERVER_TIMEOUT_MS = int(_env("MONGO_SERVER_TIMEOUT_MS", "3000"))

OPENAI_API_KEY = _env("OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = _env("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = _env("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
OPENAI_MODEL = _env("OPENAI_MODEL", "gpt-5.6-sol")
OPENAI_TIMEOUT_SECONDS = float(_env("OPENAI_TIMEOUT_SECONDS", "60"))

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(_env("JWT_EXPIRY_HOURS", "12"))

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["core.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
}
