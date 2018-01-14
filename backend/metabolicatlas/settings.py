"""
Django settings for metabolicatlas project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*iu%ha&)j07dsx#vq8f*6=o-l3y&4_+9p-itoa5b(5z!5hq5rq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    'icsb.chalmers.se',
    # '192.168.99.100', 'http://localhost', 'http://192.168.99.100'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    'api',
    'corsheaders',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'metabolicatlas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'metabolicatlas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
'''default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'hma',
    'USER': os.getenv('POSTGRES_USER'),
    'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'HOST': 'db',
    'PORT': 5432,
},'''

DATABASES = {
    'default': {
    },
    'human': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hma2',
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    },
    'yeast': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ymh',
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    },
    'gems': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB2_GEMS_DB'),
        'USER': os.getenv('POSTGRES_DB2_USER'),
        'PASSWORD': os.getenv('POSTGRES_DB2_PASSWORD'),
        'HOST': 'db2',
        'PORT': 5432,
    },
    'tiles': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB2_TILES_DB'),
        'USER': os.getenv('POSTGRES_DB2_USER'),
        'PASSWORD': os.getenv('POSTGRES_DB2_PASSWORD'),
        'HOST': 'db2',
        'PORT': 5432,
    }
}


# Database routers

DATABASE_ROUTERS = [
    'api.routers.GemodelRouter',
    'api.routers.TileRouter',
    'api.routers.ApiRouter'
]


# CORS
# https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_WHITELIST = (
    'localhost',
    'icsb.chalmers.se',
    # '192.168.99.100:8080',
    # 'localhost:8080',
)


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# SWAGGER
SWAGGER_SETTINGS = {
    'LOGIN_URL': 'admin:login',
    'LOGOUT_URL': 'admin:logout',
    "exclude_namespaces": ["internal_apis"],
}


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True




STATIC_URL = '/static/'
STATIC_ROOT = './static/'
