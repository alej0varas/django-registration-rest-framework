import datetime

from django.conf import settings
from django.db import models
from django.utils.timezone import now as datetime_now
from django.utils.translation import ugettext_lazy as _


class RegistrationProfile(models.Model):
    """
    A simple profile which stores an activation key for use during
    user account registration.

    """
    ACTIVATED = u"ALREADY_ACTIVATED"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, verbose_name=_('user'), related_name='api_registration_profile')
    activation_key = models.CharField(_('activation key'), max_length=40)

    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        Key expiration is determined by a two-step process:
        1. If the user has already activated, the key will have been
        reset to the string constant ``ACTIVATED``. Re-activating
        is not permitted, and so this method returns ``True`` in
        this case.

        2. Otherwise, the date the user signed up is incremented by
        the number of days specified in the setting
        ``REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS`` (which should be
        the number of days after signup during which a user is allowed
        to activate their account); if the result is less than or
        equal to the current date, the key has expired and this method
        returns ``True``.

        """

        # utils imported here to avoid circular import
        import utils

        expiration_date = datetime.timedelta(
            days=utils.get_settings('REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS'))
        return self.activation_key == self.ACTIVATED or \
            (self.user.date_joined + expiration_date <= datetime_now())
