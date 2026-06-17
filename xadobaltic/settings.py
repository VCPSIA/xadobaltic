from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-xadobaltic-dev-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'tinymce',
    'core',
    'catalog',
    'selector',
    'accounts',
    'cart',
    'orders',
]

SITE_ID = 1

TINYMCE_DEFAULT_CONFIG = {
    'height': 300,
    'plugins': 'lists link image table code wordcount',
    'toolbar': (
        'undo redo | formatselect | bold italic underline strikethrough | forecolor backcolor | '
        'alignleft aligncenter alignright alignjustify | '
        'bullist numlist | outdent indent | link table | removeformat code'
    ),
    'formatselect_formats': [
        {'title': 'Virsraksts 1', 'block': 'h1'},
        {'title': 'Virsraksts 2', 'block': 'h2'},
        {'title': 'Virsraksts 3', 'block': 'h3'},
        {'title': 'Rindkopa', 'block': 'p'},
    ],
    'font_size_formats': '8pt 10pt 12pt 14pt 16pt 18pt 24pt 36pt',
    'menubar': False,
    'branding': False,
    'content_style': 'body { font-family: Inter, sans-serif; font-size: 14px; }',
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'VERSION': 'v17.0',
    },
}

SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

VAT_RATE = 21  # Latvijas PVN %
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = '/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'xadobaltic.urls'

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
                'django.template.context_processors.i18n',
                'core.context_processors.site_context',
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'xadobaltic.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Valodas
LANGUAGES = [
    ('lv', 'Latviešu'),
    ('ru', 'Русский'),
    ('en', 'English'),
    ('de', 'Deutsch'),
]

LANGUAGE_CODE = 'lv'

LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'Europe/Riga'

USE_I18N = True
USE_L10N = True
USE_TZ = True

MODELTRANSLATION_DEFAULT_LANGUAGE = 'lv'
MODELTRANSLATION_LANGUAGES = ('lv', 'ru', 'en', 'de')

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_URL = 'https://xadobaltic.lv'

# Pārdevēja rekvizīti (norādīt faktiskos datus)
SELLER_INFO = {
    'name': 'SIA Olaintrans',
    'reg_nr': '40203230849',
    'vat_nr': 'LV40203230849',
    'address': 'Elijas iela 5A-18',
    'city': 'Rīga',
    'postal_code': 'LV-1050',
    'country': 'Latvija',
    'bank': 'Citadele banka AS',
    'iban': 'LV98PARX0023297000001',
    'swift': 'PARXLV22',
    'email': 'info@xadobaltic.lv',
    'phone': '+371 20000000',
    'website': 'xadobaltic.lv',
}

# E-pasta iestatījumi
# Ražošanā nomainīt uz SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'info@xadobaltic.lv'
# EMAIL_HOST_PASSWORD = '...'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'XADO Baltic <info@xadobaltic.lv>'
