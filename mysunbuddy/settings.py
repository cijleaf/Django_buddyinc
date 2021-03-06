"""
Django settings for mysunbody project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import ast
import os

import dwollav2 as dwolla

try:
    from mysunbuddy.secure_settings import SECURE_SETTINGS
except ImportError:
    SECURE_SETTINGS = {}


def get_var(name, default=None):
    """Return the settings in a precedence way with default."""
    try:
        value = os.environ.get(name, SECURE_SETTINGS.get(name, default))
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_var("SECRET_KEY", 'ymcm-rl%0&!ib1xvxb&tnu53g)(@wm8urwy1%l^z$5*aw#^87q')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_var("DEBUG", False)

ALLOWED_HOSTS = ["*"]

ADMIN_EMAIL = "brandon.bass@mysunbuddy.com"

# use fake is true when not in production
USE_FAKE = get_var("USE_FAKE", False)
USE_FAKE_EMAIL = get_var("USE_FAKE_EMAIL", False)
USE_FAKE_DOMAIN = get_var("USE_FAKE_DOMAIN", False)

# Application definition

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'compressor',
    'rest_framework',
    'django_ses',  # https://github.com/django-ses/django-ses
    'rest_api',
    'django_extensions',
    'raven.contrib.django.raven_compat',
)

# TEST_RUNNER = 'django_specter.runner.DjangoSpecterTestRunner'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'mysunbuddy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rest_api.context_processors.contact_email'
            ],
        },
    },
]

WSGI_APPLICATION = 'mysunbuddy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

if get_var("RDS_HOSTNAME"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.sqlite3',
             'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
         }
    }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_OFFLINE = True

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1

# custom auth user model
AUTH_USER_MODEL = 'rest_api.Account'

# Sentry DSN
SENTRY_DSN = get_var('SENTRY_DSN') # must be before the if use_fake block

# Email settings (Amazon SES)
CONTACT_EMAIL = 'support@mysunbuddy.com'

if USE_FAKE_EMAIL:
    DEFAULT_FROM_EMAIL = "default_email@localhost"
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Documentation: https://github.com/django-ses/django-ses
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_AUTO_THROTTLE = 0.5 # (default; safety factor applied to rate limit)
    AWS_SES_ACCESS_KEY_ID = get_var('AWS_SES_ACCESS_KEY_ID', '')
    AWS_SES_SECRET_ACCESS_KEY = get_var('AWS_SES_SECRET_ACCESS_KEY', '')
    AWS_SES_REGION_NAME = 'us-east-1'
    AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
    AWS_SES_RETURN_PATH = 'no-reply@mysunbuddy.com'
    DEFAULT_FROM_EMAIL = AWS_SES_RETURN_PATH
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }

# EMAIL_BACKEND = get_var("EMAIL_BACKEND", 'django.core.mail.backends.smtp.EmailBackend')
LOGIN_REDIRECT_URL = '/'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_PASSWORD_MIN_LENGTH = 1
ACCOUNT_LOGOUT_ON_GET = True
PASSWORD_RESET_TIMEOUT_DAYS = 3
ACCOUNT_EMAIL_SUBJECT_PREFIX = 'MySunBuddy '

SAFETY_FACTOR = 0.09

# end_date = start_date+6 months
DEAL_END_MONTH = 6

# empty key has limit,please get key in production
GOOGLE_API_KEY = get_var("GOOGLE_API_KEY")
GOOGLE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
GOOGLE_ANALYTICS_TRACKING_ID = get_var("GOOGLE_ANALYTICS_TRACKING_ID")
GOOGLE_ANALYTICS_EXPERIMENT_KEY = get_var("GOOGLE_ANALYTICS_EXPERIMENT_KEY")

if USE_FAKE:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
else:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# django-storages configurations
AWS_S3_SECURE_URLS = True  # use https instead of http
AWS_STORAGE_BUCKET_NAME = get_var('AWS_STORAGE_BUCKET_NAME', '')
AWS_ACCESS_KEY_ID = get_var('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = get_var('AWS_SECRET_ACCESS_KEY', '')
MEDIAFILES_LOCATION = get_var('MEDIAFILES_LOCATION', '')  # Set this to use base folder in bucket
AWS_LOCATION = MEDIAFILES_LOCATION
AWS_DEFAULT_ACL = "private"


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'


REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'rest_api.views.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'login': '5/minute',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}

BROKER_URL = 'django://'
DJKOMBU_POLLING_INTERVAL = 10

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
]

# logging configuration
# https://docs.djangoproject.com/en/dev/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'rest_api': {
            'handlers': ['console'],
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
        'django.request': {
            'handlers': ['console'],
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
    },
}

UTILITY_API_TOKEN = "Token " + get_var("UTILITY_API_TOKEN")
UTILITY_API_URL = 'https://utilityapi.com/api/v2/'
# if USE_FAKE:
#     UTILITY_API_PORTAL = get_var('UTILITY_API_PORTAL', '/utility_mock')
#     UTILITY_API_MODULE = get_var('UTILITY_API_MODULE', 'rest_api.api_wrappers.utility.mock')
# else:
UTILITY_API_PORTAL = get_var('UTILITY_API_PORTAL', 'https://utilityapi.com/portal/mysunbuddy_beta')
UTILITY_API_MODULE = get_var('UTILITY_API_MODULE', 'rest_api.api_wrappers.utility.api')

DOCUSIGN_EMAIL = get_var('DOCUSIGN_EMAIL', 'info@mysunbuddy.com')
DOCUSIGN_PASSWORD = get_var("DOCUSIGN_PASSWORD")
DOCUSIGN_INTEGRATOR_KEY = get_var("DOCUSIGN_INTEGRATOR_KEY")
DOCUSIGN_ROLE_NAME_SELLER = 'Signer'
DOCUSIGN_ROLE_NAME_BUYER = 'Viewer'
DOCUSIGN_TEMPLATE_ID = get_var("DOCUSIGN_TEMPLATE_ID")

if USE_FAKE:
    DOCUSIGN_BASE_URL = "https://demo.docusign.net/restapi"
    DOCUSIGN_USERNAME = 'info@example.com'
else:
    DOCUSIGN_BASE_URL = "https://docusign.com/restapi"
    DOCUSIGN_USERNAME = get_var('DOCUSIGN_USERNAME', 'info@mysunbuddy.com')

#DWOLLA settings
if USE_FAKE:
    DWOLLA_BASE_URL = "https://api-sandbox.dwolla.com"
else:
    DWOLLA_BASE_URL = "https://api.dwolla.com"
DWOLLA_API_KEY = get_var("DWOLLA_API_KEY")
DWOLLA_SECRET_KEY = get_var("DWOLLA_SECRET_KEY")
DWOLLA_WEBHOOK_SECRET = get_var("DWOLLA_WEBHOOK_SECRET")
DWOLLA_SCOPE = "Send|Transactions|Balance|Request|AccountInfoFull|Funding|Scheduled"
# This is the fraction of the buyer's savings that we charge the buyer, leaving them with a 15% savings
CREDIT_DISCOUNT = 0.85
# This is the fraction of the amount charged to the buyer that goes to MySunBuddy; the remaining goes to the seller
COMMISSION = 0.05
MYSUNBUDDY_DWOLLA_ID = "812-800-6692"

BASE_URL = get_var("BASE_URL")

# PVWatts setting configuration
# see http://developer.nrel.gov/docs/solar/pvwatts-v5/
PVWATTS_LOSSES = 10
PVWATTS_ARRAY_TYPE = 0
PVWATTS_TILT = 40
PVWATTS_AZIMUTH = 180
# PVWATTS_SAFETY_FACTOR = 0.1
PVWATTS_UNIT_PRICE = 1
PVWATTS_API_KEY = 'DEMO_KEY'
PVWATTS_API_URL = 'https://developer.nrel.gov/api/pvwatts/v5.json'
UPLOAD_DIR = 'upload'

# recaptcha
GOOGLE_RECAPTCHA_SITE_KEY = get_var('GOOGLE_RECAPTCHA_SITE_KEY')
GOOGLE_RECAPTCHA_SECRET_KEY = get_var('GOOGLE_RECAPTCHA_SECRET_KEY')

TESTING = False

# # Session
# if USE_FAKE_DOMAIN:
#     SESSION_COOKIE_NAME = 'msbTid'
# else:
#     SESSION_COOKIE_DOMAIN = '.mysunbuddy.com'
#     SESSION_COOKIE_NAME = 'msbSid'
