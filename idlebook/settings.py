# Django settings for idlebook project.
import os
import django.conf.global_settings as DEFAULT_SETTINGS
import config_reader

config = config_reader.get_config('settings.py')

DEBUG = config['debug']
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    (config['admin_name'], config['admin_email']),
)

MANAGERS = ADMINS

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

SITE_URL = config['site_url']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': config['databases_name'],                      # Or path to database file if using sqlite3.
        'USER': config['databases_user'],                      # Not used with sqlite3.
        'PASSWORD': config['databases_password'],                  # Not used with sqlite3.
        'HOST': config['databases_host'],                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': config['databases_port'],                      # Set to empty string for default. Not used with sqlite3.
    }
}

# from email
DEFAULT_FROM_EMAIL = config['default_from_email']

# email confirmation expire time in days
EMAIL_CONFIRMATION_DAYS = config['email_confirmation_days']

# Third party API
FACEBOOK_APP_ID = '206779069338929'
FACEBOOK_API_KEY = '288c004c1f3bfe7d9bfe8fcad972f806'
FACEBOOK_SECRET_KEY = '6e2f45970c5caf7a69c32354c0c812ba'

# perms set at common.js
#FACEBOOK_PERMS = ['user_education_history', 'publish_stream']

# And for local debugging, use one of the debug middlewares and set:
FACEBOOK_DEBUG_TOKEN = ''
FACEBOOK_DEBUG_UID = ''
FACEBOOK_DEBUG_COOKIE = ''
FACEBOOK_DEBUG_SIGNEDREQ = ''

# Amazon API
AMAZON_AWS_KEY = 'AKIAI6M6RNJTOTRN7M4Q'
AMAZON_SECRET_KEY = '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'
AMAZON_COUNTRY_CODE = 'us'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = config['time_zone']

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = config['language_code']

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = config['media_root']

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '%s/media/' % SITE_URL

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '%s/static/' % PROJECT_ROOT

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '%s/static/' % SITE_URL

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    STATIC_ROOT,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'wnfw9enmrd2!+y=-x_51r7$2f04sb5uv)^$&0x(#+at0wgw#7a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
#    'django.middleware.cache.UpdateCacheMiddleware', # must be first in list
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'idlebook.facebook.middleware.FacebookMiddleware',
    
#    'django.middleware.cache.FetchFromCacheMiddleware', # must be last in the list
)

ROOT_URLCONF = 'idlebook.urls'

TEMPLATE_DIRS = (
    '%s/templates' % PROJECT_ROOT,
    '%s/account/templates' % PROJECT_ROOT,
    '%s/book/templates' % PROJECT_ROOT,
    '%s/accounting/templates' % PROJECT_ROOT,
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    "django.core.context_processors.request",
    "idlebook.account.context_processors.unread_requests",
    "idlebook.account.context_processors.unread_requests_received",
    "idlebook.account.context_processors.unread_requests_sent",
    "idlebook.account.context_processors.total_book_count",
#    "idlebook.account.context_processors.timestamp",
    "idlebook.account.context_processors.unread_wallet",
)

AUTH_PROFILE_MODULE = 'account.UserProfile'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL ='/'

AUTHENTICATION_BACKENDS = (
    'idlebook.account.backends.EmailModelBackend',
    'idlebook.facebook.auth.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.admin',
#    'django.contrib.admindocs',
    'notification',
    'django.contrib.humanize',
    'idlebook.account',
    'idlebook.network',
    'idlebook.book',
    'idlebook.accounting',
    'idlebook.facebook',
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': config['django_log'],
            'maxBytes': 1024 * 1024 * 5, # 5 MB
            'backupCount': 5,
            'formatter':'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django': {
            'handlers':['file'],
            'level':'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Using python-memcache, memcached for server catching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': config['caches_location'],
    }
}

# Applications specific settings
# days a trade expires
TRADE_EXPIRATION_DAYS = 3
# Due remind in following many days
DUE_REMIND_DAYS = 3
# security deposit in cents
DEPOSIT_MIN_LIMIT = 3000
DEPOSIT_MIN_LIMIT_PERCENT = 0.66
DEPOSIT_LIST_PRICE_PERCENT = 0.2
DEPOSIT_LIST_PRICE_MIN_LIMIT = 5000
# number of amazon results
AMAZON_QUERY_COUNT = 1
