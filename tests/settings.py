import os

DIRNAME = os.path.dirname(__file__)
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': os.path.join(DIRNAME, 'database.db'),
                         },
             }
CACHES = {'default': {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

DEBUG = True
DATABASES = DATABASES
INSTALLED_APPS = ('django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.admin',
                  'registration_api',
                  )
ROOT_URLCONF = 'registration_api.urls'
CACHES = CACHES
AUTH_USER_MODEL = 'auth.User'
SECRET_KEY = 'adfs'
