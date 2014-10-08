from urllib import urlencode
import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.datastructures import MergeDict

from rest_framework import status
from rest_framework.response import Response

from registration_api import utils
from registration_api.models import RegistrationProfile
from registration_api.serializers import UserSerializer
from registration_api.views import activate, register


class WsgiHttpRequest(HttpRequest):
    def __init__(self, *args, **kwargs):
        super(WsgiHttpRequest, self).__init__(*args, **kwargs)
        self.user = AnonymousUser()
        self.session = {}
        self.META = {}
        self.GET = {}
        self.POST = {}

    def _get_request(self):
        if not hasattr(self, '_request'):
            self._request = MergeDict(self.POST, self.GET)
        return self._request
    REQUEST = property(_get_request)

    def _get_raw_post_data(self):
        if not hasattr(self, '_raw_post_data'):
            self._raw_post_data = urlencode(self.POST)
        return self._raw_post_data

    def _set_raw_post_data(self, data):
        self._raw_post_data = data
        self.POST = {}
    raw_post_data = property(_get_raw_post_data, _set_raw_post_data)


def MockHttpRequest(path='/', method='GET', GET=None, POST=None, META=None, user=None):
    if GET is None:
        GET = {}
    if POST is None:
        POST = {}
    else:
        method = 'POST'
    if META is None:
        META = {
            'REMOTE_ADDR': '127.0.0.1',
            'SERVER_PORT': '8000',
            'HTTP_REFERER': '',
            'SERVER_NAME': 'testserver',
        }
    if user is not None:
        user = user

    request = WsgiHttpRequest()
    request.path = request.path_info = path
    request.method = method
    request.META = META
    request.GET = GET
    request.POST = POST
    request.user = user
    return request


EXPECTED_VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
POST_DATA = {'username': 'john', 'email': 'john@example.com',
             'password': 'verylongpassword'}
VALID_DATA = dict(
    [(k, v) for k, v in POST_DATA.items()
     if k in EXPECTED_VALID_USER_FIELDS])
INVALID_DATA = VALID_DATA.copy()
INVALID_DATA.pop('password')


class UtilsTests(TestCase):

    def test_VALID_USER_FIELDS(self):

        self.assertListEqual(sorted(utils.VALID_USER_FIELDS),
                             sorted(EXPECTED_VALID_USER_FIELDS))

    def test_get_user_data(self):
        valid_data = {'id': 1}
        mock_data = valid_data.copy()
        mock_data.update({'invalid_field': 0})

        data = utils.get_user_data(mock_data)

        self.assertEqual(valid_data, data)

    @mock.patch('registration_api.utils.send_activation_email')
    @mock.patch('registration_api.utils.create_profile')
    def test_create_inactive_user(self, mock_create_profile, mock_send_activation_email):
        site = Site.objects.get()
        user_model = get_user_model()
        with mock.patch.object(user_model.objects, 'create_user') as mock_create_user:
            mock_create_user.return_value = get_user_model()(**VALID_DATA)
            user = utils.create_inactive_user(**VALID_DATA)

            if hasattr(user, 'username'):
                mock_create_user.assert_called_with(VALID_DATA['username'],
                                                    VALID_DATA['email'],
                                                    VALID_DATA['password'])
            else:
                mock_create_user.assert_called_with(VALID_DATA['email'],
                                                    VALID_DATA['password'])
            mock_create_profile.assert_called_with(user)
            self.assertFalse(user.is_active)
            self.assertTrue(user.pk)
            mock_send_activation_email.assert_called_with(user, site)

    @mock.patch('registration_api.utils.create_activation_key')
    @mock.patch('registration_api.models.RegistrationProfile.objects.create')
    def test_create_profile(self, mock_create, mock_create_activation_key):
        mock_create.return_value = RegistrationProfile()
        activation_key = 'activationkey'
        mock_create_activation_key.return_value = activation_key
        user = get_user_model()(**VALID_DATA)

        registration_profile = utils.create_profile(user)

        self.assertIsInstance(registration_profile, RegistrationProfile)
        mock_create_activation_key.assert_called_with(user)
        mock_create.assert_called_with(user=user,
                                       activation_key=activation_key)

    def test_create_activation_key(self):
        user = get_user_model().objects.create(**VALID_DATA)

        activation_key = utils.create_activation_key(user)

        self.assertTrue(activation_key)
        self.assertEqual(len(activation_key), 40)

    def test_activate_user(self):
        user = utils.create_inactive_user(**VALID_DATA)

        user = utils.activate_user(user.api_registration_profile.activation_key)

        self.assertTrue(user.is_active)

    def test_send_activations_email(self):
        user = get_user_model().objects.create(**VALID_DATA)
        RegistrationProfile.objects.create(user=user, activation_key='asdf')
        site = Site.objects.get()
        subject = ''
        message = ''

        with mock.patch.object(user, 'email_user') as mock_email_user:
            utils.send_activation_email(user, site)

            mock_email_user.assert_called_with(
                subject, message, settings.DEFAULT_FROM_EMAIL)

    def test_get_settings(self):
        value = utils.get_settings('REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS')

        self.assertEqual(
            value,
            utils.DEFAULT_SETTINGS['REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS'])

    @override_settings(REGISTRATION_API_ACTIVATION_SUCCESS_URL=None)
    def test_get_settings_ImproperlyConfigured(self):
        self.assertRaises(ImproperlyConfigured, utils.get_settings,
                          'REGISTRATION_API_ACTIVATION_SUCCESS_URL')


class UserSerializerTests(TestCase):

    def test_model(self):
        self.assertEqual(UserSerializer.Meta.model, get_user_model())


class RegisterAPIViewTests(TestCase):

    @mock.patch('registration_api.utils.get_user_data')
    @mock.patch('registration_api.utils.create_inactive_user')
    @mock.patch('registration_api.views.UserSerializer')
    @mock.patch('registration_api.views.Response')
    def test_valid_registration(self, mock_Response, mock_UserSerializer, mock_create_incative_user, mock_get_user_data):
        created_user = 'user'
        mock_Response.return_value = Response()
        mock_userserializer_instance = mock.Mock()
        mock_userserializer_instance.data = VALID_DATA
        mock_UserSerializer.return_value = mock_userserializer_instance
        mock_userserializer_instance.is_valid.return_value = True
        mock_create_user = mock.Mock()
        mock_create_user.return_value = created_user
        mock_objects = mock.Mock()
        mock_objects.create_user = mock_create_user
        mock_user_model = mock.Mock()
        mock_user_model.objects = mock_objects
        mock_get_user_data.return_value = VALID_DATA

        request = MockHttpRequest(POST=VALID_DATA)

        register(request)

        mock_UserSerializer.assert_called_with(data=VALID_DATA)
        mock_Response.assert_called_with(
            utils.USER_CREATED_RESPONSE_DATA,
            status=status.HTTP_201_CREATED)
        mock_create_incative_user.assert_called_with(**VALID_DATA)

    @mock.patch('registration_api.views.UserSerializer')
    @mock.patch('registration_api.views.Response')
    def test_invalid_registration(self, mock_Response, mock_UserSerializer):
        mock_Response.return_value = Response()
        mock_userserializer_instance = mock.Mock()
        mock_UserSerializer.return_value = mock_userserializer_instance
        mock_userserializer_instance.is_valid.return_value = False
        mock_userserializer_instance._errors = {}

        request = MockHttpRequest(POST=VALID_DATA)

        register(request)

        mock_UserSerializer.assert_called_with(data=VALID_DATA)
        mock_Response.assert_called_with(
            mock_userserializer_instance._errors,
            status=status.HTTP_400_BAD_REQUEST)

    def test_functional(self):
        url = reverse('registration_api_register')

        response = self.client.post(url, VALID_DATA)

        self.assertEqual(201, response.status_code)
        self.assertTrue(get_user_model().objects.get())
        self.assertFalse(get_user_model().objects.get().is_active)
        self.assertTrue(RegistrationProfile.objects.get())

    def test_functional_invalid(self):
        url = reverse('registration_api_register')

        response = self.client.post(url, INVALID_DATA)

        self.assertEqual(400, response.status_code)
        self.assertFalse(get_user_model().objects.filter())


class ActivateViewTests(TestCase):

    def test_activate(self):
        user = utils.create_inactive_user(**VALID_DATA)
        request = MockHttpRequest()

        response = activate(
            request,
            activation_key=user.api_registration_profile.activation_key)
        user = get_user_model().objects.get(pk=user.pk)

        self.assertTrue(user.is_active)
        self.assertEqual(user.api_registration_profile.activation_key,
                         RegistrationProfile.ACTIVATED)
        self.assertEqual(response.status_code,
                         status.HTTP_302_FOUND)
        self.assertEqual(response['location'],
                         utils.get_settings('REGISTRATION_API_ACTIVATION_SUCCESS_URL'))

    @override_settings(REGISTRATION_API_ACTIVATION_SUCCESS_URL=None)
    def test_activate__without_ACTIVATE_REDIRECT_URL(self):
        user = utils.create_inactive_user(**VALID_DATA)
        request = MockHttpRequest()

        self.assertRaises(
            ImproperlyConfigured,
            activate,
            request,
            activation_key=user.api_registration_profile.activation_key)
