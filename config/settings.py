import mimetypes
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# JWT 토큰 만료 시간
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME", 30))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME", 7))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
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
    "apps.support.apps.SupportConfig",
    # 서드파티 앱
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_yasg",
    "storages",
    # 소셜로그인 서드파티
    "django.contrib.sites",
]

# REST Framework 설정
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.users.middleware.CookieJWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # 검색 기능 django-filter 사용
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS 헤더 설정
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

# 커스텀 유저 모델
AUTH_USER_MODEL = "users.User"

# 로그인/로그아웃 URL
LOGIN_URL = "/api/user/login/"
LOGIN_REDIRECT_URL = "/"
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
CORS_ALLOW_CREDENTIALS = True


# Swagger 설정
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,  # Session 인증 버튼 숨김
    "DEFAULT_API_URL": os.getenv("SWAGGER_API_URL", "http://localhost:8000/api/"),
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

# email 인증을 위한 환경변수 세팅
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

# 제미나이 API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# SESSION_COOKE_* 설정은 Django 세션 쿠키에만 적용 -> set_cookie로 직접 굽는 경우 적용 안 됨
# SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() in ("true", "1", "yes")
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SAMESITE = "None"
# CSRF_COOKIE_SECURE = True

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() in ("true", "1", "yes")
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "Lax")

FRONT_BASE_URL = os.getenv("FRONT_BASE_URL", "http://localhost:5173")

# admin 페이지 접근하기 위한
CSRF_TRUSTED_ORIGINS = [
    "https://lov2ly.kro.kr",
]

# S3 버킷 정보
AWS_STORAGE_BUCKET_NAME = "oz-main-be-12-team2"  # 버킷 이름
AWS_S3_REGION_NAME = "ap-northeast-2"  # 서울 리전

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)

# 기본 파일 저장소를 S3로 지정
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# URL (이미지 접근용)
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
