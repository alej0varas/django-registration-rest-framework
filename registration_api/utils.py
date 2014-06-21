import hashlib
import random
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string

from .models import RegistrationProfile

from django.db import transaction
# django 1.6, 1.5 and 1.4 supports
try:
    atomic_decorator = transaction.atomic
except AttributeError:
    atomic_decorator = transaction.commit_on_success


SHA1_RE = re.compile('^[a-f0-9]{40}$')
DEFAULT_SETTINGS = {
    'REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS': 7,
}


def get_settings(key):
    setting = getattr(settings, key, DEFAULT_SETTINGS.get(key, None))
    if setting is None:
        raise ImproperlyConfigured("The %s setting must not be empty." % key)
    return setting


USER_CREATED_RESPONSE_DATA = {
    'activation_days': get_settings('REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS')
    }


def get_valid_user_fields():
    fields = []
    for f in get_user_model()._meta.fields:
        fields.append(f.name)
    return fields


VALID_USER_FIELDS = get_valid_user_fields()


def get_user_data(data):
    user_data = {}
    for field, data in data.items():
        if field in VALID_USER_FIELDS:
            user_data.update({field: data})
    return user_data


@atomic_decorator
def create_inactive_user(username=None, email=None, password=None):
    user_model = get_user_model()
    if username is not None:
        new_user = user_model.objects.create_user(username, email, password)
    else:
        new_user = user_model.objects.create_user(email=email, password=password)
    new_user.is_active = False
    new_user.save()
    create_profile(new_user)
    site = Site.objects.get_current()
    send_activation_email(new_user, site)
    return new_user


def create_profile(user):
    activation_key = create_activation_key(user)
    registration_profile = RegistrationProfile.objects.create(
        user=user, activation_key=activation_key)
    return registration_profile


def create_activation_key(user):
    username = getattr(user, user.USERNAME_FIELD)
    salt_bytes = str(random.random()).encode('utf-8')
    salt = hashlib.sha1(salt_bytes).hexdigest()[:5]

    hash_input = (salt + username).encode('utf-8')
    activation_key = hashlib.sha1(hash_input).hexdigest()
    return activation_key


def activate_user(activation_key):
    """
    Validate an activation key and activate the corresponding
    ``User`` if valid.
    If the key is valid and has not expired, return the ``User``
    after activating.
    If the key is not valid or has expired, return ``False``.
    If the key is valid but the ``User`` is already active,
    return ``False``.
    To prevent reactivation of an account which has been
    deactivated by site administrators, the activation key is
    reset to the string constant ``RegistrationProfile.ACTIVATED``
    after successful activation.

    """
    # Make sure the key we're trying conforms to the pattern of a
    # SHA1 hash; if it doesn't, no point trying to look it up in
    # the database.
    if SHA1_RE.search(activation_key):
        try:
            profile = RegistrationProfile.objects.get(
                activation_key=activation_key)
        except RegistrationProfile.DoesNotExist:
            return False
        if not profile.activation_key_expired():
            user = profile.user
            user.is_active = True
            user.save()
            profile.activation_key = RegistrationProfile.ACTIVATED
            profile.save()
            return user
    return False


def send_activation_email(user, site):
    """
    Send an activation email to the ``user``.
    The activation email will make use of two templates:

    ``registration/activation_email_subject.txt``
    This template will be used for the subject line of the
    email. Because it is used as the subject line of an email,
    this template's output **must** be only a single line of
    text; output longer than one line will be forcibly joined
    into only a single line.

    ``registration/activation_email.txt``
    This template will be used for the body of the email.

    These templates will each receive the following context
    variables:

    ``activation_key``
    The activation key for the new account.

    ``expiration_days``
    The number of days remaining during which the account may
    be activated.

    ``site``
    An object representing the site on which the user
    registered; depending on whether ``django.contrib.sites``
    is installed, this may be an instance of either
    ``django.contrib.sites.models.Site`` (if the sites
    application is installed) or
    ``django.contrib.sites.models.RequestSite`` (if
    not). Consult the documentation for the Django sites
    framework for details regarding these objects' interfaces.

    """
    ctx_dict = {'activation_key': user.api_registration_profile.activation_key,
                'expiration_days': get_settings('REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS'),
                'site': site}
    subject = render_to_string('registration_api/activation_email_subject.txt',
                               ctx_dict)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    message = render_to_string('registration_api/activation_email.txt',
                               ctx_dict)
    user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
