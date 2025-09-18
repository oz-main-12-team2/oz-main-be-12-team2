import mimetypes
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# JWT 토큰 만료 시간
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME", 30))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME", 7))),
}

# .env 파일 로드
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 보안 키
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-default-key")

# 디버그 모드 - 환경변수에서 DEBUG 값을 주지 않으면 자동으로 FALSE
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# 허용 호스트
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost 127.0.0.1 0.0.0.0").split()

# 앱 설정
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 프로젝트 앱
    "apps.orders.apps.OrdersConfig",
    "apps.users.apps.UsersConfig",
    "apps.products.apps.ProductsConfig",
    "apps.carts.apps.CartsConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.stats.apps.StatsConfig",
    # 서드파티 앱
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    # 소셜로그인 서드파티
    "django.contrib.sites",
]

# REST Framework 설정
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 데이터베이스
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "postgres"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Static / Media 파일 설정
STATIC_URL = os.getenv("STATIC_URL", "/static/")
STATIC_ROOT = os.getenv("STATIC_ROOT", BASE_DIR / "staticfiles")

# 개발환경에서는 정적 파일 직접 서빙할 수 있도록 DIRS 추가
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", BASE_DIR / "media")


# 커스텀 유저 모델
AUTH_USER_MODEL = "users.User"

# 로그인/로그아웃 URL
LOGIN_URL = "/api/user/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/api/user/login/"

# Swagger UI가 static 파일을 정상적으로 불러오기 위해 MIME 추가
if DEBUG:
    mimetypes.add_type("application/javascript", ".js", True)
    mimetypes.add_type("text/css", ".css", True)

SITE_ID = 1

# 개발환경용 사이트 도메인
SITE_DOMAIN = "localhost:8000"
SITE_NAME = "Local Development"


# CORS 설정
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000 http://127.0.0.1:3000").split()


# Swagger 설정
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT 인증 (예: Bearer <your_token>)",
        }
    },
    "USE_SESSION_AUTH": False,  # Session 인증 버튼 숨김
}

# OAuth 콜백 URL
GOOGLE_CALLBACK_URL = "http://localhost:8000/api/user/google/callback/"
NAVER_CALLBACK_URL = "http://localhost:8000/api/user/naver/callback/"

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
