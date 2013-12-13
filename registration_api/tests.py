from urllib import urlencode
import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase
from django.utils.datastructures import MergeDict

from rest_framework import status
from rest_framework.response import Response

# from mock_django.http import MockHttpRequest

from registration_api.serializers import UserSerializer
from registration_api.views import register
import utils


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


# Based on django.contrib.auth.models.User
EXPECTED_VALID_USER_FIELDS = [u'id', 'username', 'first_name', 'last_name',
                              'password', 'last_login', 'is_superuser',
                              'email', 'is_staff', 'is_active', 'date_joined']

VALID_DATA = {'username': 'john', 'email': 'john@example.com',
              'password': 'verylongpassword'}


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


class UserSerializerTests(TestCase):

    def test_model(self):
        self.assertEqual(UserSerializer.Meta.model, get_user_model())


class RegisterAPIViewTests(TestCase):

    @mock.patch('registration_api.utils.get_user_data')
    @mock.patch('registration_api.views.get_user_model')
    @mock.patch('registration_api.views.UserSerializer')
    @mock.patch('registration_api.views.Response')
    def test_valid_registration(self, mock_Response, mock_UserSerializer, mock_get_user_model, mock_get_user_data):
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
        mock_get_user_model.return_value = mock_user_model
        mock_get_user_model.objects = mock_objects
        mock_get_user_data.return_value = VALID_DATA

        request = MockHttpRequest(POST=VALID_DATA)

        register(request)

        mock_UserSerializer.assert_called_with(instance=created_user)
        mock_Response.assert_called_with(
            VALID_DATA,
            status=status.HTTP_201_CREATED)
        mock_get_user_model.assert_called_with()
        mock_create_user.assert_called_with(**VALID_DATA)

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

    def test_functional_invalid(self):
        url = reverse('registration_api_register')

        response = self.client.post(url, INVALID_DATA)

        self.assertEqual(400, response.status_code)
        self.assertFalse(get_user_model().objects.filter())
