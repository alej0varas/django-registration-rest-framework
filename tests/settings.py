import os


DIRNAME = os.path.dirname(__file__)
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': os.path.join(DIRNAME, 'database.db'),
                         },
             }
DEBUG = True
DATABASES = DATABASES
INSTALLED_APPS = ('django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.admin',
                  'django.contrib.sites',
                  'registration_api',
                  # 'custom_user',
                  )
# AUTH_USER_MODEL = 'custom_user.EmailUser'
ROOT_URLCONF = 'registration_api.urls'

SECRET_KEY = 'not-secret'
SITE_ID = 1

REGISTRATION_API_ACTIVATION_SUCCESS_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    )
}
