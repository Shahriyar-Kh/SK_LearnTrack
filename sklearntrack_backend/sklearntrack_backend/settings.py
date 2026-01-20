# FILE: sklearntrack_backend/settings.py - COMPLETE FIX
# ============================================================================

import os
from pathlib import Path
from datetime import timedelta


from decouple import config
import dj_database_url  # ADD THIS LINE
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# Create static directory if it doesn't exist (fix for the warning)
os.makedirs(BASE_DIR / 'static', exist_ok=True)

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key-for-dev')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1,.onrender.com,sk-learntrack-pkw6.onrender.com',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
# Add Render hostname if exists
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application Definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',
    
    # Local apps
    'accounts',
    'courses',
    'notes',
    'roadmaps',
    'analytics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sklearntrack_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'sklearntrack_backend.wsgi.application'


# Database Configuration - FIXED VERSION
# Try to get DATABASE_URL from environment, fallback to SQLite
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Parse the DATABASE_URL for PostgreSQL or other external databases
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    # Fallback to SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Create directories if they don't exist
os.makedirs(MEDIA_ROOT / 'avatars', exist_ok=True)
os.makedirs(MEDIA_ROOT / 'notes/images', exist_ok=True)
os.makedirs(MEDIA_ROOT / 'notes/pdfs', exist_ok=True)

# Custom User Model - CRITICAL
AUTH_USER_MODEL = 'accounts.User'

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',  # Custom email backend
    'django.contrib.auth.backends.ModelBackend',  # Fallback
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}
# ============================================================================
# JWT SETTINGS - ENHANCED WITH CUSTOM CLAIMS
# ============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    # Custom token claims
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    # These will be added automatically by our serializer
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
}


# CORS Settings
# CORS Settings for production and development
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True  # Only in development
else:
    CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://sk-learntrack.vercel.app",
    "https://sk-learntrack-pkw6.onrender.com",
]

# Add origins from environment
env_origins = config('CORS_ALLOWED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
CORS_ALLOWED_ORIGINS.extend(env_origins)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
#  CRITICAL: Include all necessary headers for OAuth
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'access-control-allow-credentials',
    'access-control-allow-origin',
]

#  Allow preflight requests to be cached
CORS_PREFLIGHT_MAX_AGE = 86400


# =============== EMAIL CONFIGURATION =================
# Frontend URL for email links
FRONTEND_URL = config('FRONTEND_URL', default='https://sk-learntrack.vercel.app')

# Email Configuration - PRODUCTION FIX
# Use console backend if no email credentials (for Render free tier testing)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Default to console

# Only use SMTP if credentials are provided
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# If email credentials are provided, use SMTP
if EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
    logger.info("✅ Using SMTP email backend for production")
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    logger.info("⚠️ Using console email backend - no email credentials configured")
    logger.info("ℹ️ For production, set EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD")

# Email timeout to prevent hanging
EMAIL_TIMEOUT = 10  # 10 seconds timeout
        
# # Celery Configuration
# CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
# CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = TIME_ZONE

# AI Configuration (Groq API)
GROQ_API_KEY = config('GROQ_API_KEY', default='')
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

AI_SETTINGS = {
    'DEFAULT_MODEL': 'llama-3.3-70b-versatile',
    'MAX_TOKENS': 2000,
    'TEMPERATURE': 0.7,
    'CACHE_TIMEOUT': 3600,
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']

# ============================================================================
# LOGGING - ENHANCED FOR OAUTH DEBUGGING
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Debug level for auth issues
            'propagate': False,
        },
        'google.auth': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Debug level for Google OAuth
            'propagate': False,
        },
    },
}

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# Default Auto Field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Session settings
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'sklearntrack_sessionid'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_SAMESITE = 'Lax'

# Only set secure in production
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False



# Add at the bottom of settings.py
# Custom 404 handler
def custom_404(request, exception=None):
    from django.http import JsonResponse
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found on this server.',
        'status_code': 404,
        'available_endpoints': {
            'root': '/',
            'admin': '/admin/',
            'token_obtain': '/api/token/',
            'token_refresh': '/api/token/refresh/',
            'auth': '/api/auth/',
            'courses': '/api/courses/',
            'notes': '/api/',
            'roadmaps': '/api/roadmaps/',
            'analytics': '/api/analytics/',
        }
    }, status=404)

# Add this to settings.py
handler404 = 'sklearntrack_backend.settings.custom_404'

# ============================================================================
# GOOGLE OAUTH CONFIGURATION
# ============================================================================

# Google OAuth - MUST be configured in production
GOOGLE_OAUTH_CLIENT_ID = config('GOOGLE_OAUTH_CLIENT_ID', default='')
GOOGLE_OAUTH_CLIENT_SECRET = config('GOOGLE_OAUTH_CLIENT_SECRET', default='')

# Validate Google OAuth configuration
if not GOOGLE_OAUTH_CLIENT_ID or GOOGLE_OAUTH_CLIENT_ID == 'your-google-client-id.apps.googleusercontent.com':
    logger.warning("Google OAuth Client ID is not configured. Google authentication will not work.")
else:
    logger.info(f"Google OAuth configured with Client ID: {GOOGLE_OAUTH_CLIENT_ID[:20]}...")

# Google OAuth Redirect URI (used for some OAuth flows)
GOOGLE_OAUTH_REDIRECT_URI = config(
    'GOOGLE_OAUTH_REDIRECT_URI', 
    default='http://localhost:8000/auth/google/callback/'
)


# ============================================================================
# PRODUCTION FIXES FOR RENDER
# ============================================================================

# Gunicorn settings for Render free tier
GUNICORN_CONFIG = {
    'workers': 1,  # Use only 1 worker to avoid memory issues
    'timeout': 120,  # Increase timeout to 120 seconds
    'keepalive': 5,
}

# Database connection optimization for PostgreSQL on Render
if DATABASE_URL and 'postgres' in DATABASE_URL:
    DATABASES['default']['CONN_MAX_AGE'] = 60  # Reduce to 60 seconds
    DATABASES['default']['OPTIONS'] = {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
    }
    logger.info("✅ PostgreSQL database configuration optimized for Render")

# Security headers for production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
    logger.info("✅ Production security headers enabled")