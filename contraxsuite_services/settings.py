# -*- coding: utf-8 -*-
"""
Copyright (C) 2017, ContraxSuite, LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

You can also be released from the requirements of the license by purchasing
a commercial license from ContraxSuite, LLC. Buying such a license is
mandatory as soon as you develop commercial activities involving ContraxSuite
software without disclosing the source code of your own applications.  These
activities include: offering paid services to customers as an ASP or "cloud"
provider, processing documents on the fly in a web application,
or shipping ContraxSuite within a closed source product.

Django settings for contraxsuite_services project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import sys
import environ

from apps.common.advancedcelery.fileaccess.local_file_access import LocalFileAccess
from celery.schedules import crontab

from django.core.urlresolvers import reverse_lazy


ROOT_DIR = environ.Path(__file__) - 2
PROJECT_DIR = ROOT_DIR.path('contraxsuite_services')
APPS_DIR = PROJECT_DIR.path('apps')

DEBUG = False
DEBUG_SQL = False
DEBUG_TEMPLATE = False

# APP CONFIGURATION
# ------------------------------------------------------------------------------
INSTALLED_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'suit',   # Admin
    'django.contrib.admin',

    # THIRD_PARTY_APPS
    'crispy_forms',  # Form layouts
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'simple_history',    # historical records
    'django_celery_results',    # for celery tasks
    'filebrowser',    # browse/upload documents
    'django_extensions',
    'pipeline',    # compressing js, css
    'ckeditor',    # editor
    # Useful template tags:
    'django.contrib.humanize',
    'dal',
    'dal_select2',
    # Configure the django-otp package
    'django_otp',
    'django_otp.plugins.otp_email',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    # Enable two-factor auth
    'allauth_2fa',
    'constance',     # django-constance
    'constance.backends.database',    # django-constance backend
    'corsheaders',     # inject CORS headers into response

    # django-rest
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    'rest_framework_swagger',

    # LOCAL_APPS
    'apps.common',
    'apps.analyze',
    'apps.document',
    'apps.annotator',
    'apps.extract',
    'apps.project',
    'apps.task',
    'apps.users',
    'apps.employee',
    'apps.lease',
)

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # simple history middleware
    'simple_history.middleware.HistoryRequestMiddleware',
    # custom middleware
    'apps.common.middleware.AutoLoginMiddleware',
    'apps.common.middleware.LoginRequiredMiddleware',
    'apps.common.middleware.HttpResponseNotAllowedMiddleware',
    'apps.common.middleware.RequestUserMiddleware',
    'apps.common.middleware.AppEnabledRequiredMiddleware',
    'apps.common.middleware.CookieMiddleware',
    # django-pipeline middleware for minifying data
    'pipeline.middleware.MinifyHTMLMiddleware',
    # Configure the django-otp package. Note this must be after the
    # AuthenticationMiddleware.
    'django_otp.middleware.OTPMiddleware',
    # Reset login flow middleware. If this middleware is included, the login
    # flow is reset if another page is loaded between login and successfully
    # entering two-factor credentials.
    'allauth_2fa.middleware.AllauthTwoFactorMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    PROJECT_DIR('fixtures'),
)

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
SITE_NAME = 'contraxsuite_services'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        # 'DIRS': [
        #     PROJECT_DIR('templates'),
        #     PROJECT_DIR('apps')
        # ],
        # 'APP_DIRS': True,
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'apps.common.loaders.Loader',
                # 'django.template.loaders.app_directories.Loader',
                # ('django.template.loaders.filesystem.Loader', [PROJECT_DIR('templates')])
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'apps.common.context_processors.common'
            ],
        },
    },
]

# email settings
DEFAULT_FROM_EMAIL = '"ContraxSuite" <support@contraxsuite.com>'
DEFAULT_REPLY_TO = '"ContraxSuite" <support@contraxsuite.com>'
SERVER_EMAIL = '"ContraxSuite" <support@contraxsuite.com>'

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = PROJECT_DIR('staticfiles')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    ROOT_DIR('static'),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = PROJECT_DIR('media')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'

# django-pipeline settings
# see: https://django-pipeline.readthedocs.io/en/latest/
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
PIPELINE_ENABLED = True
PIPELINE = {
    'CSS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',
    'STYLESHEETS': {
        'theme_css': {
            'source_filenames': (
                'theme/css/bootstrap.css',
                'theme/css/style.css',
                'theme/css/swiper.css',
                'theme/css/dark.css',
                'theme/css/font-icons.css',
                'theme/css/animate.css',
                'theme/css/magnific-popup.css',
                'theme/css/responsive.css',
            ),
            'output_filename': 'pipeline_theme.css',
        },
        'custom_css': {
            'source_filenames': (
                'css/project.css',
                'vendor/tagsinput/bootstrap-tagsinput.css',
            ),
            'output_filename': 'pipeline_custom.css',
        },
        'custom_jqwidgets_css': {
            'source_filenames': (
                'vendor/jqwidgets/styles/jqx.base.css',
            ),
            'output_filename': 'pipeline_custom_jqwidgets.css',
        },
    },
    'JAVASCRIPT': {
        'custom_js': {
            'source_filenames': (
                'vendor/tagsinput/bootstrap-tagsinput.js',
            ),
            'output_filename': 'pipeline_custom.js',
        },
    }
}

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# allauth settings
# http://django-allauth.readthedocs.io/en/latest/overview.html
ACCOUNT_LOGOUT_REDIRECT_URL = 'account_login'
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_ALLOW_REGISTRATION = True
# ACCOUNT_ADAPTER = 'apps.users.adapters.AccountAdapter'
# Set the allauth adapter to be the 2FA adapter
ACCOUNT_ADAPTER = 'allauth_2fa.adapter.OTPAdapter'
SOCIALACCOUNT_ADAPTER = 'apps.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = reverse_lazy('account_login')

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

# celery
# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_BROKER_URL = 'amqp://contrax1:contrax1@localhost:5672/contrax1_vhost'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXPIRES = 0
# CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_BEAT_SCHEDULE = {
    'celery.backend_cleanup': {
        'task': 'celery.clean_tasks',
        'schedule': crontab(hour=7, minute=30, day_of_week='mon')
    },
}
CELERY_LOG_FILE_NAME = 'celery.log'
CELERY_LOG_FILE_PATH = PROJECT_DIR(CELERY_LOG_FILE_NAME)
# this needed on production. check
CELERY_IMPORTS = ('apps.task.tasks',)
# CELERY_TIMEZONE = 'UTC'

CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['json', 'pickle']

# Redis for Celery args caching
CELERY_CACHE_REDIS_URL = 'redis://127.0.0.1:6379/0'
CELERY_CACHE_REDIS_KEY_PREFIX = 'celery_task'

# django-excel
# http://django-excel.readthedocs.io/en/latest/
FILE_UPLOAD_HANDLERS = (
    "django_excel.ExcelMemoryFileUploadHandler",
    "django_excel.TemporaryExcelFileUploadHandler"
)

# elasticsearch integration
# https://elasticsearch-py.readthedocs.io/en/master/
ELASTICSEARCH_CONFIG = {
    'hosts': [{'host': '127.0.0.1', 'port': 9200}],
    'index': 'contraxsuite'
}

# django-ckeditor
CKEDITOR_CONFIGS = {
    'default': {
        # 'toolbar': 'full',
        'width': '100%',
    },
}

# LoginRequiredMiddleware settings
LOGIN_EXEMPT_URLS = (
    r'^accounts/',    # allow any URL under /accounts/*
    r'^rest-auth/',   # allow any URL under /rest-auth/*
    r'^api/v',        # allow any URL under /api/v*
    r'^__debug__/',   # allow debug toolbar
    r'^extract/search/',
)

# django-filebrowser
# relative path in /media dir
FILEBROWSER_DIRECTORY = 'data/documents/'
# don't try to import a mis-installed PIL
STRICT_PIL = True
# Allowed extensions for file upload
FILEBROWSER_EXTENSIONS = {
    'Image': ['.jpg', '.jpeg', '.png', '.tif', '.tiff'],
    'Document': ['.pdf', '.doc', '.docx', '.rtf', '.txt', '.xls', '.xlsx', '.csv', '.html'],
}
# Max. Upload Size in Bytes
FILEBROWSER_MAX_UPLOAD_SIZE = 10 * 1024 ** 2    # 10Mb
# replace spaces and convert to lowercase
FILEBROWSER_CONVERT_FILENAME = False
# remove non-alphanumeric chars (except for underscores, spaces & dashes)
FILEBROWSER_NORMALIZE_FILENAME = False
# Default sorting, options are: date, filesize, filename_lower, filetype_checked, mimetype
FILEBROWSER_DEFAULT_SORTING_BY = 'filename_lower'
# traverse all subdirectories when searching (this might take a while if many files)
FILEBROWSER_SEARCH_TRAVERSE = True
FILEBROWSER_LIST_PER_PAGE = 25

CELERY_FILE_ACCESS_TYPE = 'Local'
CELERY_FILE_ACCESS_LOCAL_ROOT_DIR = MEDIA_ROOT + '/' + FILEBROWSER_DIRECTORY
#CELERY_FILE_ACCESS_TYPE = 'Nginx'
#CELERY_FILE_ACCESS_NGINX_ROOT_URL = 'http://localhost:8888/media/'

# django-constance settings
# https://django-constance.readthedocs.io/en/latest/
REQUIRED_LOCATORS = (
    'geoentity',
    'party',
    'term',
    'date',
)
OPTIONAL_LOCATORS = (
    'amount',
    'citation',
    'copyright',
    'court',
    'currency',
    'definition',
    'distance',
    'duration',
    'percent',
    'ratio',
    'regulation',
    'trademark',
    'url'
)
LOCATOR_GROUPS = {
    'amount': ('amount', 'currency', 'distance', 'percent', 'ratio'),
    'other': ('citation', 'copyright', 'definition', 'regulation', 'trademark', 'url')
}
OPTIONAL_LOCATOR_CHOICES = [(i, i) for i in OPTIONAL_LOCATORS]
CONSTANCE_ADDITIONAL_FIELDS = {
    'app_multiselect': ['django.forms.fields.MultipleChoiceField', {
        'widget': 'django.forms.SelectMultiple',
        'choices': OPTIONAL_LOCATOR_CHOICES
    }],
}
CONSTANCE_CONFIG = {
    'standard_optional_locators': (OPTIONAL_LOCATORS,
                                   'Standard Optional Locators',
                                   'app_multiselect'),
    'auto_login': (False,
                   'Enable Auto Login',
                   bool),
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

# django-rest-framework settings
# http://www.django-rest-framework.org/
# from rest_framework.authentication import SessionAuthentication
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ('v1', ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'auth.CookieAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}
# tika settings (is not used for now)
# TIKA_VERSION = '1.14'
# TIKA_SERVER_JAR = ROOT_DIR('../libs/tika/tika-server-1.14.jar')
TIKA_DISABLE = False

# use jqWidgets' export, e.g. send data to jq OR handle it on client side
# FYI: http://www.jqwidgets.com/community/topic/jqxgrid-export-data/#}
JQ_EXPORT = True

# place dictionaries for GeoEntities, Terms, US Courts, etc.
DATA_ROOT = PROJECT_DIR('data/')
GIT_DATA_REPO_ROOT = 'https://raw.githubusercontent.com/' \
                     'LexPredict/lexpredict-legal-dictionary/1.0.5'

# logging
LOG_FILE_NAME = 'log.txt'
LOG_FILE_PATH = PROJECT_DIR(LOG_FILE_NAME)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)-7s %(asctime)s | %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'filename': LOG_FILE_PATH,
            'formatter': 'verbose',
        },
        'tasks': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 5,
            'filename': CELERY_LOG_FILE_PATH,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'filters': [],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'apps.task.tasks': {
            'handlers': ['tasks'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# django-extensions notebook
NOTEBOOK_ARGUMENTS = [
    '--ip=0.0.0.0',
    '--port=8000',
]

# django-cors-headers settings
# https://github.com/ottoyiu/django-cors-headers/
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False
CORS_URLS_REGEX = r'^/api/.*$'

VERSION_NUMBER = '1.0.7'
VERSION_COMMIT = '09dd7b8'

try:
    from local_settings import *
    INSTALLED_APPS += LOCAL_INSTALLED_APPS
    MIDDLEWARE += LOCAL_MIDDLEWARE
except (ImportError, NameError):
    pass

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG_TEMPLATE

if DEBUG_SQL:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
        }
    }

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

# settings for AutoLoginMiddleware
# urls available for unauthorized users,
# otherwise login as "test_user"
AUTOLOGIN_ALWAYS_OPEN_URLS = [
    reverse_lazy('account_login'),
]
# forbidden urls for "test user" (all account/* except login/logout)
AUTOLOGIN_TEST_USER_FORBIDDEN_URLS = [
    'accounts/(?!login|logout)',
]

DATA_UPLOAD_MAX_NUMBER_FIELDS = None
PIPELINE['PIPELINE_ENABLED'] = PIPELINE_ENABLED

ANNOTATOR_RETRAIN_MODEL_ON_ANNOTATIONS_CHANGE = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
