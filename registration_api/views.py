from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import utils
from serializers import UserSerializer


VALID_USER_FIELDS = utils.get_valid_user_fields()


@api_view(['POST'])
def register(request):
    serialized = UserSerializer(data=request.POST)
    if serialized.is_valid():
        user_data = utils.get_user_data(request.POST)
        user = get_user_model().objects.create_user(
            **user_data
        )
        return Response(UserSerializer(instance=user).data,
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)
