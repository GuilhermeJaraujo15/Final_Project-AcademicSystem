import os
from pathlib import Path
import dj_database_url
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
if not DEBUG and SECRET_KEY == "unsafe-development-key-change-me":
    raise RuntimeError("Set DJANGO_SECRET_KEY to a strong secret outside development.")
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
INSTALLED_APPS = ["django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "rest_framework", "django_filters", "drf_spectacular", "apps.accounts", "apps.academics", "apps.insights", "apps.preview"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates", "DIRS":[BASE_DIR / "templates"], "APP_DIRS":True, "OPTIONS":{"context_processors":["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages", "apps.preview.context_processors.demo_context"]}}]
WSGI_APPLICATION = "config.wsgi.application"
DEMO_MODE = os.getenv("ACADEMIC_DEMO_MODE", "false").lower() == "true"
if DEMO_MODE:
    # Explicit preview-only backend. Preview routes never query or persist through it.
    DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}
else:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required. Configure PostgreSQL; SQLite fallback is intentionally disabled.")
    DATABASES = {"default": dj_database_url.parse(url, conn_max_age=60, ssl_require=(not DEBUG))}
    if os.getenv("MIGRATION_DATABASE_URL"):
        DATABASES["default"] = dj_database_url.parse(os.environ["MIGRATION_DATABASE_URL"], conn_max_age=0, ssl_require=True)
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [{"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},{"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},{"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
REST_FRAMEWORK = {"DEFAULT_PERMISSION_CLASSES":["rest_framework.permissions.IsAuthenticated"], "DEFAULT_AUTHENTICATION_CLASSES":["rest_framework.authentication.SessionAuthentication"], "DEFAULT_FILTER_BACKENDS":["django_filters.rest_framework.DjangoFilterBackend", "rest_framework.filters.SearchFilter", "rest_framework.filters.OrderingFilter"], "DEFAULT_SCHEMA_CLASS":"drf_spectacular.openapi.AutoSchema", "DEFAULT_PAGINATION_CLASS":"rest_framework.pagination.PageNumberPagination", "PAGE_SIZE":25}
SPECTACULAR_SETTINGS = {"TITLE":"API Gestão Acadêmica", "VERSION":"1.0.0", "SERVE_INCLUDE_SCHEMA":False}
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
