from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

import utils
from serializers import UserSerializer


VALID_USER_FIELDS = utils.get_valid_user_fields()


@api_view(['POST'])
@permission_classes((AllowAny, ))
def register(request):
    serialized = {}
    user_data = {}
    if request.META['CONTENT_TYPE'] == 'application/json':
        serialized = UserSerializer(data=request.DATA)
        if serialized.is_valid():
            user_data = request.DATA
    elif request.META['CONTENT_TYPE'] == 'application/x-www-form-urlencoded':
        serialized = UserSerializer(data=request.POST)
        if serialized.is_valid():
            user_data = utils.get_user_data(request.POST)
    if serialized.is_valid():
        utils.create_inactive_user(**user_data)
        return Response(utils.USER_CREATED_RESPONSE_DATA,
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


def activate(request, activation_key=None):
    """
    Given an an activation key, look up and activate the user
    account corresponding to that key (if possible).

    """
    utils.activate_user(activation_key)
    # if not activated
    success_url = utils.get_settings('REGISTRATION_API_ACTIVATION_SUCCESS_URL')
    if success_url is not None:
        return HttpResponseRedirect(success_url)
