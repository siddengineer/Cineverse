# """
# CineVerse Django Settings
# """
# import os
# from pathlib import Path
# from datetime import timedelta
# from dotenv import load_dotenv

# load_dotenv()

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-cineverse-dev-key-change-in-prod')
# DEBUG = os.environ.get('DEBUG', 'True') == 'True'
# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     # Third party
#     'rest_framework',
#     'rest_framework_simplejwt',
#     'corsheaders',
#     'django_filters',
#     # CineVerse apps
#     'movies',
#     'users',
#     'ai',
#     'lists',
#     'experience',
# ]

# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'cineverse.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'cineverse.wsgi.application'

# # Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# # Switch to PostgreSQL in production
# DATABASE_URL = os.environ.get('DATABASE_URL', '')
# if DATABASE_URL.startswith('postgresql://'):
#     import dj_database_url
#     DATABASES['default'] = dj_database_url.parse(DATABASE_URL)

# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# ]

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AUTH_USER_MODEL = 'users.User'

# # ─── REST Framework ───────────────────────────────────────────────────────────
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     ),
#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticatedOrReadOnly',
#     ),
#     'DEFAULT_FILTER_BACKENDS': [
#         'django_filters.rest_framework.DjangoFilterBackend',
#         'rest_framework.filters.SearchFilter',
#         'rest_framework.filters.OrderingFilter',
#     ],
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 20,
# }

# # ─── JWT ─────────────────────────────────────────────────────────────────────
# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
#     'ROTATE_REFRESH_TOKENS': True,
# }

# # ─── CORS ─────────────────────────────────────────────────────────────────────
# # CORS_ALLOWED_ORIGINS = os.environ.get(
# #     'CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173'
# # ).split(',')

# CORS_ALLOWED_ORIGINS = ['http://localhost:5500', 'http://127.0.0.1:5500']
# CORS_ALLOW_CREDENTIALS = True

# # ─── Cache (Redis) ────────────────────────────────────────────────────────────
# REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': REDIS_URL,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         },
#         'TIMEOUT': 300,  # 5 minutes default
#     }
# }

# # Fallback to local memory cache if redis not available
# try:
#     import django_redis  # noqa
# except ImportError:
#     CACHES = {
#         'default': {
#             'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         }
#     }

# # ─── Celery ──────────────────────────────────────────────────────────────────
# CELERY_BROKER_URL = REDIS_URL
# CELERY_RESULT_BACKEND = REDIS_URL
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'

# # ─── External APIs ────────────────────────────────────────────────────────────
# OMDB_API_KEY = os.environ.get('OMDB_API_KEY', '')
# GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

# # ─── Dataset paths ────────────────────────────────────────────────────────────
# TMDB_MOVIES_CSV = os.environ.get('TMDB_MOVIES_CSV', str(BASE_DIR / 'data' / 'tmdb_5000_movies.csv'))
# TMDB_CREDITS_CSV = os.environ.get('TMDB_CREDITS_CSV', str(BASE_DIR / 'data' / 'tmdb_5000_credits.csv'))
# INDIAN_MOVIES_CSV = os.environ.get('INDIAN_MOVIES_CSV', str(BASE_DIR / 'data' / 'indian_movies.csv'))

"""
CineVerse Django Settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-cineverse-dev-key-change-in-prod')
# 
DEBUG = False
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'rest_framework.authtoken',   # ← Token auth
    'corsheaders',
    'django_filters',

    # CineVerse apps
    'movies',
    'users',
    'ai',
    'lists',
    'experience',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'cineverse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend'],   # ← serves frontend/index.html
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cineverse.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgresql://'):
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# # Serve frontend JS/CSS as static files
# STATICFILES_DIRS = [BASE_DIR / 'frontend']

STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'   # for collectstatic in production

STATICFILES_DIRS = [
    BASE_DIR / 'static',   # Django looks here for static files in dev
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# REST Framework — Token Auth
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS — not needed when frontend is served by Django,
# but kept here in case you use Live Server during dev
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:5501',
    'http://127.0.0.1:5501',
]
CORS_ALLOW_CREDENTIALS = True

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# External APIs
OMDB_API_KEY = os.environ.get('OMDB_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

# Dataset paths
TMDB_MOVIES_CSV = os.environ.get('TMDB_MOVIES_CSV', str(BASE_DIR / 'data' / 'tmdb_5000_movies.csv'))
TMDB_CREDITS_CSV = os.environ.get('TMDB_CREDITS_CSV', str(BASE_DIR / 'data' / 'tmdb_5000_credits.csv'))
# INDIAN_MOVIES_CSV = os.environ.get('INDIAN_MOVIES_CSV', str(BASE_DIR / 'data' / 'indian_movies.csv'))
INDIAN_MOVIES_CSV = str(BASE_DIR / 'data' / 'indian_movies.csv')